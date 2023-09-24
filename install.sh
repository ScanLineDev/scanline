#! /bin/bash
echo "👋🏼 Welcome to Scanline, so glad you're here!"
echo "⏳ Downloading requirements...."
curl -L --progress-bar -o aicli https://github.com/ScanLineDev/scanline/releases/download/v0.1/aicli
chmod +x aicli
echo "🔐 We need your password to install the CLI in the right folder. (This is only used locally, we never see this.)"
read -s SUDO_PASSWORD
echo $SUDO_PASSWORD | sudo -S mv aicli /usr/local/bin/scan
echo -e "\n"
echo "🗝 Last step - enter your OpenAI API key (this is only used locally, we never see this.):"
read OPENAI_API_KEY
export OPENAI_API_KEY=$OPENAI_API_KEY
echo "✅ All done here. Run 'scan' on any branch you'd like to review. 🚀"
