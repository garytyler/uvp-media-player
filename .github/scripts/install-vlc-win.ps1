Set-Variable -Name VLC_VERSION -Value "3.0.11"
Set-Variable -Name VLC_INSTALLER -Value "~\Downloads\vlc-${VLC_VERSION}-win64.exe"
Set-Variable -Name VLC_DL_URL -Value "https://download.videolan.org/pub/vlc/${VLC_VERSION}/win64/vlc-${VLC_VERSION}-win64.exe"
Write-Host "Downloading VLC installer..."
Invoke-WebRequest -Method Get -OutFile "$VLC_INSTALLER" -Uri "$VLC_DL_URL"
Write-Host "Installing VLC..."
Start-Process -Wait $VLC_INSTALLER -ArgumentList '/L=1033 /S'
