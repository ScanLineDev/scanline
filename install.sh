#! /bin/bash
echo "👋🏼 Welcome to Scanline, so glad you're here!"
echo "🔐 We need your password to install the CLI in the right folder."
curl -Lso aicli https://github.com/scottfits/aicli/releases/download/v0.3/aicli
chmod +x aicli
sudo mv aicli /usr/local/bin/scan
echo "🗝 Last step - enter your OpenAI API key:"
read OPENAI_API_KEY
export OPENAI_API_KEY=$OPENAI_API_KEY
echo "✅ All done here. Run 'scan' to get started. 🚀"
