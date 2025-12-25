#!/bin/bash
EXPORTED_GH_TOKEN=$(gh auth token)
echo -e "EXPORTED_GH_TOKEN=$EXPORTED_GH_TOKEN\nBRIX_USER_UID=$USER\nBRIX_USER_HOSTNAME=$(hostname)" > .devcontainer/.env
docker container prune -f
docker image prune -f 
docker volume prune -f
docker system prune -f
# Start Jaeger
docker pull ghcr.io/sfdc-qbranch-emu/qbrix-base-container-quasar:latest
docker run -d --name jaeger -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 -p 4317:4317 -p 4318:4318 -p 5775:5775/udp -p 6831:6831/udp -p 6832:6832/udp -p 5778:5778 -p 16686:16686 -p 14268:14268 -p 14250:14250 -p 9411:9411 jaegertracing/all-in-one:latest || true 
# Start MCP Core
docker pull ghcr.io/sfdc-qbranch-emu/qbrix-mcp-core-container:latest
docker run -d --name brix-mcp -e PORT=7200 -p 7200:7200 ghcr.io/sfdc-qbranch-emu/qbrix-mcp-core-container:latest || true

# Download AgentForce Assistant Universal VSIX to .plugins folder
rm -rf .plugins || true
mkdir .plugins || true


echo "Downloading AgentForce Assistant Universal VSIX..."
gh release download v0.0.1 \
    --repo sfdc-qbranch-emu/sf.af.demoassist.plugin \
    --pattern "agentforce-assistant-universal.vsix" \
    --dir .plugins

# Verify download
if [ -f ".plugins/agentforce-assistant-universal.vsix" ] && [ -s ".plugins/agentforce-assistant-universal.vsix" ]; then
    echo "AgentForce Assistant Universal VSIX file downloaded successfully ($(du -h .plugins/agentforce-assistant-universal.vsix | cut -f1))"
else
    echo "Warning: Failed to download AgentForce Assistant Universal VSIX file"
fi

echo "Downloading Qbrix Dev Plugin Universal VSIX..."
gh release download v1.0.0 \
    --repo sfdc-qbranch-emu/QBrixDev-VSCode-UI \
    --pattern "qbrixdev-vscode-universal.vsix" \
    --dir .plugins

# Verify download
if [ -f ".plugins/qbrixdev-vscode-universal.vsix" ] && [ -s ".plugins/qbrixdev-vscode-universal.vsix" ]; then
    echo "Qbrix Dev Plugin UniversalVSIX file downloaded successfully ($(du -h .plugins/qbrixdev-vscode-universal.vsix | cut -f1))"
else
    echo "Warning: Failed to download Qbrix Dev Plugin Universal VSIX file"
fi
