#!/bin/bash
# set -e # Comentado temporalmente para las primeras pruebas de log

LOG_FILE="/opt/rcqevents-server/deploy.log"
WHOAMI_USER=$(whoami) # Capturar usuario
GIT_SAFE_DIR_CONFIG="-c safe.directory=/opt/rcqevents-server"

# Intento 1: Sobrescribir el log (creándolo si no existe)
/bin/echo "--- deploy.sh INICIADO como ${WHOAMI_USER} (Intentando Git con config local) ---" > "${LOG_FILE}"

# Intento 2: Añadir al log, verificando el éxito
if /bin/echo "--- Prueba de escritura adicional OK ---" >> "${LOG_FILE}"; then
    # Si la escritura fue exitosa, activa set -e para el resto del script
    set -e
    echo "Log funcionando. Continuando con el script..." >> "${LOG_FILE}"
else
    # Si la escritura falló, esto irá al stdout/stderr del webhook
    echo "FALLO CRÍTICO: No se pudo escribir en ${LOG_FILE} como ${WHOAMI_USER}"
    exit 1 # Salir con error
fi

# A partir de aquí, set -e está activo
cd /opt/rcqevents-server || { echo "FALLO: cd /opt/rcqevents-server" >> ${LOG_FILE}; exit 1; }
echo "Directorio actual: $(pwd)" >> ${LOG_FILE}

echo "Intentando operaciones de Git..." >> ${LOG_FILE}
echo "Salida de 'git remote -v':" >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} remote -v >> ${LOG_FILE} 2>&1 || echo "Advertencia: 'git remote -v' falló" >> ${LOG_FILE}

echo "Asegurando rama main..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} checkout main >> ${LOG_FILE} 2>&1 || { echo "FALLO: git checkout main" >> ${LOG_FILE}; exit 1; }

echo "Obteniendo cambios remotos (fetch)..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} fetch origin >> ${LOG_FILE} 2>&1 || { echo "FALLO: git fetch origin" >> ${LOG_FILE}; exit 1; }

echo "Reseteando a origin/main (reset --hard)..." >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} reset --hard origin/main >> ${LOG_FILE} 2>&1 || { echo "FALLO: git reset --hard origin/main" >> ${LOG_FILE}; exit 1; }
echo "Operaciones de Git completadas. Último commit en el servidor:" >> ${LOG_FILE}
git ${GIT_SAFE_DIR_CONFIG} log -1 --pretty=format:"%h - %s (%cr) <%an>" >> ${LOG_FILE} 2>&1

echo "Activando entorno virtual..." >> ${LOG_FILE}
source venv/bin/activate || { echo "FALLO: source venv/bin/activate" >> ${LOG_FILE}; exit 1; }

echo "Instalando dependencias..." >> ${LOG_FILE}
pip install -r requirements.txt >> ${LOG_FILE} 2>&1 || { echo "FALLO: pip install -r requirements.txt" >> ${LOG_FILE}; exit 1; }

echo "Reiniciando servicio..." >> ${LOG_FILE}
sudo systemctl restart rcqevents-server.service >> ${LOG_FILE} 2>&1 || { echo "FALLO: sudo systemctl restart rcqevents-server.service" >> ${LOG_FILE}; exit 1; }
echo "--- Log RCQEvents: Finalizado deploy.sh ---" >> ${LOG_FILE}

exit 0

