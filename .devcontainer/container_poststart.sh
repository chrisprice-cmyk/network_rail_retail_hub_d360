#!/bin/bash
# for template changes - run this manually unless you enjoy watching your changes disappear.
if [ \"${PWD##*/}\" != \"xDO-Template\" ]; then qx setup init-codespace; fi
xrandr -s 1920x1080 
pip install protobuf==5.28.1 --force --no-deps || true
#not yet
#sf org login web -a QLABS -r https://qlabs-org.my.salesforce.com