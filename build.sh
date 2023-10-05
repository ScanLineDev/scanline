pyinstaller scanline-build.spec
echo "🔐 Scanline needs your permission to install into '/usr/local/bin/scanline'. (This is only used locally, we never see this.)"
sudo mv dist/scanline /usr/local/bin/scanline