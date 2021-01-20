#!/usr/bin/env bash

VLC_VERSION="3.0.11"
VLC_DMG_FILE_PATH="$HOME/Downloads/vlc-${VLC_VERSION}.dmg"
VLC_DOWNLOAD_URL="https://download.videolan.org/pub/vlc/${VLC_VERSION}/macosx/vlc-${VLC_VERSION}.dmg"
curl --output $VLC_DMG_FILE_PATH $VLC_DOWNLOAD_URL
VLC_VOLUME=$(hdiutil attach $VLC_DMG_FILE_PATH | grep /Volumes | sed 's/.*\/Volumes\//\/Volumes\//')
APP_FILE_NAME="VLC.app"
echo "Copying $APP_FILE_NAME to /Applications ..."
sudo cp -rf "$VLC_VOLUME/VLC.app" /Applications
hdiutil detach "$VLC_VOLUME"
