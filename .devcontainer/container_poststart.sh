#!/bin/bash
# for template changes - run this manually unless you enjoy watching your changes disappear.
if [ \"${PWD##*/}\" != \"xDO-Template\" ]; then qx setup init-codespace; fi
printf "vscode\\nvscode\n\n" | vncpasswd && vncserver && xrandr -s 1920x1080 
source activate
#not yet
#sf org login web -a QLABS -r https://qlabs-org.my.salesforce.com