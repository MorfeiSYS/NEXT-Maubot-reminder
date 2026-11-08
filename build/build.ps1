param(
    [switch]$BumpPatch
)

$ErrorActionPreference = "Stop"
if (-not $env:HOME -and $env:USERPROFILE) {
    $env:HOME = $env:USERPROFILE
}
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VersionFile = Join-Path $Root "VERSION"
$MaubotYaml = Join-Path $Root "maubot.yaml"
$OutDir = Join-Path $Root "build"

if (-not (Test-Path $VersionFile)) {
    throw "VERSION file not found at $VersionFile"
}

$Version = (Get-Content $VersionFile -Raw).Trim()

if ($BumpPatch) {
    if ($Version -match '^(\d+)\.(\d+)\.(\d+)$') {
        $patch = [int]$Matches[3] + 1
        $Version = "$($Matches[1]).$($Matches[2]).$patch"
        Set-Content -Path $VersionFile -Value $Version
        $yaml = Get-Content $MaubotYaml -Raw
        $yaml = $yaml -replace '(?m)^version:\s*.+$', "version: $Version"
        Set-Content -Path $MaubotYaml -Value $yaml.TrimEnd()
        Write-Host "Bumped version to $Version"
    } else {
        throw "VERSION must be semver x.y.z for -BumpPatch"
    }
}

if (-not (Get-Command mbc -ErrorAction SilentlyContinue)) {
    throw "mbc (maubot-cli) not found in PATH. Install maubot and ensure mbc is available."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutFile = Join-Path $OutDir "NEXT-Maubot-reminder-v$Version.mbp"

Push-Location $Root
try {
    & mbc build -o $OutFile .
    if ($LASTEXITCODE -ne 0) {
        throw "mbc build failed with exit code $LASTEXITCODE"
    }
    Write-Host "Built: $OutFile"
} finally {
    Pop-Location
}
