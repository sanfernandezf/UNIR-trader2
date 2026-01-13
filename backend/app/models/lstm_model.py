"""
Modelo LSTM (Long Short-Term Memory) para predicción de Bitcoin
"""
import numpy as np
from tensorflow import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from .base_model import BaseModel


class LSTMModel(BaseModel):
    """Modelo LSTM para clasificación de series temporales."""

    def __init__(
        self,
        sequence_length: int = 60,
        lstm_units: list = [128, 64],
        dropout: float = 0.2,
        learning_rate: float = 0.001,
        random_state: int = 42
    ):
        """
        Inicializa el modelo LSTM.

        Args:
            sequence_length: Longitud de la secuencia temporal
            lstm_units: Lista con unidades LSTM por capa
            dropout: Tasa de dropout
            learning_rate: Tasa de aprendizaje
            random_state: Semilla aleatoria
        """
        super().__init__(name='lstm')
        self.sequence_length = sequence_length
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.learning_rate = learning_rate
        self.random_state = random_state

        # Establecer semilla
        np.random.seed(random_state)

    def build_model(self, input_shape: tuple):
        """
        Construye la arquitectura del modelo LSTM.

        Args:
            input_shape: Forma de los datos de entrada (sequence_length, n_features)
        """
        self.model = Sequential(name=self.name)

        # Primera capa LSTM
        self.model.add(LSTM(
            units=self.lstm_units[0],
            return_sequences=len(self.lstm_units) > 1,
            input_shape=input_shape
        ))
        self.model.add(Dropout(self.dropout))

        # Capas LSTM adicionales
        for i, units in enumerate(self.lstm_units[1:], 1):
            return_sequences = i < len(self.lstm_units) - 1
            self.model.add(LSTM(units=units, return_sequences=return_sequences))
            self.model.add(Dropout(self.dropout))

        # Capa de salida
        self.model.add(Dense(1, activation='sigmoid'))

        # Compilar modelo
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

    def create_sequences(self, X, y=None):
        """
        Crea secuencias temporales para LSTM.

        Args:
            X: Datos de entrada
            y: Etiquetas (opcional)

        Returns:
            X_sequences y y_sequences (si se proporciona y)
        """
        X_sequences = []
        y_sequences = [] if y is not None else None

        for i in range(self.sequence_length, len(X)):
            X_sequences.append(X[i - self.sequence_length:i])
            if y is not None:
                y_sequences.append(y[i])

        X_sequences = np.array(X_sequences)

        if y is not None:
            y_sequences = np.array(y_sequences)
            return X_sequences, y_sequences

        return X_sequences

    def train(self, X_train, y_train, X_val=None, y_val=None, epochs: int = 50, batch_size: int = 32):
        """
        Entrena el modelo LSTM.

        Args:
            X_train: Datos de entrenamiento
            y_train: Etiquetas de entrenamiento
            X_val: Datos de validación (opcional)
            y_val: Etiquetas de validación (opcional)
            epochs: Número de épocas
            batch_size: Tamaño del batch
        """
        print(f"🧠 Entrenando {self.name}...")

        # Preprocesar datos
        if X_val is not None:
            X_train_scaled, X_val_scaled = self.preprocess(X_train, X_val)
        else:
            X_train_scaled = self.preprocess(X_train)
            X_val_scaled = None

        # Crear secuencias
        X_train_seq, y_train_seq = self.create_sequences(X_train_scaled, y_train)

        if X_val_scaled is not None and y_val is not None:
            X_val_seq, y_val_seq = self.create_sequences(X_val_scaled, y_val)
            validation_data = (X_val_seq, y_val_seq)
        else:
            validation_data = None

        # Construir modelo si no existe
        if self.model is None:
            input_shape = (self.sequence_length, X_train_scaled.shape[1])
            self.build_model(input_shape)

        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if validation_data else 'loss',
                patience=10,
                restore_best_weights=True,
                verbose=0
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if validation_data else 'loss',
                factor=0.5,
                patience=5,
                min_lr=0.00001,
                verbose=0
            )
        ]

        # Entrenar
        self.history = self.model.fit(
            X_train_seq,
            y_train_seq,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=0
        )

        self.is_fitted = True

        # Mostrar resultados
        final_train_loss = self.history.history['loss'][-1]
        final_train_acc = self.history.history['accuracy'][-1]
        print(f"  ✅ Loss en entrenamiento: {final_train_loss:.4f}")
        print(f"  ✅ Accuracy en entrenamiento: {final_train_acc:.4f}")

        if validation_data:
            final_val_loss = self.history.history['val_loss'][-1]
            final_val_acc = self.history.history['val_accuracy'][-1]
            print(f"  ✅ Loss en validación: {final_val_loss:.4f}")
            print(f"  ✅ Accuracy en validación: {final_val_acc:.4f}")

    def predict(self, X):
        """
        Realiza predicciones.

        Args:
            X: Datos de entrada

        Returns:
            Predicciones (0 o 1)
        """
        if not self.is_fitted:
            raise ValueError(f"El modelo {self.name} no ha sido entrenado")

        X_scaled = self.scaler.transform(X)
        X_seq = self.create_sequences(X_scaled)

        predictions_prob = self.model.predict(X_seq, verbose=0)
        predictions = (predictions_prob > 0.5).astype(int).flatten()

        return predictions

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
        X_seq = self.create_sequences(X_scaled)

        predictions_prob = self.model.predict(X_seq, verbose=0).flatten()

        # Retornar probabilidades para ambas clases
        return np.column_stack([1 - predictions_prob, predictions_prob])
