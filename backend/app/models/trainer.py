"""
Sistema de entrenamiento paralelo de múltiples modelos
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import time
from .rf_model import RandomForestModel
from .xgb_model import XGBoostModel
from .lstm_model import LSTMModel


class ModelTrainer:
    """Clase para entrenar múltiples modelos en paralelo."""

    def __init__(self):
        """Inicializa el entrenador de modelos."""
        self.models = []
        self.results = {}

    def initialize_models(self) -> List:
        """
        Inicializa todos los modelos a entrenar.

        Returns:
            Lista de modelos
        """
        self.models = [
            RandomForestModel(n_estimators=100, max_depth=10),
            XGBoostModel(n_estimators=100, max_depth=6, learning_rate=0.1),
            LSTMModel(sequence_length=60, lstm_units=[128, 64], dropout=0.2)
        ]

        print(f"🤖 Modelos inicializados: {[m.name for m in self.models]}")
        return self.models

    def train_single_model(
        self,
        model,
        X_train,
        y_train,
        X_val=None,
        y_val=None
    ) -> Dict:
        """
        Entrena un modelo individual y retorna resultados.

        Args:
            model: Modelo a entrenar
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)

        Returns:
            Diccionario con resultados del entrenamiento
        """
        start_time = time.time()

        try:
            # Entrenar el modelo
            model.train(X_train, y_train, X_val, y_val)

            # Calcular tiempo de entrenamiento
            training_time = time.time() - start_time

            # Hacer predicciones en el conjunto de prueba
            predictions = model.predict(X_val) if X_val is not None else None

            return {
                'model_name': model.name,
                'model': model,
                'success': True,
                'training_time': training_time,
                'predictions': predictions,
                'error': None
            }

        except Exception as e:
            print(f"  ❌ Error entrenando {model.name}: {str(e)}")
            return {
                'model_name': model.name,
                'model': model,
                'success': False,
                'training_time': time.time() - start_time,
                'predictions': None,
                'error': str(e)
            }

    def train_all_parallel(
        self,
        X_train,
        y_train,
        X_val=None,
        y_val=None,
        max_workers: int = 3
    ) -> Dict:
        """
        Entrena todos los modelos en paralelo.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)
            max_workers: Número máximo de workers paralelos

        Returns:
            Diccionario con resultados de todos los modelos
        """
        print(f"\n🚀 Iniciando entrenamiento paralelo de {len(self.models)} modelos...")
        print(f"   Workers: {max_workers}")

        results = {}
        start_time = time.time()

        # Entrenar modelos en paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar trabajos
            future_to_model = {
                executor.submit(
                    self.train_single_model,
                    model,
                    X_train,
                    y_train,
                    X_val,
                    y_val
                ): model for model in self.models
            }

            # Recoger resultados
            for future in as_completed(future_to_model):
                result = future.result()
                results[result['model_name']] = result

        total_time = time.time() - start_time

        # Resumen
        print(f"\n✅ Entrenamiento completado en {total_time:.2f} segundos")
        print(f"   Modelos exitosos: {sum(1 for r in results.values() if r['success'])}/{len(results)}")

        for name, result in results.items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {name}: {result['training_time']:.2f}s")

        self.results = results
        return results

    def train_all_sequential(
        self,
        X_train,
        y_train,
        X_val=None,
        y_val=None
    ) -> Dict:
        """
        Entrena todos los modelos secuencialmente.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)

        Returns:
            Diccionario con resultados de todos los modelos
        """
        print(f"\n🔄 Iniciando entrenamiento secuencial de {len(self.models)} modelos...")

        results = {}
        start_time = time.time()

        for model in self.models:
            result = self.train_single_model(model, X_train, y_train, X_val, y_val)
            results[result['model_name']] = result

        total_time = time.time() - start_time

        # Resumen
        print(f"\n✅ Entrenamiento completado en {total_time:.2f} segundos")
        print(f"   Modelos exitosos: {sum(1 for r in results.values() if r['success'])}/{len(results)}")

        self.results = results
        return results

    def get_trained_models(self) -> List:
        """
        Obtiene la lista de modelos entrenados exitosamente.

        Returns:
            Lista de modelos entrenados
        """
        if not self.results:
            return []

        return [
            result['model']
            for result in self.results.values()
            if result['success']
        ]

    def save_all_models(self, directory: str = 'models_saved'):
        """
        Guarda todos los modelos entrenados.

        Args:
            directory: Directorio donde guardar los modelos
        """
        trained_models = self.get_trained_models()

        if not trained_models:
            print("⚠️ No hay modelos entrenados para guardar")
            return

        print(f"\n💾 Guardando {len(trained_models)} modelos...")

        for model in trained_models:
            try:
                model.save(directory)
            except Exception as e:
                print(f"  ❌ Error guardando {model.name}: {str(e)}")

        print("✅ Modelos guardados")

    def load_all_models(self, directory: str = 'models_saved'):
        """
        Carga todos los modelos guardados.

        Args:
            directory: Directorio desde donde cargar los modelos
        """
        print(f"\n📂 Cargando modelos desde {directory}...")

        for model in self.models:
            try:
                model.load(directory)
            except Exception as e:
                print(f"  ⚠️ No se pudo cargar {model.name}: {str(e)}")

        print("✅ Modelos cargados")


# Función auxiliar para uso rápido
def train_all_models(X_train, y_train, X_val=None, y_val=None, parallel: bool = True):
    """
    Función auxiliar para entrenar todos los modelos rápidamente.

    Args:
        X_train: Datos de entrenamiento
        y_train: Etiquetas de entrenamiento
        X_val: Datos de validación (opcional)
        y_val: Etiquetas de validación (opcional)
        parallel: Si True, entrena en paralelo

    Returns:
        Diccionario con resultados
    """
    trainer = ModelTrainer()
    trainer.initialize_models()

    if parallel:
        results = trainer.train_all_parallel(X_train, y_train, X_val, y_val)
    else:
        results = trainer.train_all_sequential(X_train, y_train, X_val, y_val)

    return trainer, results
