# PowerShell 5.1 / PowerShell 7
# Ejecutar desde cualquier ubicacion:
# powershell -NoProfile -ExecutionPolicy Bypass -File .\ISO-AI-Governance\download_iso_ai.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$script = Join-Path $here "download_iso_ai.py"
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $script
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $script
} else {
    Write-Error "Se requiere Python 3 (https://www.python.org/downloads/). Alternativa: GitHub Actions en el repositorio."
    exit 1
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Consulta ISO-AI-Governance\ISO_IA_5_Niveles y el ZIP generado."
