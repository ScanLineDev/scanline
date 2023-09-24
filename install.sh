#! /bin/bash
echo "👋🏼 Welcome to Scanline, so glad you're here!"
curl -Lso aicli https://github.com/ScanLineDev/scanline/releases/download/v1.0/aicli
chmod +x aicli
echo "🔐 We need your password to install the CLI in the right folder."
read -s SUDO_PASSWORD
echo $SUDO_PASSWORD | sudo -S mv aicli /usr/local/bin/scan
echo -e "\n"
echo "🗝 Last step - enter your OpenAI API key:"
read OPENAI_API_KEY
export OPENAI_API_KEY=$OPENAI_API_KEY
echo "✅ All done here. Run 'scan' on any branch you'd like to review. 🚀"
