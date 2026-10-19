"""Check handoff records with Python's standard library; no model or network use."""
import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
AREA = 'ascend_tuning/integration/'
SHA = re.compile(r'[0-9a-f]{64}\Z')
COMMIT = re.compile(r'[0-9a-f]{40}\Z')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def path(name):
    require(isinstance(name, str) and bool(name), 'Empty/non-string path')
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
            f'Unsafe path: {name}')
    target = ROOT.joinpath(*p.parts)
    require(ROOT in target.resolve().parents, f'Path escapes repository: {name}')
    require(not any(q.is_symlink() for q in (target, *target.parents)
                    if q != ROOT and ROOT in q.parents), f'Symlink: {name}')
    require(target.is_file(), f'Missing file: {name}')
    return target


def digest(name):
    return hashlib.sha256(path(name).read_bytes()).hexdigest()


def read(name):
    return json.loads(path(name).read_text())


def array(obj, name):
    require(isinstance(obj.get(name), list), f'{obj.get("id", "record")}: {name} must be an array')
    return obj[name]


def optional_commit(value, label):
    require(value is None or isinstance(value, str) and COMMIT.fullmatch(value),
            f'{label}: use exact 40-character commit or null')


def check_run(name, rules, ids, gates):
    require(name.startswith(AREA + 'runs/') and name.endswith('.json'),
            f'Validation evidence must be a real runs/*.json record: {name}')
    r = read(name)
    require(set(rules['run_required_fields']) <= set(r), f'{name}: missing run fields')
    require(r['schema_version'] == 1 and r['example'] is False, f'{name}: example is not evidence')
    require(r['verdict'] in rules['run_verdicts'], f'{name}: invalid verdict')
    require(bool(r['run_id']), f'{name}: missing run_id')
    require(bool(array(r, 'item_ids')) and set(r['item_ids']) <= set(ids), f'{name}: unknown item IDs')
    optional_commit(r['candidate_commit'], name)
    manifest = r['candidate_source_manifest']
    if manifest is not None:
        require(isinstance(manifest, dict) and set(manifest) >= {'path', 'sha256'}, f'{name}: bad source manifest')
        require(isinstance(manifest['sha256'], str) and SHA.fullmatch(manifest['sha256']), f'{name}: bad manifest SHA')
        require(digest(manifest['path']) == manifest['sha256'], f'{name}: source manifest hash mismatch')
    for check in array(r, 'checks'):
        require(check.get('gate_id') in gates, f'{name}: unknown check gate')
        require(check.get('result') in rules['check_results'] and bool(check.get('scope')), f'{name}: incomplete check')
    for artifact in array(r, 'artifacts'):
        require(isinstance(artifact.get('sha256'), str) and SHA.fullmatch(artifact['sha256']), f'{name}: artifact SHA required')
        require(bool(artifact.get('path') or artifact.get('uri')), f'{name}: missing artifact locator')
        if artifact.get('path'):
            require(digest(artifact['path']) == artifact['sha256'], f'{name}: artifact hash mismatch')
    array(r, 'failures')
    array(r, 'limitations')
    if r['verdict'] == 'passed':
        require(r['candidate_commit'] is not None or manifest is not None, f'{name}: passed without source identity')
        require(bool(r['executed_at']) and bool(r['hardware']) and bool(r['runtime']) and bool(r['model']),
                f'{name}: passed without execution identity')
        require(datetime.fromisoformat(r['executed_at'].replace('Z', '+00:00')).tzinfo is not None,
                f'{name}: execution time needs timezone')
        require(bool(r['checks']) and bool(r['artifacts']), f'{name}: passed without checks/artifacts')
    return r


def review_paths():
    names = {'AGENTS.md', 'CONTRIBUTING_ASCEND.md', 'CODE_STATUS.md', 'UPSTREAM_UPDATES.md',
             'ascend_tuning/tools/check_registry.py', '.github/workflows/ascend-registry.yml'}
    names |= {p.relative_to(ROOT).as_posix() for p in (ROOT / AREA).rglob('*')
              if p.is_file() and p.name != 'REVIEW_MANIFEST.json'}
    return names


def refresh_manifest():
    manifest = {'schema_version': 2,
                'source_collection_commit': read(AREA + 'items.json')['source_collection_commit'],
                'scope': 'Maintenance records and checker; original source archive manifest remains separate.',
                'original_package_manifest_sha256': digest('ascend_tuning/PACKAGE_MANIFEST.json'),
                'files': {name: {'sha256': digest(name), 'bytes': path(name).stat().st_size}
                          for name in sorted(review_paths())}, 'self_excluded': True}
    (ROOT / AREA / 'REVIEW_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def verify(base_ref=None):
    rules = read(AREA + 'REGISTRY_RULES.json')
    ledger = read(AREA + 'items.json')
    inventory = read(AREA + 'file-classification.json')
    plan = read(AREA + 'verification-plan.json')
    require(ledger['schema_version'] == rules['registry_schema_version'], 'Registry schema mismatch')
    ids = {item['id']: item for item in ledger['items']}
    require(len(ids) == len(ledger['items']), 'Duplicate item ID')
    gates = {g['id'] for g in plan['gates']}
    require(len(gates) == len(plan['gates']), 'Duplicate verification gate')
    visits, runs = set(), {}

    def visit(uid, stack=()):
        require(uid not in stack, f'Dependency cycle: {stack + (uid,)}')
        if uid in visits:
            return
        for dep in ids[uid]['integration_after']:
            require(dep in ids, f'{uid}: unknown dependency {dep}')
            visit(dep, stack + (uid,))
        visits.add(uid)

    for uid, item in ids.items():
        require(set(rules['item_required_fields']) <= set(item), f'{uid}: missing item fields')
        require(re.fullmatch(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*', uid), f'Invalid item ID: {uid}')
        require(bool(item['title']) and bool(item['summary']) and bool(item['model']), f'{uid}: empty description')
        for field, enum in [('category', 'categories'), ('source_presence', 'source_presence'),
                            ('validation_state', 'validation_states'), ('integration_state', 'integration_states'),
                            ('merge_policy', 'merge_policies')]:
            require(item[field] in rules[enum], f'{uid}: invalid {field}')
        for field in rules['path_arrays']:
            if field in item:
                for name in array(item, field):
                    path(name)
        array(item, 'notes')
        require(set(array(item, 'required_validation')) <= gates, f'{uid}: unknown required gate')
        if item['category'] != 'reference':
            require('SOURCE' in item['required_validation'], f'{uid}: SOURCE check required')
        if item['category'] == 'reference':
            require(item['merge_policy'] == 'reference_only', f'{uid}: reference merge policy required')
        array(item, 'integration_after')
        visit(uid)
        require(isinstance(item['scope'], dict) and set(item['scope']) >= {'base_source_commit', 'hardware', 'profiles', 'limitations'}, f'{uid}: incomplete scope')
        optional_commit(item['scope']['base_source_commit'], uid)
        require(isinstance(item['scope']['profiles'], list), f'{uid}: profiles must be an array')
        require(isinstance(item['rollback'], dict) and set(item['rollback']) >= {'commit', 'profile', 'notes'}, f'{uid}: incomplete rollback')
        optional_commit(item['rollback']['commit'], uid)
        up = item['upstream']
        require(isinstance(up, dict) and up.get('status') in rules['upstream_statuses'], f'{uid}: invalid upstream record')
        optional_commit(up.get('target_commit'), uid)
        for name in up.get('evidence_refs', []):
            path(name)
        if item['source_presence'] in {'in_collection', 'partially_in_collection', 'tooling'}:
            require(bool(item['source_paths']), f'{uid}: claimed source missing')
        if item['validation_state'] in {'component_pass', 'historical_scoped_pass'}:
            require(bool(item['evidence_refs'] or item['validation_runs']), f'{uid}: claimed pass without evidence')
        for name in item['validation_runs']:
            if name not in runs:
                runs[name] = check_run(name, rules, ids, gates)
            require(uid in runs[name]['item_ids'], f'{uid}: unrelated run {name}')
        if item['validation_state'] == 'candidate_pass':
            grouped = defaultdict(set)
            for name in item['validation_runs']:
                r = runs[name]
                if r['verdict'] == 'passed':
                    identity = json.dumps([r['candidate_commit'], r['candidate_source_manifest'],
                                           r['model'], r['configuration'], r['runtime'], r['hardware']], sort_keys=True)
                    grouped[identity] |= {c['gate_id'] for c in r['checks'] if c['result'] == 'passed'}
            require(any(set(item['required_validation']) <= passed for passed in grouped.values()),
                    f'{uid}: candidate_pass lacks same-source required checks')
            if item['category'] not in {'reference', 'tooling'}:
                require(any(g.endswith('FUNCTIONAL') for g in item['required_validation']),
                        f'{uid}: runtime candidate needs functional qualification')
        if item['integration_state'] in {'verified', 'released'}:
            require(item['validation_state'] == 'candidate_pass', f'{uid}: verified/released without candidate_pass')
        if item['integration_state'] == 'released':
            require(item['merge_policy'] not in {'experimental_only', 'reference_only', 'hold_integration'},
                    f'{uid}: held/experimental/reference released')

    recorded = {r['path']: r for r in inventory['files']}
    require(len(recorded) == len(inventory['files']), 'Duplicate inventory path')
    require(inventory['code_files'] == len(recorded), 'Inventory count mismatch')
    for name, row in recorded.items():
        require(row['primary_item'] in ids and row['role'] in rules['inventory_roles'], f'{name}: invalid owner/role')
        require(name in ids[row['primary_item']]['source_paths'], f'{name}: owner does not declare source')
        require(digest(name) == row['sha256'], f'{name}: source SHA mismatch')
    for item in ids.values():
        require(set(item['source_paths']) <= set(recorded), f'{item["id"]}: source not inventoried')
    retired = set(inventory.get('retired_paths', []))
    require(not retired & set(recorded), 'Retired path remains active')
    if base_ref:
        q = subprocess.run(['git', 'rev-parse', '--verify', base_ref + '^{commit}'], cwd=ROOT, check=True, capture_output=True, text=True)
        ref = q.stdout.strip()
        q = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=ACMRT', ref, '--'], cwd=ROOT, check=True, capture_output=True, text=True)
        changed = set(q.stdout.splitlines())
        q = subprocess.run(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, check=True, capture_output=True, text=True)
        changed |= set(q.stdout.splitlines())
        for name in changed:
            if name.startswith(('python/sglang/', 'sgl-kernel/', 'ascend_tuning/')) and name.endswith(('.py', '.c', '.cpp', '.cc', '.h', '.cu', '.cuh')):
                require(name in recorded, f'Changed source has no item/inventory record: {name}')

    manifest = read(AREA + 'REVIEW_MANIFEST.json')
    require(manifest['original_package_manifest_sha256'] == digest('ascend_tuning/PACKAGE_MANIFEST.json'), 'Original archive manifest changed')
    require(set(manifest['files']) == review_paths(), 'Maintenance manifest file coverage stale')
    private_address = re.compile(r'(?<![\d.])(?:10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})(?![\d.])')
    personal_path = re.compile('/' + 'Users' + r'/[^/\s]+/')
    credential = re.compile(r"(?i)(?:password|api[_-]?key|access_token|secret_key)\s*[:=]\s*['\"][^'\"\n]{8,}['\"]")
    for name, record in manifest['files'].items():
        require(digest(name) == record['sha256'], f'Maintenance manifest stale: {name}')
        text = path(name).read_text()
        require(not any(p.search(text) for p in (private_address, personal_path, credential)),
                f'Publication privacy review required: {name}')
    return {'passed': True, 'items': len(ids), 'classified_files': len(recorded),
            'real_run_records_checked': len(runs), 'changed_source_check': base_ref is not None,
            'scope': 'CPU record consistency only; does not establish NPU correctness or performance.',
            'model_requests': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-ref', help='Optional Git commit to check changed runtime source registration')
    parser.add_argument('--refresh-review-manifest', action='store_true', help='Refresh maintenance-record hashes only')
    args = parser.parse_args()
    if args.refresh_review_manifest:
        refresh_manifest()
    print(json.dumps(verify(args.base_ref), ensure_ascii=False))


if __name__ == '__main__':
    main()
