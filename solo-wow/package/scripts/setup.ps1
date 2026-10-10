# One-time setup for Azeroth Solo: database + map extraction from your own WoW 1.12.1 client.
. (Join-Path $PSScriptRoot 'common.ps1')

try {
    Write-Title 'Azeroth Solo - one-time setup'

    # ---------------------------------------------------------------- find the WoW client
    $settings = Get-Settings
    $wow = $settings.WowPath
    if (-not (Test-WowFolder $wow)) {
        $candidates = @(
            'E:\wow\New folder\SoloCraft 1.12.1',
            (Split-Path $Root -Parent),
            'C:\Program Files (x86)\World of Warcraft',
            'C:\World of Warcraft'
        )
        $wow = $candidates | Where-Object { Test-WowFolder $_ } | Select-Object -First 1
    }
    if (-not (Test-WowFolder $wow)) {
        Add-Type -AssemblyName System.Windows.Forms
        $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
        $dlg.Description = 'Select your World of Warcraft 1.12.1 folder (the one containing WoW.exe)'
        if ($dlg.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $wow = $dlg.SelectedPath }
    }
    if (-not (Test-WowFolder $wow)) { throw 'No WoW 1.12.1 folder selected (it must contain WoW.exe and a Data folder).' }
    $ver = (Get-Item (Join-Path $wow 'WoW.exe')).VersionInfo.FileVersion
    Write-Ok "WoW client: $wow  (version $ver)"
    if ($ver -and $ver -notmatch '1\.12') { Write-Warn2 'This does not look like a 1.12.x client. The server needs 1.12.1 (build 5875).' }
    $settings = [pscustomobject]@{ WowPath = $wow }
    Save-Settings $settings

    # ---------------------------------------------------------------- server config
    Write-Step 'Configuring server...'
    Get-ChildItem -Recurse -File $ServerDir -Filter *.conf | ForEach-Object {
        $c = Get-Content $_.FullName
        $c = $c -replace '127\.0\.0\.1;3306;', "127.0.0.1;$DbPort;"
        Set-Content -Encoding ASCII $_.FullName $c
    }
    Write-Ok 'Server configured'

    # ---------------------------------------------------------------- database
    $marker = Join-Path $Root '.database-ready'
    if (-not (Test-Path $marker)) {
        if (-not (Test-Path $DbDataDir)) {
            Write-Step 'Creating database...'
            $install = Find-MariaExe @('mariadb-install-db.exe', 'mysql_install_db.exe')
            & $install "--datadir=$DbDataDir" "--password=$DbRootPass" "--port=$DbPort" | Out-Host
            if ($LASTEXITCODE -ne 0) { throw 'Could not initialise the database.' }
        }
        Start-Database
        Write-Step 'Creating database user...'
        Invoke-Sql "CREATE USER IF NOT EXISTS 'mangos'@'localhost' IDENTIFIED BY 'mangos'; CREATE USER IF NOT EXISTS 'mangos'@'127.0.0.1' IDENTIFIED BY 'mangos'; GRANT ALL PRIVILEGES ON *.* TO 'mangos'@'localhost'; GRANT ALL PRIVILEGES ON *.* TO 'mangos'@'127.0.0.1'; FLUSH PRIVILEGES;"
        foreach ($f in Get-ChildItem $SqlDir -Filter *.sql) {
            Write-Step "Importing world database ($([math]::Round($f.Length/1MB)) MB, a few minutes)..."
            Import-SqlFile $f.FullName
        }
        New-Item -ItemType File $marker | Out-Null
        Write-Ok 'Database ready'
    } else {
        Write-Ok 'Database already set up'
    }

    # ---------------------------------------------------------------- maps
    $data = Join-Path (Split-Path (Find-ServerExe 'mangosd.exe') -Parent) 'data'
    New-Item -ItemType Directory -Force $data | Out-Null
    if (-not (Test-Path (Join-Path $data 'maps'))) {
        Write-Step 'Extracting DBC files and maps from your client (5-10 minutes)...'
        $ad = Find-ServerExe 'ad.exe'
        & $ad -i "$wow" -o "$data" | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'Map extraction failed.' }
        Write-Ok 'Maps extracted'
    } else { Write-Ok 'Maps already extracted' }

    if (-not (Test-Path (Join-Path $data 'vmaps'))) {
        Write-Step 'Extracting line-of-sight data (vmaps, 10-20 minutes)...'
        $vx = Find-ServerExe 'vmap_extractor.exe'
        & $vx -d (Join-Path $wow 'Data') -o "$data" | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'vmap extraction failed.' }
        New-Item -ItemType Directory -Force (Join-Path $data 'vmaps') | Out-Null
        $va = Find-ServerExe 'vmap_assembler.exe'
        & $va (Join-Path $data 'Buildings') (Join-Path $data 'vmaps') | Out-Host
        if ($LASTEXITCODE -ne 0) { throw 'vmap assembling failed.' }
        Remove-Item -Recurse -Force (Join-Path $data 'Buildings') -ErrorAction SilentlyContinue
        Write-Ok 'vmaps ready'
    } else { Write-Ok 'vmaps already extracted' }

    $mangosConf = Get-ChildItem -Recurse -File $ServerDir -Filter mangosd.conf | Select-Object -First 1
    if (-not (Test-Path (Join-Path $data 'mmaps'))) {
        Write-Host ''
        Write-Host '  Movement maps (mmaps) make monsters walk around walls instead of through them.' -ForegroundColor White
        Write-Host '  Building them takes roughly 30-90 minutes on your PC, but only once.' -ForegroundColor White
        $ans = Read-Host '  Build movement maps now? [Y/n]'
        if ($ans -eq '' -or $ans -match '^[yY]') {
            New-Item -ItemType Directory -Force (Join-Path $data 'mmaps') | Out-Null
            $mm = Find-ServerExe 'MoveMapGen.exe'
            $threads = [Math]::Max(1, [Environment]::ProcessorCount - 1)
            $cfg = Join-Path $PSScriptRoot 'config.json'
            $off = Join-Path $PSScriptRoot 'offmesh.txt'
            Push-Location $data
            & $mm --silent --configInputPath "$cfg" --offMeshInput "$off" --workdir "$($data -replace '\\', '/')/" --buildGameObjects --threads $threads | Out-Host
            $code = $LASTEXITCODE
            Pop-Location
            if ($code -ne 0) { throw 'Movement map generation failed.' }
            (Get-Content $mangosConf.FullName) -replace '^mmap\.enabled\s*=.*', 'mmap.enabled = 1' | Set-Content -Encoding ASCII $mangosConf.FullName
            Write-Ok 'Movement maps ready'
        } else {
            (Get-Content $mangosConf.FullName) -replace '^mmap\.enabled\s*=.*', 'mmap.enabled = 0' | Set-Content -Encoding ASCII $mangosConf.FullName
            Write-Warn2 'Skipped. Run SETUP.bat again any time to build them.'
        }
    } else { Write-Ok 'Movement maps already built' }

    # ---------------------------------------------------------------- client + shortcut
    Set-Realmlist $wow
    $addonSrc = Join-Path $Root 'addons'
    if (Test-Path $addonSrc) {
        $addonDst = Join-Path $wow 'Interface\AddOns'
        New-Item -ItemType Directory -Force $addonDst | Out-Null
        Copy-Item -Recurse -Force (Join-Path $addonSrc '*') $addonDst
        Write-Ok 'Zelda Controls addon installed (1 sword, 2 bow, 3 shield, 4 boomerang, 5 roll, tap Shift to lock on)'
    }
    Write-Ok 'Client pointed at your own PC (realmlist 127.0.0.1). Original saved as realmlist.wtf.original'
    try {
        $desktop = [Environment]::GetFolderPath('Desktop')
        $sh = New-Object -ComObject WScript.Shell
        $lnk = $sh.CreateShortcut((Join-Path $desktop 'Azeroth Solo.lnk'))
        $lnk.TargetPath = Join-Path $Root 'PLAY.bat'
        $lnk.WorkingDirectory = $Root
        $lnk.IconLocation = (Join-Path $wow 'WoW.exe') + ',0'
        $lnk.Save()
        Write-Ok 'Desktop shortcut "Azeroth Solo" created'
    } catch { Write-Warn2 'Could not create a desktop shortcut (not important).' }

    Stop-Database

    Write-Title 'Setup complete!'
    Write-Host '  Start the game with PLAY.bat (or the "Azeroth Solo" desktop shortcut).' -ForegroundColor White
    Write-Host '  Log in with   account: PLAYER   password: PLAYER' -ForegroundColor White
    Write-Host '  (GM account:  ADMINISTRATOR / ADMINISTRATOR)' -ForegroundColor DarkGray
}
catch {
    Write-Host ''
    Write-Host "  SETUP FAILED: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host '  Fix the problem above and run SETUP.bat again - it continues where it stopped.' -ForegroundColor Red
}
Write-Host ''
Read-Host '  Press Enter to close'
