
$target_name = 'player'
$module_name = 'src'
$project_root = $PSScriptRoot

if (!(Test-Path -Path "$project_root\$module_name")) {
    $msg = "`'$module_name`' not found in script root `'$project_root`'"
    Write-Error -Message $msg -ErrorAction Stop -Category ObjectNotFound -Exception [System.Management.Automation.ItemNotFoundException]
}
elseif ("$project_root\$module_name" -match '.py$') {
    $script_path = "$project_root\$module_name"
}
elseif (Test-Path -Path $project_root\$target_name\__main__.py) {
    $script_path = "$project_root\$module_name\__main__.py"
}
else {
    $msg = "`'$target_path`' is not a python script or module"
    Write-Error -Message $msg -ErrorAction Stop -Category ObjectNotFound -Exception [System.Management.Automation.ItemNotFoundException]
}

Write-Output "Building `'$target_name`' with script `'$script_path`'"

Invoke-Command { pyinstaller @args } -args @(
    # '--windowed'
    '--debug'
    '--log-level=DEBUG'
    '--console'
    '--noconfirm'
    '--clean'
    '--onedir'
    '--name=player'
    '--hidden-import=PyQt5.QtNetwork'
    "--paths=${env:PROGRAMFILES}/VideoLAN/VLC/"
    "--add-data=./media/*;media"
    "--add-binary=${env:PROGRAMFILES}/VideoLAN/VLC/plugins/*;plugins"
    "--add-binary=${env:PROGRAMFILES}/VideoLAN/VLC/libvlc.dll;."
    "$script_path"
)