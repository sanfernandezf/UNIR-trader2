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

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm start
```

La aplicación estará disponible en `http://localhost:3000`

## Datos de Entrenamiento

- **Entrenamiento**: 4 años de datos históricos
- **Pruebas**: 1 año de datos

## Licencia

MIT
