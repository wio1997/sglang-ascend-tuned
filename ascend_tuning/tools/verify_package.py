"""Verify the published source collection without importing Torch or using an NPU."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

ROOT = Path(__file__).resolve().parents[2]
TUNING = ROOT / "ascend_tuning"


def safe_path(name):
    p = PurePosixPath(name)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise ValueError(f"Unsafe package path: {name}")
    target = ROOT.joinpath(*p.parts)
    if any(q.is_symlink() for q in [target, *target.parents] if q != ROOT.parent):
        raise ValueError(f"Symlink in package path: {name}")
    return target


def verify():
    manifest = json.loads((TUNING / "PACKAGE_MANIFEST.json").read_text())
    parsed = 0
    private_address = re.compile(
        r"(?<![\d.])(?:10\.(?:\d{1,3}\.){2}\d{1,3}|"
        r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|"
        r"192\.168\.\d{1,3}\.\d{1,3})(?![\d.])"
    )
    personal_path = re.compile("/" + "Users" + r"/[^/\s]+/")
    token = re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")
    credential = re.compile(
        r"(?i)(?:password|api[_-]?key|access_token|secret_key)\s*[:=]\s*['\"][^'\"\n]{8,}['\"]"
    )
    for name, record in manifest["files"].items():
        target = safe_path(name)
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Hash mismatch: {name}")
        text = data.decode("utf-8")
        if private_address.search(text) or personal_path.search(text) or token.search(text) or credential.search(text):
            raise ValueError(f"Publication privacy review required: {name}")
        if target.suffix == ".py":
            ast.parse(text, filename=name)
            parsed += 1
    index = json.loads((TUNING / "profiles/index.json").read_text())
    names = [p["name"] for p in index["profiles"]]
    if len(names) != len(set(names)) or index["default_enabled_profile"] is not None:
        raise ValueError("Invalid profile selection")
    for profile in index["profiles"]:
        prefix = f"profiles/{profile['name']}/"
        for item in profile["files"]:
            if not item["path"].startswith(prefix):
                raise ValueError("Cross-profile file reference")
            public_name = "ascend_tuning/" + item["path"]
            if manifest["files"][public_name]["sha256"] != item["sha256"]:
                raise ValueError(f"Profile hash mismatch: {item['path']}")
    return {"passed": True, "files": len(manifest["files"]), "python_sources_parsed": parsed,
            "profiles": names, "validation_scope": "CPU package integrity, syntax, privacy patterns and profile closure only",
            "model_requests": 0, "NPU_validation": False}


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False))
