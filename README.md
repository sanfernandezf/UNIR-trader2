# UNIR Trader - Sistema de Predicción de Bitcoin

Aplicación web didáctica para el análisis y predicción del precio de Bitcoin usando múltiples modelos de Machine Learning.

## Características

- 📊 Descarga de datos históricos de Binance (BTC/USD)
- 🔧 Ingeniería de características: RSI, MACD, Bandas de Bollinger
- 🤖 Múltiples modelos ML en paralelo:
  - LSTM (Long Short-Term Memory)
  - Random Forest
  - XGBoost
  - Gradient Boosting
- 📈 Backtesting completo con métricas:
  - Rentabilidad
  - Ratio de Sharpe
  - Matriz de confusión
  - Drawdown máximo
- 🎓 Interfaz didáctica que explica cada paso del proceso

## Estructura del Proyecto

```
UNIR-trader/
├── backend/          # API y lógica de ML
│   └── app/
│       ├── data/     # Descarga de datos de Binance
│       ├── features/ # Ingeniería de características
│       ├── models/   # Modelos de ML
│       ├── backtesting/ # Sistema de backtesting
│       └── api/      # Endpoints REST
└── frontend/         # Interfaz web React
```

## Configuración

1. Clonar el repositorio:
```bash
git clone https://github.com/sanfernandezf/UNIR-trader2.git
cd UNIR-trader2
```

2. Configurar variables de entorno:
```bash
cd backend
cp .env.example .env
# Editar .env con tus credenciales de Binance
```

3. Instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

4. Instalar dependencias del frontend:
```bash
cd frontend
npm install
```

## Uso

### Opción 1: Scripts de inicio rápido (Recomendado)

En terminales separadas:

```bash
# Terminal 1 - Backend
./start_backend.sh

# Terminal 2 - Frontend
./start_frontend.sh
```

### Opción 2: Docker Compose (Producción)

```bash
docker-compose up -d
```

La aplicación estará disponible en `http://localhost:3001`

### Opción 3: Manual

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### Opción 4: Script Python directo

```bash
cd backend
source venv/bin/activate
python ../example_usage.py
```

## Datos de Entrenamiento

- **Entrenamiento**: 4 años de datos históricos
- **Pruebas**: 1 año de datos

## Documentación Adicional

- [Guía de Instalación Detallada](INSTALL.md)
- [Ejemplo de Uso con Python](example_usage.py)
- [Documentación de la API](http://localhost:8000/docs) (después de iniciar el backend)

## Archivos y Scripts Útiles

- `start_backend.sh`: Script para iniciar el backend automáticamente
- `start_frontend.sh`: Script para iniciar el frontend automáticamente
- `example_usage.py`: Ejemplo de uso del sistema sin API
- `docker-compose.yml`: Configuración de Docker para despliegue

## Endpoints de la API

### Datos
- `POST /api/v1/data/download` - Descargar datos de Binance
- `GET /api/v1/data/status` - Estado de los datos

### Características
- `POST /api/v1/features/engineer` - Generar características técnicas

### Modelos
- `POST /api/v1/models/train` - Entrenar modelos
- `GET /api/v1/models/status` - Estado de los modelos

### Backtesting
- `POST /api/v1/backtest/run` - Ejecutar backtesting
- `GET /api/v1/backtest/results` - Ver resultados

### Pipeline
- `POST /api/v1/pipeline/run` - Ejecutar todo el pipeline

## Despliegue en Producción

Para desplegar en www.cubelabs.co/UNIR2:

1. Configurar nginx como proxy reverso
2. Usar gunicorn/uvicorn con múltiples workers
3. Construir el frontend con `npm run build`
4. Configurar SSL con Let's Encrypt
5. Usar Docker Compose para orquestación

Ver [INSTALL.md](INSTALL.md) para más detalles.

## Licencia

MIT
