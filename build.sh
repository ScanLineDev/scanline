pyinstaller scanline-build.spec
echo "🔐 We need your password to install the CLI in the right folder. (This is only used locally, we never see this.)"

sudo mv dist/scanline /usr/local/bin/scanline