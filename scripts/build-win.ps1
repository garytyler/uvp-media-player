$directions = "Run script from project root using `'$MyInvocation.MyCommand.Name`'"

$app_module = "src"
$_name = 'player'


### Check paths ###

$working_dir = "$PWD"

if (!(Test-Path -Path "$working_dir\$app_module")) {
    $msg = "`'$app_module`' module not found in `'$PSScriptRoot`'. $directions"
    Write-Error -Message $msg -ErrorAction Stop -Category ObjectNotFound -Exception [System.Management.Automation.ItemNotFoundException]
}
elseif ("$working_dir\$app_module" -match '.py$') {
    $app_script = "$working_dir\$app_module"
}
elseif (Test-Path -Path $working_dir\$app_module\__main__.py) {
    $app_script = "$working_dir\$app_module\__main__.py"
}
else {
    $msg = "`'$target_path`' is not a python script or module"
    Write-Error -Message $msg -ErrorAction Stop -Category ObjectNotFound -Exception [System.Management.Automation.ItemNotFoundException]
}


### Prep ###

Write-Output "Prep: Removing existing `'dist/`' contents"
Remove-Item "$working_dir\dist" -Force  -Recurse -ErrorAction SilentlyContinue
Write-Output "Prep: Removing existing `'build/`' contents"
Remove-Item "$working_dir\build" -Force  -Recurse -ErrorAction SilentlyContinue


### Build ###

# Define default args
$default_args = @(
    # '--debug'
    # '--console'
    '--windowed'
    '--log-level=INFO'
    '--noconfirm'
    '--clean'
    '--onedir'
    '--name=player'
    '--hidden-import=PyQt5.QtNetwork'
    "--paths=${env:PROGRAMFILES}/VideoLAN/VLC/"
    "--add-data=./media/*;media"
    "--add-data=./resources/*;resources"
    "--add-binary=${env:PROGRAMFILES}/VideoLAN/VLC/plugins/*;plugins"
    "--add-binary=${env:PROGRAMFILES}/VideoLAN/VLC/libvlc.dll;."
)

# Append passed args and application script path to default args
$pyinstaller_args = $default_args + $args + "$app_script"

Write-Output "Building `'$_name`' with script `'$app_script`' and pyinstaller arguments: [$pyinstaller_args]"

Invoke-Command { pyinstaller @args } -args $pyinstaller_args

### Cleanup ###

Write-Output "Clean-up: Removing `'*.pyo`' files from project directory"
Get-ChildItem -Path "*.pyo" -Recurse  -ErrorAction SilentlyContinue -File | Remove-Item
