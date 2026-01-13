"""
Modelo XGBoost para predicción de Bitcoin
"""
import xgboost as xgb
from .base_model import BaseModel


class XGBoostModel(BaseModel):
    """Modelo XGBoost para clasificación."""

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """
        Inicializa el modelo XGBoost.

        Args:
            n_estimators: Número de árboles
            max_depth: Profundidad máxima
            learning_rate: Tasa de aprendizaje
            random_state: Semilla aleatoria
        """
        super().__init__(name='xgboost')
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state

    def build_model(self, input_shape: tuple = None):
        """
        Construye el modelo XGBoost.

        Args:
            input_shape: No se usa en XGBoost
        """
        self.model = xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            n_jobs=-1,
            eval_metric='logloss',
            use_label_encoder=False
        )

    def train(self, X_train, y_train, X_val=None, y_val=None):
        """
        Entrena el modelo XGBoost.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)
        """
        print(f"🚀 Entrenando {self.name}...")

        # Preprocesar datos
        if X_val is not None:
            X_train_scaled, X_val_scaled = self.preprocess(X_train, X_val)
        else:
            X_train_scaled = self.preprocess(X_train)
            X_val_scaled = None

        # Construir modelo si no existe
        if self.model is None:
            self.build_model()

        # Configurar early stopping si hay datos de validación
        if X_val_scaled is not None and y_val is not None:
            eval_set = [(X_train_scaled, y_train), (X_val_scaled, y_val)]
            self.model.fit(
                X_train_scaled,
                y_train,
                eval_set=eval_set,
                verbose=False
            )
        else:
            self.model.fit(X_train_scaled, y_train)

        self.is_fitted = True

        # Calcular accuracy
        train_score = self.model.score(X_train_scaled, y_train)
        print(f"  ✅ Accuracy en entrenamiento: {train_score:.4f}")

        if X_val_scaled is not None and y_val is not None:
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
