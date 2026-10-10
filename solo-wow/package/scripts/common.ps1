# Shared helpers for the Azeroth Solo launcher scripts.
$ErrorActionPreference = 'Stop'

$Root        = Split-Path $PSScriptRoot -Parent
$ServerDir   = Join-Path $Root 'server'
$MariaDir    = Join-Path $Root 'mariadb'
$DbDataDir   = Join-Path $Root 'mariadb-data'
$SqlDir      = Join-Path $Root 'db'
$SettingsFile = Join-Path $Root 'settings.json'
$DbPort      = 3310
$DbRootPass  = 'root'

function Write-Title($text) {
    Write-Host ''
    Write-Host ('=' * 70) -ForegroundColor DarkYellow
    Write-Host "  $text" -ForegroundColor Yellow
    Write-Host ('=' * 70) -ForegroundColor DarkYellow
}

function Write-Step($text) { Write-Host "  > $text" -ForegroundColor Cyan }
function Write-Ok($text)   { Write-Host "  OK  $text" -ForegroundColor Green }
function Write-Warn2($text) { Write-Host "  !!  $text" -ForegroundColor Magenta }

function Find-ServerExe([string]$name) {
    $f = Get-ChildItem -Recurse -File -Path $ServerDir -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $f) { throw "Could not find $name inside $ServerDir" }
    return $f.FullName
}

function Find-MariaExe([string[]]$names) {
    foreach ($n in $names) {
        $p = Join-Path (Join-Path $MariaDir 'bin') $n
        if (Test-Path $p) { return $p }
    }
    throw "Could not find any of: $($names -join ', ') in $MariaDir\bin"
}

function Get-Settings {
    if (Test-Path $SettingsFile) { return Get-Content $SettingsFile -Raw | ConvertFrom-Json }
    return [pscustomobject]@{ WowPath = '' }
}

function Save-Settings($s) { $s | ConvertTo-Json | Set-Content -Encoding UTF8 $SettingsFile }

function Test-Port([int]$port) {
    $c = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $c.BeginConnect('127.0.0.1', $port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(300)
        if ($ok -and $c.Connected) { $c.EndConnect($iar); return $true }
        return $false
    } catch { return $false } finally { $c.Close() }
}

function Wait-Port([int]$port, [int]$seconds, [string]$what) {
    $deadline = (Get-Date).AddSeconds($seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $port) { return $true }
        Start-Sleep -Milliseconds 700
        Write-Host -NoNewline '.'
    }
    Write-Host ''
    throw "$what did not start within $seconds seconds."
}

function Start-Database {
    if (Test-Port $DbPort) { return }
    Write-Step 'Starting database...'
    $mysqld = Find-MariaExe @('mariadbd.exe', 'mysqld.exe')
    Start-Process -FilePath $mysqld -ArgumentList @("--datadir=`"$DbDataDir`"", "--port=$DbPort", '--bind-address=127.0.0.1', '--max_allowed_packet=256M') -WindowStyle Hidden | Out-Null
    Wait-Port $DbPort 90 'The database' | Out-Null
    Write-Host ''
    Write-Ok 'Database running'
}

function Stop-Database {
    if (-not (Test-Port $DbPort)) { return }
    Write-Step 'Stopping database...'
    $admin = Find-MariaExe @('mariadb-admin.exe', 'mysqladmin.exe')
    cmd /c "`"$admin`" -uroot -p$DbRootPass -h127.0.0.1 -P$DbPort shutdown 2>nul"
    $deadline = (Get-Date).AddSeconds(30)
    while ((Test-Port $DbPort) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
}

function Invoke-Sql([string]$sql) {
    $mysql = Find-MariaExe @('mariadb.exe', 'mysql.exe')
    & $mysql -uroot "-p$DbRootPass" -h127.0.0.1 "-P$DbPort" -e $sql
    if ($LASTEXITCODE -ne 0) { throw "SQL failed: $sql" }
}

function Import-SqlFile([string]$file) {
    $mysql = Find-MariaExe @('mariadb.exe', 'mysql.exe')
    $cmd = "`"`"$mysql`" -uroot -p$DbRootPass -h127.0.0.1 -P$DbPort --max_allowed_packet=256M --default-character-set=utf8 < `"$file`"`""
    cmd /c $cmd
    if ($LASTEXITCODE -ne 0) { throw "Importing $file failed." }
}

function Test-WowFolder([string]$p) {
    return ($p -and (Test-Path (Join-Path $p 'WoW.exe')) -and (Test-Path (Join-Path $p 'Data')))
}

function Set-Realmlist([string]$wow) {
    $rl = Join-Path $wow 'realmlist.wtf'
    $backup = Join-Path $wow 'realmlist.wtf.original'
    if ((Test-Path $rl) -and -not (Test-Path $backup)) { Copy-Item $rl $backup }
    Set-Content -Encoding ASCII $rl 'set realmlist 127.0.0.1'
}

function Stop-GameServers {
    foreach ($n in @('mangosd', 'realmd')) {
        Get-Process -Name $n -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Step "Stopping $n..."
            $_.CloseMainWindow() | Out-Null
            if (-not $_.WaitForExit(8000)) { $_ | Stop-Process -Force }
        }
    }
}
