"""Python orchestration of the installed Artifact Tool workbook exporter."""
import json
import os
import shutil
import subprocess
from pathlib import Path


def export(payload, output, root):
    output.mkdir(parents=True, exist_ok=True)
    payload_path = output / "flow_atlas.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    run_builder(root, root / 'src/export_excel.mjs', [str(payload_path), str(output)])
    return output / 'flow_atlas.xlsx'


def run_builder(root, script, arguments):
    """Reuse the same installed Artifact Tool runtime for workbook builders."""
    deps = Path(os.environ.get("FLOW_ATLAS_NODE_MODULES", Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"))
    if not (deps / "@oai/artifact-tool").exists():
        raise RuntimeError("Artifact Tool unavailable. Set FLOW_ATLAS_NODE_MODULES to the installed node_modules directory.")
    work = root / "tmp/export"
    work.mkdir(parents=True, exist_ok=True)
    link = work / "node_modules"
    if not link.exists():
        if os.name == "nt":
            subprocess.run(["powershell", "-NoProfile", "-Command",
                f"New-Item -ItemType Junction -Path '{str(link).replace(chr(39), chr(39)*2)}' -Target '{str(deps).replace(chr(39), chr(39)*2)}' | Out-Null"], check=True)
        else:
            link.symlink_to(deps, target_is_directory=True)
    target=work/script.name
    shutil.copyfile(script,target)
    subprocess.run(["node", str(target), *arguments], check=True)
