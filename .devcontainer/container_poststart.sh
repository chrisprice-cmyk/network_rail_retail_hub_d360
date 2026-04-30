#!/bin/bash
# for template changes - run this manually unless you enjoy watching your changes disappear.

if [ \"${PWD##*/}\" != \"xDO-Template\" ]; then qx setup init-codespace; fi
printf "vscode\\nvscode\n\n" | vncpasswd && vncserver && xrandr -s 1920x1080 
source activate
grep -qxF 'source activate' /root/.bashrc || echo 'source activate' >> /root/.bashrc

# install ca and claude setup script
_DEVC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "${_DEVC_DIR}/install_ca_and_claude_sso.sh"
#not yet
#sf org login web -a QLABS -r https://qlabs-org.my.salesforce.com