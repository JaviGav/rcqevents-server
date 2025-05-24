# RCQEvents Server

<!-- Test webhook logging again -->

Servidor backend para la aplicación RCQEvents desarrollado con Flask.

## Requisitos

- Python 3.8 o superior
- PostgreSQL
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/JaviGav/rcqevents-server.git
cd rcqevents-server
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Desarrollo

Para ejecutar el servidor en modo desarrollo:
```bash
flask run
```

El servidor estará disponible en `http://localhost:5000`

## Producción

Para ejecutar en producción usando Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Estructura del Proyecto

```
rcqevents-server/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── migrations/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── config.py
├── requirements.txt
└── run.py
```

## Licencia

Este proyecto está bajo la Licencia MIT. 