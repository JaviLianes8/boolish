# Build and upload to PyPI. Run scripts/check.ps1 first.
# Hard rule: the distribution name must not already exist on PyPI.
$ErrorActionPreference = "Stop"

try {
    Invoke-WebRequest -UseBasicParsing "https://pypi.org/pypi/strtobool/json" | Out-Null
    throw "The name 'strtobool' already exists on PyPI. Choose another before publishing."
} catch [System.Net.WebException], [Microsoft.PowerShell.Commands.HttpResponseException] {
    if ($_.Exception.Response.StatusCode.value__ -ne 404) { throw }
}

Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
python -m twine check dist/*
python -m twine upload dist/*
