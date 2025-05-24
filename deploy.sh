#!/bin/bash
cd /opt/rcqevents-server || exit

echo "--- Deploy RCQEvents: Iniciando ---"
# Asegurar que estamos en la rama main
git checkout main

# Traer todos los cambios del remoto
git fetch origin

# Forzar la rama local main a ser idéntica a origin/main
# Esto descarta cualquier cambio local o commit en el servidor que no esté en origin/main
git reset --hard origin/main

echo "Activando entorno virtual..."
source venv/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Reiniciando servicio..."
sudo systemctl restart rcqevents-server.service
echo "--- Deploy RCQEvents: Finalizado ---"

