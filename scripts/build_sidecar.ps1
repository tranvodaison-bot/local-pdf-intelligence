param(
    [Parameter(Mandatory=$true)][string]$BuildRoot
)
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $BuildRoot "source"
$module = Join-Path $source "localpdf"
$sql = Join-Path $source "db"
$entry = Join-Path $source "scripts"
New-Item -ItemType Directory -Force -Path $module,$sql,$entry | Out-Null
Get-ChildItem -LiteralPath (Join-Path $repoRoot "apps/api/localpdf") -Filter "*.py" -File | Copy-Item -Destination $module
Copy-Item -LiteralPath (Join-Path $repoRoot "db/001_initial.sql") -Destination $sql
Copy-Item -LiteralPath (Join-Path $repoRoot "scripts/sidecar_entry.py") -Destination $entry
Push-Location $source
try {
    python -m PyInstaller --noconfirm --onefile --name localpdf-sidecar --paths $source --add-data "$(Join-Path $sql '001_initial.sql');db" --collect-submodules uvicorn --distpath (Join-Path $BuildRoot "dist") --workpath (Join-Path $BuildRoot "work") --specpath $BuildRoot (Join-Path $entry "sidecar_entry.py")
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }
} finally { Pop-Location }
