#!/bin/bash
set -e # Salir inmediatamente si un comando falla

LOG_FILE="/opt/rcqevents-server/deploy.log"
WHOAMI_USER=$(whoami) # Capturar usuario
GIT_SAFE_DIR_CONFIG="-c safe.directory=/opt/rcqevents-server"

# Sobrescribir el log (creándolo si no existe)
/bin/echo "--- deploy.sh INICIADO como ${WHOAMI_USER} (Git con config local) ---" > "${LOG_FILE}"
/bin/echo "--- Log activado, set -e está activo ---" >> "${LOG_FILE}"

cd /opt/rcqevents-server || { echo "FALLO: cd /opt/rcqevents-server" >> ${LOG_FILE}; exit 1; }
echo "Directorio actual: $(pwd)" >> ${LOG_FILE}

echo "Intentando operaciones de Git..." >> ${LOG_FILE}
echo "Salida de 'git remote -v':" >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} remote -v >> ${LOG_FILE} 2>&1 || echo "Advertencia: 'git remote -v' falló" >> ${LOG_FILE}

echo "Asegurando rama main..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} checkout main >> ${LOG_FILE} 2>&1
echo "Obteniendo cambios remotos (fetch)..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} fetch origin >> ${LOG_FILE} 2>&1
echo "Reseteando a origin/main (reset --hard)..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} reset --hard origin/main >> ${LOG_FILE} 2>&1
echo "Operaciones de Git completadas. Último commit en el servidor:" >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} log -1 --pretty=format:"%h - %s (%cr) <%an>" >> ${LOG_FILE} 2>&1

echo "Activando entorno virtual..." >> ${LOG_FILE}
source venv/bin/activate
echo "Instalando dependencias..." >> ${LOG_FILE}
pip install -r requirements.txt >> ${LOG_FILE} 2>&1

echo "Reiniciando servicio..." >> ${LOG_FILE}
sudo systemctl restart rcqevents-server.service >> ${LOG_FILE} 2>&1
echo "--- Log RCQEvents: Finalizado deploy.sh ---" >> ${LOG_FILE}

exit 0

