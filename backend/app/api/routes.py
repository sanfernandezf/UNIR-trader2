"""
Rutas de la API REST
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import numpy as np

# Importar módulos propios
from ..data.binance_client import BinanceDataClient
from ..features.engineering import FeatureEngineer
from ..models.trainer import ModelTrainer
from ..backtesting.backtest import Backtester

# Variables globales para mantener estado
trainer = None
data_cache = {}

router = APIRouter()


# Modelos Pydantic para requests/responses
class DataRequest(BaseModel):
    symbol: str = 'BTCUSDT'
    lookback_days: int = 1825
    train_years: int = 4
    test_years: int = 1


class TrainRequest(BaseModel):
    parallel: bool = True


class BacktestRequest(BaseModel):
    pass


class StatusResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict] = None


@router.get("/", response_model=StatusResponse)
async def root():
    """Endpoint raíz."""
    return {
        "status": "success",
        "message": "UNIR Trader API - Sistema de Predicción de Bitcoin",
        "data": {
            "version": "1.0.0",
            "endpoints": [
                "/data/download",
                "/data/status",
                "/features/engineer",
                "/models/train",
                "/models/status",
                "/backtest/run",
                "/backtest/results"
            ]
        }
    }


@router.post("/data/download", response_model=StatusResponse)
async def download_data(request: DataRequest):
    """
    Descarga datos históricos de Binance.

    Args:
        request: Parámetros de descarga

    Returns:
        Status y resumen de datos descargados
    """
    try:
        print(f"\n📥 Descargando datos de {request.symbol}...")

        # Inicializar cliente
        client = BinanceDataClient()

        # Descargar datos
        df = client.get_historical_data(
            symbol=request.symbol,
            lookback_days=request.lookback_days
        )

        # Dividir en train/test
        df_train, df_test = client.split_train_test(
            df,
            train_years=request.train_years,
            test_years=request.test_years
        )

        # Guardar en caché
        data_cache['raw_data'] = df
        data_cache['train_data'] = df_train
        data_cache['test_data'] = df_test

        return {
            "status": "success",
            "message": f"Datos descargados correctamente de {request.symbol}",
            "data": {
                "total_records": len(df),
                "train_records": len(df_train),
                "test_records": len(df_test),
                "date_range": {
                    "start": str(df['timestamp'].min()),
                    "end": str(df['timestamp'].max())
                }
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data/status", response_model=StatusResponse)
async def get_data_status():
    """Obtiene el estado de los datos cargados."""
    if 'raw_data' not in data_cache:
        return {
            "status": "warning",
            "message": "No hay datos cargados",
            "data": None
        }

    df = data_cache['raw_data']

    return {
        "status": "success",
        "message": "Datos disponibles",
        "data": {
            "total_records": len(df),
            "train_records": len(data_cache.get('train_data', [])),
            "test_records": len(data_cache.get('test_data', [])),
            "features_engineered": 'features_train' in data_cache
        }
    }


@router.post("/features/engineer", response_model=StatusResponse)
async def engineer_features():
    """Genera características técnicas (RSI, MACD, Bollinger, etc.)."""
    try:
        if 'train_data' not in data_cache or 'test_data' not in data_cache:
            raise HTTPException(
                status_code=400,
                detail="Primero debe descargar los datos con /data/download"
            )

        print("\n🔧 Generando características técnicas...")

        # Generar características para train
        engineer_train = FeatureEngineer(data_cache['train_data'])
        df_train_features = engineer_train.add_all_features()

        # Generar características para test
        engineer_test = FeatureEngineer(data_cache['test_data'])
        df_test_features = engineer_test.add_all_features()

        # Obtener X, y
        feature_cols = engineer_train.get_feature_columns()

        X_train = df_train_features[feature_cols].values
        y_train = df_train_features['target'].values
        prices_train = df_train_features['close'].values

        X_test = df_test_features[feature_cols].values
        y_test = df_test_features['target'].values
        prices_test = df_test_features['close'].values

        # Guardar en caché
        data_cache['features_train'] = df_train_features
        data_cache['features_test'] = df_test_features
        data_cache['X_train'] = X_train
        data_cache['y_train'] = y_train
        data_cache['X_test'] = X_test
        data_cache['y_test'] = y_test
        data_cache['prices_train'] = prices_train
        data_cache['prices_test'] = prices_test
        data_cache['feature_names'] = feature_cols

        return {
            "status": "success",
            "message": "Características generadas correctamente",
            "data": {
                "total_features": len(feature_cols),
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "feature_names": feature_cols[:10]  # Primeras 10 features
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/train", response_model=StatusResponse)
async def train_models(request: TrainRequest):
    """Entrena múltiples modelos de ML en paralelo."""
    global trainer

    try:
        if 'X_train' not in data_cache:
            raise HTTPException(
                status_code=400,
                detail="Primero debe generar características con /features/engineer"
            )

        print(f"\n🤖 Entrenando modelos (paralelo={request.parallel})...")

        # Inicializar trainer
        trainer = ModelTrainer()
        trainer.initialize_models()

        # Obtener datos
        X_train = data_cache['X_train']
        y_train = data_cache['y_train']
        X_test = data_cache['X_test']
        y_test = data_cache['y_test']

        # Entrenar modelos
        if request.parallel:
            results = trainer.train_all_parallel(X_train, y_train, X_test, y_test)
        else:
            results = trainer.train_all_sequential(X_train, y_train, X_test, y_test)

        # Guardar predicciones
        predictions_dict = {}
        for model_name, result in results.items():
            if result['success']:
                model = result['model']
                predictions = model.predict(X_test)
                predictions_dict[model_name] = predictions

        data_cache['predictions'] = predictions_dict
        data_cache['training_results'] = results

        # Resumen
        summary = {
            model_name: {
                "success": result["success"],
                "training_time": f"{result['training_time']:.2f}s",
                "error": result.get("error")
            }
            for model_name, result in results.items()
        }

        return {
            "status": "success",
            "message": f"Modelos entrenados correctamente ({len(results)} modelos)",
            "data": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/status", response_model=StatusResponse)
async def get_models_status():
    """Obtiene el estado de los modelos."""
    if trainer is None:
        return {
            "status": "warning",
            "message": "No hay modelos entrenados",
            "data": None
        }

    models = trainer.get_trained_models()

    return {
        "status": "success",
        "message": f"{len(models)} modelos entrenados",
        "data": {
            "trained_models": [m.name for m in models],
            "predictions_ready": 'predictions' in data_cache
        }
    }


@router.post("/backtest/run", response_model=StatusResponse)
async def run_backtest():
    """Ejecuta el backtesting de todos los modelos."""
    try:
        if 'predictions' not in data_cache:
            raise HTTPException(
                status_code=400,
                detail="Primero debe entrenar los modelos con /models/train"
            )

        print("\n📊 Ejecutando backtesting...")

        # Obtener datos
        predictions_dict = data_cache['predictions']
        y_test = data_cache['y_test']
        prices_test = data_cache['prices_test']

        # Inicializar backtester
        backtester = Backtester(initial_capital=10000.0)

        # Ejecutar backtesting
        results = backtester.backtest_multiple_models(
            predictions_dict,
            y_test,
            prices_test
        )

        # Guardar resultados
        data_cache['backtest_results'] = results

        # Preparar resumen
        summary = {
            model_name: {
                "accuracy": result["accuracy"],
                "sharpe_ratio": result["sharpe_ratio"],
                "total_return_pct": result["total_return_pct"],
                "max_drawdown_pct": result["max_drawdown_pct"],
                "win_rate_pct": result["win_rate_pct"]
            }
            for model_name, result in results.items()
        }

        return {
            "status": "success",
            "message": "Backtesting completado",
            "data": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/backtest/results")
async def get_backtest_results():
    """Obtiene los resultados detallados del backtesting."""
    if 'backtest_results' not in data_cache:
        raise HTTPException(
            status_code=400,
            detail="Primero debe ejecutar el backtesting con /backtest/run"
        )

    return {
        "status": "success",
        "message": "Resultados del backtesting",
        "data": data_cache['backtest_results']
    }


@router.post("/pipeline/run", response_model=StatusResponse)
async def run_full_pipeline():
    """Ejecuta el pipeline completo: descarga, features, entrenamiento y backtesting."""
    try:
        print("\n" + "=" * 80)
        print("🚀 EJECUTANDO PIPELINE COMPLETO")
        print("=" * 80)

        # 1. Descargar datos
        await download_data(DataRequest())

        # 2. Generar características
        await engineer_features()

        # 3. Entrenar modelos
        await train_models(TrainRequest(parallel=True))

        # 4. Ejecutar backtesting
        await run_backtest()

        print("\n" + "=" * 80)
        print("✅ PIPELINE COMPLETADO")
        print("=" * 80)

        return {
            "status": "success",
            "message": "Pipeline completo ejecutado correctamente",
            "data": {
                "data_downloaded": True,
                "features_engineered": True,
                "models_trained": True,
                "backtest_completed": True
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
