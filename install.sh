#! /bin/bash
echo "👋🏼 Welcome to AI CLI, glad you're here!"
curl -O https://raw.githubusercontent.com/stephenkfrey/ailinter/reviewme/dist/aicli
echo "🔐 We need your password to install the CLI in the right folder."
chmod +x aicli
sudo mv aicli /usr/local/bin/ai
echo "✅ All done here. Run 'ai' to get started. 🚀"