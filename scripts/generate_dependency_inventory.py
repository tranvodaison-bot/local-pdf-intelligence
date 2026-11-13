"""Offline provisional CycloneDX inventory: lockfiles plus direct Python packages.

Not a release SBOM: Python transitive dependencies and Rust license metadata are
not represented, and optional lockfile packages are not deployment-filtered.
"""
import importlib.metadata as metadata
import json
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
components = []
for line in (root / "requirements-dev.txt").read_text(encoding="utf-8").splitlines():
    if "==" not in line or line.startswith("#"):
        continue
    name, requested = line.split("==", 1)
    try:
        record = metadata.metadata(name)
        installed = metadata.version(name)
        license_name = record.get("License-Expression") or record.get("License")
    except metadata.PackageNotFoundError:
        installed, license_name = "NOT_INSTALLED", None
    entry = {"type":"library", "name":name, "version":requested, "properties":[{"name":"inventory:source", "value":"python-direct"}, {"name":"inventory:installed", "value":installed}]}
    if license_name:
        entry["licenses"] = [{"license":{"name":license_name}}]
    components.append(entry)
lock = json.loads((root / "apps/desktop/package-lock.json").read_text(encoding="utf-8"))
for path, entry in lock["packages"].items():
    if not path or "version" not in entry:
        continue
    component = {"type":"library", "name":path.rsplit("node_modules/",1)[-1], "version":entry["version"], "properties":[{"name":"inventory:source", "value":"npm-lock"}, {"name":"inventory:path", "value":path}]}
    if entry.get("license"):
        component["licenses"] = [{"license":{"name":entry["license"]}}]
    components.append(component)
lock = tomllib.loads((root / "apps/desktop/src-tauri/Cargo.lock").read_text(encoding="utf-8"))
for entry in lock["package"]:
    components.append({"type":"library", "name":entry["name"], "version":entry["version"], "properties":[{"name":"inventory:source", "value":"cargo-lock-license-unknown"}]})
output = {"bomFormat":"CycloneDX", "specVersion":"1.5", "version":1, "components":components}
path = root / "docs/evidence/CTO-002-dependency-inventory.json"
path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Generated provisional inventory: {len(components)} components; Python transitive and Rust license review are incomplete")
