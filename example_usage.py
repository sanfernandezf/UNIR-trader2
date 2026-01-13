"""
Ejemplo de uso del sistema UNIR Trader sin usar la API
Este script ejecuta todo el pipeline completo de forma local
"""

import sys
import os

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.data.binance_client import BinanceDataClient
from app.features.engineering import FeatureEngineer
from app.models.trainer import ModelTrainer
from app.backtesting.backtest import Backtester


def main():
    """Ejecuta el pipeline completo de predicción de Bitcoin."""

    print("\n" + "=" * 80)
    print("🚀 UNIR TRADER - PIPELINE COMPLETO")
    print("=" * 80)

    # ========== PASO 1: DESCARGAR DATOS ==========
    print("\n📊 PASO 1: Descargando datos de Binance...")
    print("-" * 80)

    client = BinanceDataClient()
    df = client.get_historical_data(
        symbol='BTCUSDT',
        lookback_days=1825  # 5 años
    )

    # Dividir en train/test
    df_train, df_test = client.split_train_test(df, train_years=4, test_years=1)

    # Opcional: Guardar datos
    # client.save_data(df, 'btc_data.csv')

    # ========== PASO 2: INGENIERÍA DE CARACTERÍSTICAS ==========
    print("\n🔧 PASO 2: Generando características técnicas...")
    print("-" * 80)

    # Generar características para training
    engineer_train = FeatureEngineer(df_train)
    df_train_features = engineer_train.add_all_features()

    # Generar características para testing
    engineer_test = FeatureEngineer(df_test)
    df_test_features = engineer_test.add_all_features()

    # Preparar datos para modelos
    feature_cols = engineer_train.get_feature_columns()
    X_train = df_train_features[feature_cols].values
    y_train = df_train_features['target'].values
    prices_train = df_train_features['close'].values

    X_test = df_test_features[feature_cols].values
    y_test = df_test_features['target'].values
    prices_test = df_test_features['close'].values

    print(f"\n📊 Datos preparados:")
    print(f"   - Características: {len(feature_cols)}")
    print(f"   - Muestras de entrenamiento: {len(X_train)}")
    print(f"   - Muestras de prueba: {len(X_test)}")

    # ========== PASO 3: ENTRENAR MODELOS ==========
    print("\n🤖 PASO 3: Entrenando modelos...")
    print("-" * 80)

    trainer = ModelTrainer()
    trainer.initialize_models()

    # Entrenar en paralelo
    results = trainer.train_all_parallel(
        X_train, y_train,
        X_test, y_test,
        max_workers=3
    )

    # Opcional: Guardar modelos
    # trainer.save_all_models('models_saved')

    # ========== PASO 4: BACKTESTING ==========
    print("\n📈 PASO 4: Ejecutando backtesting...")
    print("-" * 80)

    # Obtener predicciones de cada modelo
    predictions_dict = {}
    for model_name, result in results.items():
        if result['success']:
            model = result['model']
            predictions = model.predict(X_test)
            predictions_dict[model_name] = predictions

    # Ejecutar backtesting
    backtester = Backtester(initial_capital=10000.0)
    backtest_results = backtester.backtest_multiple_models(
        predictions_dict,
        y_test,
        prices_test
    )

    # Opcional: Exportar resultados
    # backtester.export_results('backtest_results.json')

    # ========== RESUMEN FINAL ==========
    print("\n" + "=" * 80)
    print("✅ PIPELINE COMPLETADO")
    print("=" * 80)

    print("\n🏆 MEJORES MODELOS:")

    # Encontrar mejor modelo por cada métrica
    best_accuracy = max(backtest_results.items(), key=lambda x: x[1]['accuracy'])
    best_sharpe = max(backtest_results.items(), key=lambda x: x[1]['sharpe_ratio'])
    best_return = max(backtest_results.items(), key=lambda x: x[1]['total_return'])

    print(f"\n  📊 Mejor Accuracy: {best_accuracy[0]}")
    print(f"     Valor: {best_accuracy[1]['accuracy']:.4f}")

    print(f"\n  📈 Mejor Sharpe Ratio: {best_sharpe[0]}")
    print(f"     Valor: {best_sharpe[1]['sharpe_ratio']:.4f}")

    print(f"\n  💰 Mejor Rentabilidad: {best_return[0]}")
    print(f"     Valor: {best_return[1]['total_return_pct']:.2f}%")

    print("\n" + "=" * 80)
    print("🎓 ¡Sistema de predicción completado con éxito!")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
