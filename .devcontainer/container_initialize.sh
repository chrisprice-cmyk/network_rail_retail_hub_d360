#!/bin/bash
EXPORTED_GH_TOKEN=$(gh auth token)
echo -e "EXPORTED_GH_TOKEN=$EXPORTED_GH_TOKEN\nBRIX_USER_UID=$USER\nBRIX_USER_HOSTNAME=$(hostname)" > .devcontainer/.env
docker container prune -f
docker image prune -f 
docker volume prune -f
docker system prune -f
docker pull ghcr.io/sfdc-qbranch-emu/qbrix-base-container-quasar:latest
docker run -d --name jaeger -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 -p 4317:4317 -p 4318:4318 -p 5775:5775/udp -p 6831:6831/udp -p 6832:6832/udp -p 5778:5778 -p 16686:16686 -p 14268:14268 -p 14250:14250 -p 9411:9411 jaegertracing/all-in-one:latest || true 
rm -rf  .extensions || true
mkdir .extensions || true
curl -L https://$EXPORTED_GH_TOKEN:x-oauth-basic@github.com/sfdc-qbranch-emu/qbrixdev-vscode-ui/archive/main.zip -o .extensions/vscode-ui.zip
unzip .extensions/vscode-ui.zip -d .extensions/vscode-ui
