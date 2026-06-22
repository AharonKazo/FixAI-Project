#!/bin/bash

sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common git

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

sudo usermod -aG docker ubuntu

cd /home/ubuntu
git clone https://github.com/oranmeir-git/FixAI.git
cd FixAI

sudo docker compose up -d --build
