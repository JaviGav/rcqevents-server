#!/bin/bash
cd /opt/rcqevents-server || exit

# Activar entorno virtual
source venv/bin/activate

# Pull del repo
git pull origin master

# Instalar dependencias
pip install -r requirements.txt

# Reiniciar el servidor
sudo systemctl restart rcqevents-server.service

