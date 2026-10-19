"""Export one historical source/configuration profile; never install or run it."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil

from verify_package import TUNING, verify


def export(profile_name, output):
    verify()
    profiles = json.loads((TUNING / "profiles/index.json").read_text())["profiles"]
    matches = [p for p in profiles if p["name"] == profile_name]
    if len(matches) != 1:
        raise ValueError("Unknown profile")
    profile = matches[0]
    output = Path(output).absolute()
    if output.exists():
        raise ValueError("Output must be a new directory; existing files are never overwritten")
    if any(p.is_symlink() for p in output.parents):
        raise ValueError("Output parent must not be a symlink")
    prefix = f"profiles/{profile_name}/"
    planned = []
    for item in profile["files"]:
        name = item["path"]
        if not name.startswith(prefix):
            raise ValueError("Cross-profile path")
        relative = PurePosixPath(name[len(prefix):])
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError("Unsafe export path")
        planned.append((TUNING / name, output.joinpath(*relative.parts)))
    output.mkdir(parents=True)
    for source, target in planned:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (output / "export-manifest.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    return {"exported": profile_name, "files": len(planned), "output": str(output),
            "status": profile["status"], "installed": False, "model_started": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.profile, args.output), ensure_ascii=False))
