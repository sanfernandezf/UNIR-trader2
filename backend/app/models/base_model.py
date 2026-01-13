"""
Clase base para todos los modelos de predicción
"""
from abc import ABC, abstractmethod
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler


class BaseModel(ABC):
    """Clase base abstracta para todos los modelos."""

    def __init__(self, name: str):
        """
        Inicializa el modelo base.

        Args:
            name: Nombre identificativo del modelo
        """
        self.name = name
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = None
        self.history = None

    @abstractmethod
    def build_model(self, input_shape: tuple):
        """
        Construye la arquitectura del modelo.

        Args:
            input_shape: Forma de los datos de entrada
        """
        pass

    def preprocess(self, X_train, X_test=None):
        """
        Preprocesa los datos (normalización).

        Args:
            X_train: Datos de entrenamiento
            X_test: Datos de prueba (opcional)

        Returns:
            X_train escalado y X_test escalado (si se proporciona)
        """
        X_train_scaled = self.scaler.fit_transform(X_train)

        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled

        return X_train_scaled

    @abstractmethod
    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Entrena el modelo.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)
        """
        pass

    def predict(self, X):
        """
        Realiza predicciones.

        Args:
            X: Datos de entrada

        Returns:
            Predicciones
        """
        if not self.is_fitted:
            raise ValueError(f"El modelo {self.name} no ha sido entrenado")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X):
        """
        Realiza predicciones de probabilidad.

        Args:
            X: Datos de entrada

        Returns:
            Probabilidades
        """
        if not self.is_fitted:
            raise ValueError(f"El modelo {self.name} no ha sido entrenado")

        X_scaled = self.scaler.transform(X)

        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)
        else:
            # Para modelos que no tienen predict_proba, usar predict
            predictions = self.model.predict(X_scaled)
            # Convertir a probabilidades (0 o 1)
            return np.column_stack([1 - predictions, predictions])

    def save(self, directory: str = 'models_saved'):
        """
        Guarda el modelo y el scaler.

        Args:
            directory: Directorio donde guardar el modelo
        """
        os.makedirs(directory, exist_ok=True)

        model_path = os.path.join(directory, f'{self.name}_model.joblib')
        scaler_path = os.path.join(directory, f'{self.name}_scaler.joblib')

        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)

        print(f"💾 Modelo {self.name} guardado en {directory}")

    def load(self, directory: str = 'models_saved'):
        """
        Carga el modelo y el scaler.

        Args:
            directory: Directorio desde donde cargar el modelo
        """
        model_path = os.path.join(directory, f'{self.name}_model.joblib')
        scaler_path = os.path.join(directory, f'{self.name}_scaler.joblib')

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"No se encontró el modelo en {model_path}")

        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.is_fitted = True

        print(f"📂 Modelo {self.name} cargado desde {directory}")

    def get_info(self) -> dict:
        """
        Obtiene información del modelo.

        Returns:
            Diccionario con información del modelo
        """
        return {
            'name': self.name,
            'is_fitted': self.is_fitted,
            'feature_count': len(self.feature_names) if self.feature_names else None,
        }
