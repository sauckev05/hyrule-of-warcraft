# Stops the world server, login server and database.
. (Join-Path $PSScriptRoot 'common.ps1')
Write-Title 'Stopping Azeroth Solo'
Stop-GameServers
Stop-Database
Write-Ok 'Stopped.'
Start-Sleep -Seconds 2
