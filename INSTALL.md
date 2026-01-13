# Guía de Instalación - UNIR Trader

Esta guía te ayudará a instalar y ejecutar el sistema de predicción de Bitcoin.

## Requisitos Previos

- Python 3.8 o superior
- Node.js 14 o superior
- npm o yarn
- Git

## Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone https://github.com/sanfernandezf/UNIR-trader2.git
cd UNIR-trader2
```

### 2. Configurar Backend

#### Opción A: Usando el script automático (Linux/Mac)

```bash
./start_backend.sh
```

#### Opción B: Manual

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno (opcional, ya están en .env)
cp .env.example .env
# Editar .env si es necesario

# Iniciar servidor
uvicorn app.main:app --reload
```

El backend estará disponible en: `http://localhost:8000`
Documentación de la API: `http://localhost:8000/docs`

### 3. Configurar Frontend

#### Opción A: Usando el script automático (Linux/Mac)

En otra terminal:

```bash
./start_frontend.sh
```

#### Opción B: Manual

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

El frontend estará disponible en: `http://localhost:3000`

## Uso de la Aplicación

### Interfaz Web

1. Abre tu navegador en `http://localhost:3000`
2. Haz clic en "Ejecutar Pipeline Completo" para ejecutar todo el proceso
3. O ejecuta cada paso individualmente:
   - Paso 1: Descarga de datos de Binance
   - Paso 2: Ingeniería de características
   - Paso 3: Entrenamiento de modelos
   - Paso 4: Backtesting

### API REST

También puedes usar la API directamente:

```bash
# Ejecutar pipeline completo
curl -X POST http://localhost:8000/api/v1/pipeline/run

# Descargar datos
curl -X POST http://localhost:8000/api/v1/data/download \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "lookback_days": 1825}'

# Generar características
curl -X POST http://localhost:8000/api/v1/features/engineer

# Entrenar modelos
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Content-Type: application/json" \
  -d '{"parallel": true}'

# Ejecutar backtesting
curl -X POST http://localhost:8000/api/v1/backtest/run

# Ver resultados
curl http://localhost:8000/api/v1/backtest/results
```

## Estructura del Proyecto

```
UNIR-trader2/
├── backend/
│   ├── app/
│   │   ├── data/           # Descarga de datos de Binance
│   │   ├── features/       # Ingeniería de características
│   │   ├── models/         # Modelos de ML
│   │   ├── backtesting/    # Sistema de backtesting
│   │   ├── api/            # Endpoints REST
│   │   └── main.py         # Aplicación FastAPI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js          # Componente principal
│   │   └── ...
│   └── package.json
├── start_backend.sh        # Script de inicio backend
├── start_frontend.sh       # Script de inicio frontend
└── README.md
```

## Características Principales

### Backend (Python + FastAPI)

- **Descarga de datos**: Obtiene datos históricos de Binance
- **Ingeniería de características**: Calcula RSI, MACD, Bollinger Bands, etc.
- **Modelos ML**: Random Forest, XGBoost, LSTM
- **Entrenamiento paralelo**: Entrena múltiples modelos simultáneamente
- **Backtesting**: Evalúa rendimiento con métricas financieras

### Frontend (React)

- **Interfaz didáctica**: Explica cada paso del proceso
- **Visualización de resultados**: Muestra métricas y comparaciones
- **Paso a paso**: Permite ejecutar cada fase individualmente
- **Pipeline completo**: Ejecuta todo el proceso automáticamente

## Solución de Problemas

### Error: "Module not found"

Asegúrate de haber instalado todas las dependencias:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Error: "Port already in use"

Si el puerto 8000 o 3000 ya está en uso, puedes cambiarlos:

```bash
# Backend (puerto diferente)
uvicorn app.main:app --reload --port 8001

# Frontend (puerto diferente)
PORT=3001 npm start
```

### Error de conexión con Binance

Verifica que:
1. Tienes conexión a internet
2. Las credenciales en `.env` son correctas
3. Las credenciales tienen permisos de lectura

## Notas de Seguridad

- **IMPORTANTE**: El archivo `.env` contiene credenciales sensibles y NO debe compartirse
- Las credenciales de Binance deben tener solo permisos de **lectura**
- En producción, usa variables de entorno del sistema en lugar de archivos .env

## Despliegue en Producción

Para desplegar en www.cubelabs.co/UNIR2:

1. Configura el servidor web (nginx/apache)
2. Usa gunicorn/uvicorn para el backend
3. Construye el frontend: `npm run build`
4. Sirve el frontend desde el directorio `build/`
5. Configura HTTPS con certificados SSL

## Soporte

Para problemas o preguntas:
- GitHub Issues: https://github.com/sanfernandezf/UNIR-trader2/issues
- Email: [tu-email]

## Licencia

MIT
