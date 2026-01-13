"""
Modelo Random Forest para predicción de Bitcoin
"""
from sklearn.ensemble import RandomForestClassifier
from .base_model import BaseModel


class RandomForestModel(BaseModel):
    """Modelo de Random Forest para clasificación."""

    def __init__(self, n_estimators: int = 100, max_depth: int = 10, random_state: int = 42):
        """
        Inicializa el modelo Random Forest.

        Args:
            n_estimators: Número de árboles
            max_depth: Profundidad máxima de los árboles
            random_state: Semilla aleatoria
        """
        super().__init__(name='random_forest')
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

    def build_model(self, input_shape: tuple = None):
        """
        Construye el modelo Random Forest.

        Args:
            input_shape: No se usa en Random Forest
        """
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
            verbose=0
        )

    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Entrena el modelo Random Forest.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (no se usan)
            y_val: Etiquetas de validación (no se usan)
        """
        print(f"🌲 Entrenando {self.name}...")

        # Preprocesar datos
        X_train_scaled = self.preprocess(X_train)

        # Construir modelo si no existe
        if self.model is None:
            self.build_model()

        # Entrenar
        self.model.fit(X_train_scaled, y_train)
        self.is_fitted = True

        # Calcular accuracy en entrenamiento
        train_score = self.model.score(X_train_scaled, y_train)
        print(f"  ✅ Accuracy en entrenamiento: {train_score:.4f}")

        if X_val is not None and y_val is not None:
            X_val_scaled = self.scaler.transform(X_val)
            val_score = self.model.score(X_val_scaled, y_val)
            print(f"  ✅ Accuracy en validación: {val_score:.4f}")

    def get_feature_importance(self, feature_names: list) -> dict:
        """
        Obtiene la importancia de las características.

        Args:
            feature_names: Nombres de las características

        Returns:
            Diccionario con importancias ordenadas
        """
        if not self.is_fitted:
            raise ValueError("El modelo no ha sido entrenado")

        importances = self.model.feature_importances_
        feature_importance = dict(zip(feature_names, importances))

        # Ordenar por importancia
        sorted_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance
