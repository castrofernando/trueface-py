# !/usr/bin/env bash

echo "Atualizando repositorios"
sudo apt-get update && sudo apt-get upgrade -y

echo "Instalando dependencias"
sudo apt-get install curl -y
sudo apt install python3-pip -y

sudo apt-get install python3-h5py -y
sudo apt-get install libopenjp2-7 libtiff5 libatlas-base-dev -y
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng-dev -y
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt-get install libxvidcore-dev libx264-dev -y
sudo apt-get install libgtk2.0-dev libgtk-3-dev -y
sudo apt-get install libatlas-base-dev gfortran -y
sudo apt-get install zbar-tools -y

echo "Instalando pacotes do python"
sudo pip install Flask 
sudo pip install imutils 
sudo pip install -U numpy 
sudo pip install opencv_contrib_python==4.5.5.62 
sudo pip install psutil 
sudo pip install pyzbar 
sudo pip install requests 

echo "Instalação finalizada"
