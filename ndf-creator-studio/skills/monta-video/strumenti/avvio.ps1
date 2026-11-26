# NDF Creator Studio: il programma di avvio per Windows. Lo stesso comando installa la prima volta e controlla in
# silenzio a ogni chat:
#   powershell -NoProfile -ExecutionPolicy Bypass -File "<studio>\strumenti\avvio.ps1" [opzioni di controllo.py]
#
# Usa solo quello che c'è su ogni Windows 10 e 11 (PowerShell, tar). Lo studio ha il SUO Python 3.12, nella sua
# casa (%LOCALAPPDATA%\NDFCreatorStudio\python): se non c'è lo scarica (circa 45 MB, una volta sola) e lo controlla
# con l'impronta SHA-256 scritta qui sotto. Non usa il Python del computer (spesso è il finto Python dello Store).
# Sempre la versione x64: gira anche sui Windows ARM. Niente amministratore, niente installato nel sistema.
# Poi passa la mano a controllo.py, che stampa le righe STATO e alla fine PRONTO o NON PRONTO.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'      # con la barra di avanzamento il download è molto più lento

$PyVersione = '3.12.15'
$PyUscita   = '20261021'
$PyImpronta = 'be7f14464d1d66f84429ad27e01f6d1482963afff64a2fb5256b2a51c7b5d398'
$PyUrl      = "https://github.com/astral-sh/python-build-standalone/releases/download/$PyUscita/cpython-$PyVersione%2B$PyUscita-x86_64-pc-windows-msvc-install_only.tar.gz"

$Qui = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($env:NDF_STUDIO_CASA) { $Casa = $env:NDF_STUDIO_CASA }
else {
    $Locale = $env:LOCALAPPDATA
    if (-not $Locale) { $Locale = Join-Path $HOME 'AppData\Local' }
    $Casa = Join-Path $Locale 'NDFCreatorStudio'
}

function Va([string]$Py) {
    if (-not $Py -or -not (Test-Path -LiteralPath $Py -PathType Leaf)) { return $false }
    try {
        & $Py -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" *> $null
        return ($LASTEXITCODE -eq 0)
    } catch { return $false }
}

function NonPronto([string]$Perche) {
    Write-Output "STATO Python dello studio: MANCA · $Perche"
    Write-Output 'NON PRONTO'
    exit 1
}

$Py = $null
foreach ($c in @((Join-Path $Casa 'venv\Scripts\python.exe'), (Join-Path $Casa 'python\python.exe'))) {
    if (Va $c) { $Py = $c; break }
}

if (-not $Py) {
    Write-Output 'STATO Python dello studio: lo scarico (circa 45 MB, una volta sola)'
    New-Item -ItemType Directory -Force -Path $Casa | Out-Null
    $Parte = Join-Path $Casa 'python.tar.gz.parziale'
    $Nuovo = Join-Path $Casa 'python.nuovo'
    Remove-Item -Recurse -Force -LiteralPath $Parte, $Nuovo -ErrorAction SilentlyContinue
    $ok = $false
    for ($prova = 1; $prova -le 3; $prova++) {
        try {
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $PyUrl -OutFile $Parte -UseBasicParsing -TimeoutSec 600
            $ok = $true; break
        } catch {
            Remove-Item -Force -LiteralPath $Parte -ErrorAction SilentlyContinue
            if ($prova -lt 3) {
                Write-Output "STATO Python dello studio: il download si è fermato, riprovo ($($prova + 1) di 3)"
                Start-Sleep -Seconds 3
            }
        }
    }
    if (-not $ok) { NonPronto 'il download non arriva: controlla internet e riprova' }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Parte).Hash.ToLower() -ne $PyImpronta) {
        Remove-Item -Force -LiteralPath $Parte
        NonPronto "il file scaricato non è quello giusto (impronta diversa), quindi non l'ho usato: riprova più tardi"
    }
    New-Item -ItemType Directory -Force -Path $Nuovo | Out-Null
    & tar -xzf $Parte -C $Nuovo
    Remove-Item -Force -LiteralPath $Parte
    if (-not (Va (Join-Path $Nuovo 'python\python.exe'))) {
        Remove-Item -Recurse -Force -LiteralPath $Nuovo
        NonPronto 'il Python scaricato non parte su questo computer'
    }
    Remove-Item -Recurse -Force -LiteralPath (Join-Path $Casa 'python') -ErrorAction SilentlyContinue
    Move-Item -LiteralPath (Join-Path $Nuovo 'python') -Destination (Join-Path $Casa 'python')
    Remove-Item -Recurse -Force -LiteralPath $Nuovo -ErrorAction SilentlyContinue
    $Py = Join-Path $Casa 'python\python.exe'
    Write-Output "STATO Python dello studio: OK · $PyVersione"
}

$env:PYTHONIOENCODING = 'utf-8'
& $Py (Join-Path $Qui 'controllo.py') @args
exit $LASTEXITCODE
