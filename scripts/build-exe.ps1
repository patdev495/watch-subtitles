[CmdletBinding()]
param(
    [ValidatePattern('^[a-zA-Z0-9._-]+$')]
    [string]$Name = 'watch-subtitles'
)

$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$frontendDirectory = Join-Path $projectRoot 'frontend'
$frontendDist = Join-Path $frontendDirectory 'dist'
$outputDirectory = Join-Path $projectRoot 'dist'
$workDirectory = Join-Path $projectRoot 'build\pyinstaller'
$pathSeparator = [IO.Path]::PathSeparator

if ($env:FFMPEG_PATH -and (Test-Path -LiteralPath $env:FFMPEG_PATH -PathType Leaf)) {
    $ffmpegPath = (Resolve-Path -LiteralPath $env:FFMPEG_PATH).Path
}
else {
    $ffmpegCommand = Get-Command ffmpeg -CommandType Application -ErrorAction Stop
    $ffmpegPath = $ffmpegCommand.Source
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw $FailureMessage
    }
}

Push-Location $projectRoot
try {
    Write-Host 'Installing locked frontend dependencies...'
    Invoke-CheckedCommand { pnpm --dir $frontendDirectory install --frozen-lockfile } `
        'Failed to install frontend dependencies.'

    Write-Host 'Building frontend...'
    Invoke-CheckedCommand { pnpm --dir $frontendDirectory build } 'Failed to build the frontend.'

    if (-not (Test-Path (Join-Path $frontendDist 'index.html'))) {
        throw 'Frontend build did not produce frontend/dist/index.html.'
    }

    Write-Host 'Packaging one-file executable...'
    Invoke-CheckedCommand {
        uv run --with pyinstaller pyinstaller `
            --noconfirm `
            --clean `
            --log-level WARN `
            --onefile `
            --windowed `
            --name $Name `
            --distpath $outputDirectory `
            --workpath $workDirectory `
            --specpath $workDirectory `
            --add-data "${frontendDist}${pathSeparator}frontend/dist" `
            --add-binary "${ffmpegPath}${pathSeparator}." `
            main.py
    } 'PyInstaller failed to create the executable.'

    Write-Host "Created $(Join-Path $outputDirectory "$Name.exe")"
}
finally {
    Pop-Location
}
