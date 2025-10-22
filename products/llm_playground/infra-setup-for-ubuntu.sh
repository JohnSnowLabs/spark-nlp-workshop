#!/bin/bash

echo '1. Setting up ubuntu GPU drivers'
sudo apt update -y > /dev/null 2>&1 && sudo apt upgrade -y > /dev/null 2>&1

sudo apt install ubuntu-drivers-common -y > /dev/null 2>&1

driver=$(ubuntu-drivers devices 2>/dev/null | grep "recommended" | sed -n 's/driver   : \(.*\) - distro.*/\1/p')

sudo apt install -y ${driver} > /dev/null 2>&1
echo '√ done'

echo '2. Setting up containerization dependencies'
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update -y > /dev/null 2>&1
sudo apt install -y nvidia-container-toolkit nvtop > /dev/null 2>&1
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common > /dev/null 2>&1
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - > /dev/null 2>&1
sudo add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"  > /dev/null 2>&1
sudo apt update -y > /dev/null 2>&1
echo '√ done'
echo '3. Installing docker-ce'
sudo apt install docker-ce -y > /dev/null 2>&1
sudo usermod -aG docker $USER

echo '{
  "default-runtime": "nvidia",
   "runtimes": {
      "nvidia": {
          "path": "/usr/bin/nvidia-container-runtime",
          "runtimeArgs": []
      }
  }
}' | sudo tee /etc/docker/daemon.json  > /dev/null 2>&1
echo '√ done'
echo '4. rebooting your system'
sleep 5
sudo reboot