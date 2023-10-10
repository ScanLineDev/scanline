#! /bin/bash
echo "👋🏼 Welcome to Scanline, so glad you're here!"
echo "⏳ Downloading requirements...."
curl -L --progress-bar -o scanline https://github.com/ScanLineDev/scanline/releases/download/v0.3.0-x86/scanline
chmod +x scanline
echo "🔐 We need your password to install the CLI in the right folder. (This is only used locally, we never see this.)"
read -s SUDO_PASSWORD
echo $SUDO_PASSWORD | sudo -S mv scanline /usr/local/bin/scanline
echo -e "\n"
echo "🗝 Last step - enter your OpenAI API key (this is only used locally, we never see this). To get your OpenAI API key, go here: https://platform.openai.com/account/api-keys "
read OPENAI_API_KEY
echo "export OPENAI_API_KEY=$OPENAI_API_KEY" >> ~/.bashrc
source ~/.bashrc
echo "
✅ All done with setup. 

== 🔍 How to use ScanLine ==

Code is sent directly to the OpenAI API with your OpenAI key (your code is only shared with OpenAI, not us)

"


echo -e "By default, \033[1mscanline\033[0m compares your current branch to the 'main' or 'master' branch. You can change the scope of review:
"

echo -e "\033[1mscanline --scope commit\033[0m     # Review your current changes, compared to the previous commit
"

echo -e "\033[1mscanline --scope branch\033[0m     # Review your current branch, compared to 'main' or 'master' branch (the default; you can also just run \033[1m'scanline'\033[0m)
"

echo -e "\033[1mscanline --scope repo\033[0m       # Review the entire repository

"

echo -e "🚀 To get started, cd into to any repo you'd like to review and run '\033[1mscanline\033[0m' 🚀"
