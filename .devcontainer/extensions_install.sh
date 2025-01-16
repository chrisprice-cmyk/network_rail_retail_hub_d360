#!/bin/bash

if [ -z "$EXPORTED_GH_TOKEN" ]; then
  EXPORTED_GH_TOKEN=$(gh auth token) || true
fi

rm -rf  .extensions || true
mkdir .extensions || true

#fresh pull
curl -L https://$EXPORTED_GH_TOKEN:x-oauth-basic@github.com/sfdc-qbranch-emu/qbrixdev-vscode-ui/archive/main.zip -o .extensions/vscode-ui.zip || true
unzip .extensions/vscode-ui.zip -d .extensions/vscode-ui || true

FILE=.extensions/vscode-ui.zip
if [ -f "$FILE" ]; then
  npm install --global npm i @vscode/vsce || true
  npm install --global typescript  || true
  cd .extensions/vscode-ui/QBrixDev-VSCode-UI-main || true
  npm install npm-run-all || true
  cd webview
  npm install
  cd ..
  npm install
  npm run vscode:prepublish
  vsce package --out ./qbrixdev-vscode-ui.vsix
  code --install-extension ./qbrixdev-vscode-ui.vsix --verbose
fi