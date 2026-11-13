import sys
from pathlib import Path

import yaml

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "apps" / "api"))
from localpdf.main import app

def test_contract_marks_only_implemented_routes_as_implemented():
    spec = yaml.safe_load((root / "contracts/openapi.yaml").read_text(encoding="utf-8"))
    actual = {(route.path.removeprefix("/api/v1"), method.lower()) for route in app.routes for method in (getattr(route, "methods", None) or set())}
    documented = set()
    for path, operations in spec["paths"].items():
        implemented = operations["x-implementation-status"] == "implemented"
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in operations:
                continue
            assert ((path, method) in actual) == implemented
            if implemented:
                documented.add((path, method))
    assert documented == actual
    assert spec["security"] == [{"bearerAuth": []}]
