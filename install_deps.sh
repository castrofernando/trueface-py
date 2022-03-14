# !/usr/bin/env bash

echo "Atualizando repositorios"
sudo apt-get update && sudo apt-get upgrade

echo "Instalando dependencias"
sudo apt-get install curl
sudo apt install python3-pip

echo "Instalando libs do python3"
sudo pip install -r requirements.txt

echo "Instalação finalizada"