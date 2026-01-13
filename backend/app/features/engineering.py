"""
Módulo de ingeniería de características para análisis técnico
Calcula indicadores: RSI, MACD, Bandas de Bollinger, y más
"""
import pandas as pd
import numpy as np
from typing import Optional


class FeatureEngineer:
    """Clase para generar características técnicas a partir de datos OHLCV."""

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el ingeniero de características.

        Args:
            df: DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        self.df = df.copy()

    def add_all_features(self) -> pd.DataFrame:
        """
        Añade todas las características técnicas al DataFrame.

        Returns:
            DataFrame con todas las características añadidas
        """
        print("🔧 Generando características técnicas...")

        # Indicadores básicos
        self.add_returns()
        self.add_moving_averages()

        # Indicadores técnicos
        self.add_rsi()
        self.add_macd()
        self.add_bollinger_bands()
        self.add_stochastic()
        self.add_atr()

        # Características adicionales
        self.add_volume_features()
        self.add_price_features()
        self.add_lag_features()

        # Crear target (predicción)
        self.create_target()

        # Eliminar NaN
        initial_rows = len(self.df)
        self.df = self.df.dropna()
        removed_rows = initial_rows - len(self.df)

        print(f"✅ Características generadas: {len(self.df.columns)} columnas")
        print(f"🧹 Filas eliminadas por NaN: {removed_rows}")
        print(f"📊 Filas finales: {len(self.df)}")

        return self.df

    def add_returns(self):
        """Calcula los retornos (cambios porcentuales)."""
        self.df['returns'] = self.df['close'].pct_change()
        self.df['log_returns'] = np.log(self.df['close'] / self.df['close'].shift(1))

    def add_moving_averages(self, periods: list = [7, 14, 21, 50, 200]):
        """
        Añade medias móviles simples (SMA) y exponenciales (EMA).

        Args:
            periods: Lista de períodos para las medias móviles
        """
        for period in periods:
            self.df[f'sma_{period}'] = self.df['close'].rolling(window=period).mean()
            self.df[f'ema_{period}'] = self.df['close'].ewm(span=period, adjust=False).mean()

    def add_rsi(self, period: int = 14):
        """
        Calcula el Relative Strength Index (RSI).

        Args:
            period: Período para el cálculo del RSI
        """
        delta = self.df['close'].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        self.df['rsi'] = 100 - (100 / (1 + rs))

    def add_macd(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        Calcula el MACD (Moving Average Convergence Divergence).

        Args:
            fast: Período rápido
            slow: Período lento
            signal: Período de la señal
        """
        ema_fast = self.df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = self.df['close'].ewm(span=slow, adjust=False).mean()

        self.df['macd'] = ema_fast - ema_slow
        self.df['macd_signal'] = self.df['macd'].ewm(span=signal, adjust=False).mean()
        self.df['macd_histogram'] = self.df['macd'] - self.df['macd_signal']

    def add_bollinger_bands(self, period: int = 20, std_dev: int = 2):
        """
        Calcula las Bandas de Bollinger.

        Args:
            period: Período para la media móvil
            std_dev: Número de desviaciones estándar
        """
        sma = self.df['close'].rolling(window=period).mean()
        std = self.df['close'].rolling(window=period).std()

        self.df['bb_upper'] = sma + (std * std_dev)
        self.df['bb_middle'] = sma
        self.df['bb_lower'] = sma - (std * std_dev)
        self.df['bb_width'] = self.df['bb_upper'] - self.df['bb_lower']
        self.df['bb_position'] = (self.df['close'] - self.df['bb_lower']) / self.df['bb_width']

    def add_stochastic(self, k_period: int = 14, d_period: int = 3):
        """
        Calcula el oscilador estocástico.

        Args:
            k_period: Período para %K
            d_period: Período para %D
        """
        low_min = self.df['low'].rolling(window=k_period).min()
        high_max = self.df['high'].rolling(window=k_period).max()

        self.df['stoch_k'] = 100 * (self.df['close'] - low_min) / (high_max - low_min)
        self.df['stoch_d'] = self.df['stoch_k'].rolling(window=d_period).mean()

    def add_atr(self, period: int = 14):
        """
        Calcula el Average True Range (ATR).

        Args:
            period: Período para el cálculo
        """
        high_low = self.df['high'] - self.df['low']
        high_close = np.abs(self.df['high'] - self.df['close'].shift())
        low_close = np.abs(self.df['low'] - self.df['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)

        self.df['atr'] = true_range.rolling(window=period).mean()

    def add_volume_features(self):
        """Añade características basadas en volumen."""
        self.df['volume_sma_20'] = self.df['volume'].rolling(window=20).mean()
        self.df['volume_ratio'] = self.df['volume'] / self.df['volume_sma_20']

        # On-Balance Volume (OBV)
        self.df['obv'] = (np.sign(self.df['close'].diff()) * self.df['volume']).fillna(0).cumsum()

    def add_price_features(self):
        """Añade características basadas en precio."""
        # Rango alto-bajo normalizado
        self.df['hl_ratio'] = (self.df['high'] - self.df['low']) / self.df['close']

        # Posición del cierre en el rango del día
        self.df['close_position'] = (self.df['close'] - self.df['low']) / (self.df['high'] - self.df['low'])

        # Diferencia open-close
        self.df['oc_diff'] = (self.df['close'] - self.df['open']) / self.df['open']

    def add_lag_features(self, lags: list = [1, 2, 3, 5, 7]):
        """
        Añade características rezagadas (lag features).

        Args:
            lags: Lista de períodos de rezago
        """
        for lag in lags:
            self.df[f'close_lag_{lag}'] = self.df['close'].shift(lag)
            self.df[f'volume_lag_{lag}'] = self.df['volume'].shift(lag)
            self.df[f'returns_lag_{lag}'] = self.df['returns'].shift(lag)

    def create_target(self, horizon: int = 1):
        """
        Crea la variable objetivo para predicción.

        Args:
            horizon: Horizonte de predicción (períodos hacia adelante)
        """
        # Precio futuro
        self.df['future_close'] = self.df['close'].shift(-horizon)

        # Retorno futuro
        self.df['future_return'] = (self.df['future_close'] - self.df['close']) / self.df['close']

        # Target binario: 1 si sube, 0 si baja
        self.df['target'] = (self.df['future_return'] > 0).astype(int)

        # Target multiclase: 0=baja mucho, 1=baja, 2=neutral, 3=sube, 4=sube mucho
        self.df['target_multiclass'] = pd.cut(
            self.df['future_return'],
            bins=[-np.inf, -0.02, -0.005, 0.005, 0.02, np.inf],
            labels=[0, 1, 2, 3, 4]
        ).astype(float)

    def get_feature_columns(self) -> list:
        """
        Obtiene la lista de columnas de características (excluyendo target y metadatos).

        Returns:
            Lista de nombres de columnas de características
        """
        exclude_cols = [
            'timestamp', 'future_close', 'future_return', 'target', 'target_multiclass'
        ]
        feature_cols = [col for col in self.df.columns if col not in exclude_cols]
        return feature_cols

    def get_prepared_data(self) -> tuple:
        """
        Prepara los datos para entrenamiento de modelos.

        Returns:
            Tupla con (X, y, feature_names)
        """
        feature_cols = self.get_feature_columns()

        X = self.df[feature_cols].values
        y = self.df['target'].values

        return X, y, feature_cols


# Función auxiliar para uso rápido
def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Función auxiliar para generar características rápidamente.

    Args:
        df: DataFrame con datos OHLCV

    Returns:
        DataFrame con características añadidas
    """
    engineer = FeatureEngineer(df)
    return engineer.add_all_features()
