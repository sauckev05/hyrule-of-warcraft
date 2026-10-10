# Shared helpers for the Azeroth Solo launcher scripts.
$ErrorActionPreference = 'Stop'

$Root        = Split-Path $PSScriptRoot -Parent
$ServerDir   = Join-Path $Root 'server'
$MariaDir    = Join-Path $Root 'mariadb'
$DbDataDir   = Join-Path $Root 'mariadb-data'
$SqlDir      = Join-Path $Root 'db'
$SettingsFile = Join-Path $Root 'settings.json'
$DbPort      = 3310
$LogFile     = Join-Path $Root 'setup.log'
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
    if (-not (Test-Port $DbPort)) {
    Write-Step 'Starting database...'
    $mysqld = Find-MariaExe @('mariadbd.exe', 'mysqld.exe')
    # --no-defaults: ignore any my.ini left behind by other MySQL/MariaDB installs on this PC
    Start-Process -FilePath $mysqld -ArgumentList @('--no-defaults', "--datadir=`"$DbDataDir`"", "--port=$DbPort", '--bind-address=127.0.0.1', '--max_allowed_packet=256M', '--skip-name-resolve') -WindowStyle Hidden | Out-Null
    Wait-Port $DbPort 90 'The database' | Out-Null
    Write-Host ''
    }
    # The port opens a moment before the server accepts logins - wait until a real query works
    $deadline = (Get-Date).AddSeconds(60)
    while ($true) {
        if ((Invoke-MariaDb 'SELECT 1;' '' -Quiet) -eq 0) { break }
        if ((Get-Date) -gt $deadline) { throw "The database is running but refuses logins. Details: $(Get-LogTail)" }
        Start-Sleep -Seconds 2
    }
    Write-Ok 'Database running'
}

function Get-LogTail {
    if (Test-Path $LogFile) { return ((Get-Content $LogFile -Tail 12) -join ' | ') }
    return '(no log)'
}

# Runs a MariaDB command-line tool directly (no cmd.exe), feeding SQL through standard input and
# writing everything it prints - plus how it exited - to setup.log. Returns the exit code.
function Invoke-MariaTool([string]$exeNames, [string[]]$toolArgs, [string]$inputFile, [switch]$Quiet) {
    $exe = Find-MariaExe ($exeNames -split ',')
    $common = @('--no-defaults', '--protocol=TCP', '-uroot', "-p$DbRootPass", '-h127.0.0.1', "-P$DbPort")
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $exe
    $psi.Arguments = (($common + $toolArgs) | ForEach-Object { if ($_ -match '\s') { '"' + $_ + '"' } else { $_ } }) -join ' '
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.WorkingDirectory = Split-Path $exe -Parent
    if (-not $Quiet) { Add-Content -Path $LogFile -Value "---- $(Get-Date -Format s) $(Split-Path $exe -Leaf) $($toolArgs -join ' ') $inputFile" }
    try {
        $p = [System.Diagnostics.Process]::Start($psi)
    } catch {
        Add-Content -Path $LogFile -Value "could not start ${exe}: $($_.Exception.Message)"
        return -1
    }
    $errTask = $p.StandardError.ReadToEndAsync()
    $outTask = $p.StandardOutput.ReadToEndAsync()
    if ($inputFile) {
        # copy the file byte-for-byte so UTF-8 text in the database survives
        $fs = [System.IO.File]::OpenRead($inputFile)
        $fs.CopyTo($p.StandardInput.BaseStream, 1048576)
        $fs.Close()
        $p.StandardInput.BaseStream.Flush()
    }
    $p.StandardInput.Close()
    $p.WaitForExit()
    $text = ($outTask.Result + $errTask.Result).Trim()
    if ($text -and -not ($Quiet -and $p.ExitCode -eq 0)) { Add-Content -Path $LogFile -Value $text }
    if ($p.ExitCode -ne 0) { Add-Content -Path $LogFile -Value ("exit code {0} (0x{0:X8})" -f $p.ExitCode) }
    return $p.ExitCode
}

function Invoke-MariaDb([string]$sql, [string]$inputFile, [switch]$Quiet) {
    $file = $inputFile
    if (-not $file) {
        $file = Join-Path $Root 'last-command.sql'
        Set-Content -Path $file -Value $sql -Encoding ASCII
    }
    return Invoke-MariaTool 'mariadb.exe,mysql.exe' @('--max_allowed_packet=256M', '--default-character-set=utf8') $file -Quiet:$Quiet
}

function Stop-Database {
    if (-not (Test-Port $DbPort)) { return }
    Write-Step 'Stopping database...'
    Invoke-MariaTool 'mariadb-admin.exe,mysqladmin.exe' @('shutdown') '' | Out-Null
    $deadline = (Get-Date).AddSeconds(30)
    while ((Test-Port $DbPort) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
    if (Test-Port $DbPort) {
        Get-Process -Name mariadbd, mysqld -ErrorAction SilentlyContinue | Stop-Process -Force
    }
}

function Invoke-Sql([string]$sql) {
    $code = Invoke-MariaDb $sql ''
    if ($code -ne 0) { throw "Database command failed. Details: $(Get-LogTail)" }
}

function Import-SqlFile([string]$file) {
    $code = Invoke-MariaDb '' $file
    if ($code -ne 0) { throw "Importing $file failed. Details: $(Get-LogTail)" }
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
