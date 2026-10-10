# Zelda of Warcraft launcher: starts the Azeroth Solo server, then the Benilla client with Zelda controls.
$ErrorActionPreference = 'Stop'
$Here = Split-Path $PSScriptRoot -Parent
$Solo = Join-Path (Split-Path $Here -Parent) 'AzerothSolo'
try {
    if (-not (Test-Path (Join-Path $Solo 'scripts\common.ps1'))) {
        throw "Azeroth Solo was not found next to this folder ($Solo). Put the ZeldaWoW folder beside AzerothSolo."
    }
    . (Join-Path $Solo 'scripts\common.ps1')
    Write-Title 'Zelda of Warcraft'
    if (-not (Test-Path (Join-Path $Solo '.database-ready'))) { throw 'Run SETUP.bat in the AzerothSolo folder first.' }
    $settings = Get-Settings
    $wow = $settings.WowPath
    if (-not (Test-WowFolder $wow)) { throw 'WoW folder not found. Run SETUP.bat in AzerothSolo again.' }

    # Benilla does not run Warden, so the server must not ask for it
    $ac = Get-ChildItem -Recurse -File $ServerDir -Filter anticheat.conf.dist | Select-Object -First 1
    if ($ac) {
        $conf = Join-Path $ac.DirectoryName 'anticheat.conf'
        (Get-Content $ac.FullName) -replace '^Enable\s*=.*', 'Enable = 0' -replace '^Warden\.Enable\s*=.*', 'Warden.Enable = 0' |
            Set-Content -Encoding ASCII $conf
    }

    Start-Database
    $realmd = Find-ServerExe 'realmd.exe'
    $mangosd = Find-ServerExe 'mangosd.exe'
    if (-not (Get-Process -Name realmd -ErrorAction SilentlyContinue)) {
        Write-Step 'Starting login server...'
        Start-Process -FilePath $realmd -WorkingDirectory (Split-Path $realmd -Parent) -WindowStyle Minimized | Out-Null
    }
    if (-not (Get-Process -Name mangosd -ErrorAction SilentlyContinue)) {
        Write-Step 'Starting world server (a console window opens - leave it running)...'
        Start-Process -FilePath $mangosd -WorkingDirectory (Split-Path $mangosd -Parent) | Out-Null
    }
    Write-Step 'Waiting for the world to load'
    Wait-Port 3724 60 'The login server' | Out-Null
    Wait-Port 8085 400 'The world server' | Out-Null
    Write-Host ''
    Write-Ok 'Azeroth is online'

    $env:WOW_DATA = Join-Path $wow 'Data'
    $env:WOW_HOST = '127.0.0.1:3724'
    Write-Step 'Launching Zelda of Warcraft... (account PLAYER / password PLAYER)'
    $game = Start-Process -FilePath (Join-Path $Here 'benilla.exe') -WorkingDirectory $Here -PassThru
    $game.WaitForExit()

    Write-Step 'Game closed. Saving your character...'
    Start-Sleep -Seconds 25
    Stop-GameServers
    Stop-Database
    Write-Ok 'Everything shut down cleanly.'
}
catch {
    Write-Host ''
    Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host '  Press Enter to close'
}
