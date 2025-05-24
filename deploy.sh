#!/bin/bash
# Salir inmediatamente si un comando falla
set -e 

LOG_FILE="/opt/rcqevents-server/deploy.log"

# Limpiar el log anterior para ver solo la última ejecución
echo "" > ${LOG_FILE}
chmod 666 ${LOG_FILE} # Asegurar que se pueda escribir

echo "--- Log RCQEvents: Iniciando deploy.sh (ejecutado como $(whoami)) ---" >> ${LOG_FILE} || { echo "FALLO CRÍTICO: No se pudo escribir en el archivo de log inicial: ${LOG_FILE}"; exit 1; }

cd /opt/rcqevents-server || { echo "FALLO: cd /opt/rcqevents-server" >> ${LOG_FILE}; exit 1; }
echo "Directorio actual: $(pwd)" >> ${LOG_FILE}

echo "Intentando operaciones de Git..." >> ${LOG_FILE}
echo "Salida de 'git remote -v':" >> ${LOG_FILE}
git remote -v >> ${LOG_FILE} 2>&1 || echo "Advertencia: 'git remote -v' falló" >> ${LOG_FILE}

echo "Asegurando rama main..." >> ${LOG_FILE}
git checkout main >> ${LOG_FILE} 2>&1 || { echo "FALLO: git checkout main" >> ${LOG_FILE}; exit 1; }

echo "Obteniendo cambios remotos (fetch)..." >> ${LOG_FILE}
git fetch origin >> ${LOG_FILE} 2>&1 || { echo "FALLO: git fetch origin" >> ${LOG_FILE}; exit 1; }

echo "Reseteando a origin/main (reset --hard)..." >> ${LOG_FILE}
git reset --hard origin/main >> ${LOG_FILE} 2>&1 || { echo "FALLO: git reset --hard origin/main" >> ${LOG_FILE}; exit 1; }
echo "Operaciones de Git completadas. Último commit en el servidor:" >> ${LOG_FILE}
git log -1 --pretty=format:"%h - %s (%cr) <%an>" >> ${LOG_FILE} 2>&1

echo "Activando entorno virtual..." >> ${LOG_FILE}
source venv/bin/activate || { echo "FALLO: source venv/bin/activate" >> ${LOG_FILE}; exit 1; }

echo "Instalando dependencias..." >> ${LOG_FILE}
pip install -r requirements.txt >> ${LOG_FILE} 2>&1 || { echo "FALLO: pip install -r requirements.txt" >> ${LOG_FILE}; exit 1; }

echo "Reiniciando servicio..." >> ${LOG_FILE}
sudo systemctl restart rcqevents-server.service >> ${LOG_FILE} 2>&1 || { echo "FALLO: sudo systemctl restart rcqevents-server.service" >> ${LOG_FILE}; exit 1; }
echo "--- Log RCQEvents: Finalizado deploy.sh ---" >> ${LOG_FILE}

