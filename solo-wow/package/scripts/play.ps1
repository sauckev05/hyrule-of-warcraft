# Starts the database, login server and world server, then launches WoW. Shuts everything down afterwards.
. (Join-Path $PSScriptRoot 'common.ps1')

try {
    Write-Title 'Azeroth Solo'
    if (-not (Test-Path (Join-Path $Root '.database-ready'))) { throw 'Run SETUP.bat first.' }
    $settings = Get-Settings
    $wow = $settings.WowPath
    if (-not (Test-WowFolder $wow)) { throw 'WoW folder not found. Run SETUP.bat again.' }

    Start-Database

    $realmd = Find-ServerExe 'realmd.exe'
    $mangosd = Find-ServerExe 'mangosd.exe'
    if (-not (Get-Process -Name realmd -ErrorAction SilentlyContinue)) {
        Write-Step 'Starting login server...'
        Start-Process -FilePath $realmd -WorkingDirectory (Split-Path $realmd -Parent) -WindowStyle Minimized | Out-Null
    }
    if (-not (Get-Process -Name mangosd -ErrorAction SilentlyContinue)) {
        Write-Step 'Starting world server (a new console window opens - leave it running)...'
        Start-Process -FilePath $mangosd -WorkingDirectory (Split-Path $mangosd -Parent) | Out-Null
    }
    Write-Step 'Waiting for the world to load (1-3 minutes the first time)'
    Wait-Port 3724 60 'The login server' | Out-Null
    Wait-Port 8085 400 'The world server' | Out-Null
    Write-Host ''
    Write-Ok 'Azeroth is online'

    Set-Realmlist $wow
    Write-Step 'Launching World of Warcraft... (account PLAYER / password PLAYER)'
    $game = Start-Process -FilePath (Join-Path $wow 'WoW.exe') -WorkingDirectory $wow -PassThru
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
