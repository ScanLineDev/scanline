#! /bin/bash
echo "👋🏼 Welcome to AI CLI, glad you're here!"
echo "🔐 We need your password to install the CLI in the right folder."
curl -s -o aicli https://github.com/scottfits/aicli/releases/download/v0.2/aicli
chmod +x aicli
sudo mv aicli /usr/local/bin/ai
echo "✅ All done here. Run 'ai' to get started. 🚀"