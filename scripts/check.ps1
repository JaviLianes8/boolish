# Local quality gate. Run before every commit. No CI runs in the cloud.
# Each step must pass on its own; the script stops at the first failure.
$ErrorActionPreference = "Stop"

function Step([string]$name, [scriptblock]$command) {
    & $command
    if ($LASTEXITCODE -ne 0) { throw "$name failed with exit code $LASTEXITCODE" }
}

Step "ruff format" { ruff format --check . }
Step "ruff check" { ruff check . }
Step "mypy" { mypy --strict src tests }
Step "pytest" { python -m pytest }
