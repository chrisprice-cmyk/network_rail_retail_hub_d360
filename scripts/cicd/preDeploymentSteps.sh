#!/bin/bash
echo 'Running pre-deployment CICD steps...'
./scripts/bash/installPackages.sh

./scripts/bash/uploadImages.sh
