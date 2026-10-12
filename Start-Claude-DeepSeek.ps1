[CmdletBinding()]
param(
    [string]$Model = 'deepseek-flash[1m]',
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ClaudeArgs = @()
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command 'claude' -ErrorAction SilentlyContinue)) {
    Write-Host "Khong tim thay lenh 'claude'. Hay cai Claude Code va mo lai PowerShell." -ForegroundColor Red
    exit 1
}

# Reuse DEEPSEEK_API_KEY if already set; otherwise prompt without echoing it.
$apiKey = $env:DEEPSEEK_API_KEY
if ([string]::IsNullOrWhiteSpace($apiKey)) {
    $secureKey = Read-Host 'Nhap DeepSeek API key (ky tu se duoc an)' -AsSecureString
    if ($secureKey.Length -eq 0) {
        Write-Host 'API key dang trong. Huy khoi dong.' -ForegroundColor Red
        exit 1
    }
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
    try {
        $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    }
    finally {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    }
}

# DeepSeek's official Anthropic-compatible endpoint for Claude Code.
$env:ANTHROPIC_BASE_URL = 'https://api.deepseek.com/anthropic'
$env:ANTHROPIC_AUTH_TOKEN = $apiKey
$env:ANTHROPIC_MODEL = $Model
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = $Model
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = $Model
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = 'deepseek-flash'
$env:CLAUDE_CODE_SUBAGENT_MODEL = 'deepseek-flash'
$env:CLAUDE_CODE_EFFORT_LEVEL = 'max'
$env:CLAUDE_CODE_AUTO_COMPACT_WINDOW = '786432'

# Prevent an inherited Anthropic key from taking precedence.
Remove-Item Env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue

Write-Host ''
Write-Host 'Claude Code -> DeepSeek' -ForegroundColor Cyan
Write-Host "Model : $Model"
Write-Host "Folder: $((Get-Location).Path)"
Write-Host 'API key khong duoc ghi vao file; no chi ton tai trong tien trinh nay.'
Write-Host 'Go /exit trong Claude Code de ket thuc.'
Write-Host ''

try {
    & claude --model $Model @ClaudeArgs
    $claudeExitCode = $LASTEXITCODE
}
finally {
    # Clear temporary credentials/config from this PowerShell process.
    @(
        'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL',
        'ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL',
        'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL',
        'CLAUDE_CODE_SUBAGENT_MODEL', 'CLAUDE_CODE_EFFORT_LEVEL',
        'CLAUDE_CODE_AUTO_COMPACT_WINDOW'
    ) | ForEach-Object { Remove-Item "Env:$_" -ErrorAction SilentlyContinue }
    $apiKey = $null
}

if ($null -eq $claudeExitCode) { exit 1 }
exit $claudeExitCode
