#!/bin/bash
# Script wrapper para ejecutar deploy.sh con logging

# El directorio donde está este script (y deploy.sh, deploy.log)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Ejecutar deploy.sh y redirigir su salida a deploy.log
# cd al directorio del script por si acaso el webhook no lo hace bien
cd "${SCRIPT_DIR}"
./deploy.sh >> "${SCRIPT_DIR}/deploy.log" 2>&1 