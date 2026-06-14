#!/bin/bash
# for template changes - run this manually unless you enjoy watching your changes disappear.

if [ \"${PWD##*/}\" != \"xDO-Template\" ]; then qx setup init-codespace; fi
printf "vscode\\nvscode\n\n" | vncpasswd && vncserver && xrandr -s 1920x1080 
source activate
grep -qxF 'source activate' /root/.bashrc || echo 'source activate' >> /root/.bashrc

# install ca and claude setup script
_DEVC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${_DEVC_DIR}/install_ca_and_claude_sso.sh"

TOKEN=$EXPORTED_GH_TOKEN && \
echo "@sfdc-qbranch-emu:registry=https://npm.pkg.github.com" >> ~/.npmrc && \
echo "//npm.pkg.github.com/:_authToken=${TOKEN}" >> ~/.npmrc && \
echo "✓ ~/.npmrc configured for @sfdc-qbranch-emu"

npx @sfdc-qbranch-emu/mcp-brix --install-skills