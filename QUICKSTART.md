# UNIR Trader - Quick Start Guide

## Desarrollo Local (Puerto 3010)

### Opción 1: Scripts automáticos

```bash
# Terminal 1 - Backend
./start_backend.sh

# Terminal 2 - Frontend
./start_frontend.sh
```

Accede a: **http://localhost:3010**

### Opción 2: Manual

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (en otra terminal)
cd frontend
npm install
npm start
```

## Producción en cubelabs.co/UNIR2

Ver guía completa: [DEPLOYMENT.md](DEPLOYMENT.md)

Resumen rápido:

```bash
# En el servidor
cd /var/www/unir-trader
git pull origin main

# Backend con PM2
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart unir-trader-api

# Frontend
cd frontend
npm install
npm run build
sudo systemctl reload nginx
```

Accede a: **https://cubelabs.co/UNIR2**

## Documentación

- [README.md](README.md) - Visión general del proyecto
- [INSTALL.md](INSTALL.md) - Guía de instalación detallada
- [DEPLOYMENT.md](DEPLOYMENT.md) - Despliegue en producción

## URLs Importantes

### Desarrollo
- Frontend: http://localhost:3010
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Producción
- Frontend: https://cubelabs.co/UNIR2
- Backend API: https://cubelabs.co/UNIR2/api/v1/

## Estructura de Archivos

```
UNIR-trader2/
├── backend/              # Python + FastAPI
│   ├── app/
│   │   ├── data/        # Descarga de Binance
│   │   ├── features/    # Ingeniería de características
│   │   ├── models/      # ML Models
│   │   ├── backtesting/ # Backtesting
│   │   └── api/         # REST API
│   └── requirements.txt
├── frontend/             # React
│   ├── src/
│   └── package.json
├── start_backend.sh      # Script inicio backend
├── start_frontend.sh     # Script inicio frontend
├── nginx-cubelabs.conf   # Config Nginx producción
├── DEPLOYMENT.md         # Guía de despliegue
└── example_usage.py      # Ejemplo Python standalone
```

## Scripts Útiles

| Script | Descripción |
|--------|-------------|
| `./start_backend.sh` | Inicia backend en desarrollo |
| `./start_frontend.sh` | Inicia frontend en desarrollo |
| `python example_usage.py` | Ejecuta pipeline completo sin API |
| `docker-compose up -d` | Inicia con Docker |

## Comandos Frecuentes

```bash
# Ver logs del backend (producción)
pm2 logs unir-trader-api

# Reiniciar backend
pm2 restart unir-trader-api

# Actualizar código
git pull origin main

# Reconstruir frontend
cd frontend && npm run build

# Ver estado de servicios
pm2 status
sudo systemctl status nginx
```

## Soporte

- GitHub: https://github.com/sanfernandezf/UNIR-trader2
- Issues: https://github.com/sanfernandezf/UNIR-trader2/issues
