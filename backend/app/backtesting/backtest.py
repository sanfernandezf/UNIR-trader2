"""
Sistema de backtesting y cálculo de métricas de rendimiento
"""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)
from typing import Dict, List, Optional


class Backtester:
    """Clase para realizar backtesting y calcular métricas de rendimiento."""

    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Inicializa el backtester.

        Args:
            initial_capital: Capital inicial
            commission: Comisión por operación (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.results = {}

    def backtest_strategy(
        self,
        predictions: np.ndarray,
        actual: np.ndarray,
        prices: np.ndarray,
        model_name: str = 'model'
    ) -> Dict:
        """
        Realiza backtesting de una estrategia basada en predicciones.

        Args:
            predictions: Predicciones del modelo (1=compra, 0=venta/hold)
            actual: Valores reales (1=subida, 0=bajada)
            prices: Precios reales
            model_name: Nombre del modelo

        Returns:
            Diccionario con métricas de rendimiento
        """
        print(f"\n📊 Backtesting: {model_name}")

        # Calcular retornos
        returns = np.diff(prices) / prices[:-1]

        # Ajustar arrays al mismo tamaño
        min_len = min(len(predictions), len(returns), len(actual) - 1)
        predictions = predictions[:min_len]
        returns = returns[:min_len]
        actual_adjusted = actual[1:min_len + 1]

        # Estrategia: comprar cuando predicción = 1, vender/hold cuando = 0
        strategy_returns = np.where(predictions == 1, returns, 0)

        # Aplicar comisiones
        strategy_returns = strategy_returns - self.commission

        # Calcular equity curve
        equity_curve = self.initial_capital * (1 + strategy_returns).cumprod()

        # Métricas de clasificación
        accuracy = accuracy_score(actual_adjusted, predictions)
        precision = precision_score(actual_adjusted, predictions, zero_division=0)
        recall = recall_score(actual_adjusted, predictions, zero_division=0)
        f1 = f1_score(actual_adjusted, predictions, zero_division=0)
        conf_matrix = confusion_matrix(actual_adjusted, predictions)

        # Métricas financieras
        total_return = (equity_curve[-1] - self.initial_capital) / self.initial_capital
        annualized_return = self._calculate_annualized_return(strategy_returns)
        sharpe_ratio = self._calculate_sharpe_ratio(strategy_returns)
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        win_rate = self._calculate_win_rate(strategy_returns)

        # Buy & Hold para comparación
        buy_hold_return = (prices[-1] - prices[0]) / prices[0]

        results = {
            'model_name': model_name,
            # Métricas de clasificación
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': conf_matrix.tolist(),
            # Métricas financieras
            'initial_capital': self.initial_capital,
            'final_capital': equity_curve[-1],
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annualized_return': annualized_return,
            'annualized_return_pct': annualized_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'total_trades': len(strategy_returns),
            'winning_trades': np.sum(strategy_returns > 0),
            'losing_trades': np.sum(strategy_returns < 0),
            # Comparación con Buy & Hold
            'buy_hold_return': buy_hold_return,
            'buy_hold_return_pct': buy_hold_return * 100,
            'vs_buy_hold': total_return - buy_hold_return,
            # Curva de equity
            'equity_curve': equity_curve.tolist(),
            'strategy_returns': strategy_returns.tolist()
        }

        self._print_results(results)

        return results

    def backtest_multiple_models(
        self,
        models_predictions: Dict[str, np.ndarray],
        actual: np.ndarray,
        prices: np.ndarray
    ) -> Dict:
        """
        Realiza backtesting de múltiples modelos.

        Args:
            models_predictions: Diccionario {model_name: predictions}
            actual: Valores reales
            prices: Precios reales

        Returns:
            Diccionario con resultados de todos los modelos
        """
        print("\n" + "=" * 80)
        print("📊 BACKTESTING DE MÚLTIPLES MODELOS")
        print("=" * 80)

        all_results = {}

        for model_name, predictions in models_predictions.items():
            results = self.backtest_strategy(predictions, actual, prices, model_name)
            all_results[model_name] = results

        # Comparación
        self._print_comparison(all_results)

        self.results = all_results
        return all_results

    def _calculate_annualized_return(self, returns: np.ndarray, periods_per_year: int = 365 * 24) -> float:
        """
        Calcula el retorno anualizado.

        Args:
            returns: Array de retornos
            periods_per_year: Períodos por año (365*24 para datos horarios)

        Returns:
            Retorno anualizado
        """
        total_return = (1 + returns).prod() - 1
        n_periods = len(returns)
        years = n_periods / periods_per_year

        if years > 0:
            annualized_return = (1 + total_return) ** (1 / years) - 1
        else:
            annualized_return = 0

        return annualized_return

    def _calculate_sharpe_ratio(self, returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """
        Calcula el ratio de Sharpe.

        Args:
            returns: Array de retornos
            risk_free_rate: Tasa libre de riesgo anualizada

        Returns:
            Ratio de Sharpe
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0

        excess_returns = returns - (risk_free_rate / (365 * 24))  # Ajustar para datos horarios
        sharpe = np.sqrt(365 * 24) * excess_returns.mean() / excess_returns.std()

        return sharpe

    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """
        Calcula el máximo drawdown.

        Args:
            equity_curve: Curva de equity

        Returns:
            Máximo drawdown (como porcentaje)
        """
        cumulative_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - cumulative_max) / cumulative_max

        max_dd = np.min(drawdown)

        return max_dd

    def _calculate_win_rate(self, returns: np.ndarray) -> float:
        """
        Calcula la tasa de operaciones ganadoras.

        Args:
            returns: Array de retornos

        Returns:
            Tasa de operaciones ganadoras
        """
        trades = returns[returns != 0]  # Solo operaciones reales

        if len(trades) == 0:
            return 0

        win_rate = np.sum(trades > 0) / len(trades)

        return win_rate

    def _print_results(self, results: Dict):
        """
        Imprime los resultados del backtesting.

        Args:
            results: Diccionario con resultados
        """
        print(f"\n📈 Resultados de {results['model_name']}:")
        print(f"  Clasificación:")
        print(f"    - Accuracy:   {results['accuracy']:.4f}")
        print(f"    - Precision:  {results['precision']:.4f}")
        print(f"    - Recall:     {results['recall']:.4f}")
        print(f"    - F1-Score:   {results['f1_score']:.4f}")
        print(f"\n  Matriz de Confusión:")
        print(f"    {results['confusion_matrix']}")
        print(f"\n  Rendimiento Financiero:")
        print(f"    - Capital Inicial:      ${results['initial_capital']:,.2f}")
        print(f"    - Capital Final:        ${results['final_capital']:,.2f}")
        print(f"    - Retorno Total:        {results['total_return_pct']:.2f}%")
        print(f"    - Retorno Anualizado:   {results['annualized_return_pct']:.2f}%")
        print(f"    - Ratio de Sharpe:      {results['sharpe_ratio']:.4f}")
        print(f"    - Máximo Drawdown:      {results['max_drawdown_pct']:.2f}%")
        print(f"    - Win Rate:             {results['win_rate_pct']:.2f}%")
        print(f"    - Operaciones Totales:  {results['total_trades']}")
        print(f"    - Operaciones Ganadoras: {results['winning_trades']}")
        print(f"    - Operaciones Perdedoras: {results['losing_trades']}")
        print(f"\n  Comparación con Buy & Hold:")
        print(f"    - Buy & Hold Return:    {results['buy_hold_return_pct']:.2f}%")
        print(f"    - Diferencia:           {results['vs_buy_hold'] * 100:.2f}%")

    def _print_comparison(self, all_results: Dict):
        """
        Imprime una comparación de todos los modelos.

        Args:
            all_results: Diccionario con resultados de todos los modelos
        """
        print("\n" + "=" * 80)
        print("📊 COMPARACIÓN DE MODELOS")
        print("=" * 80)

        # Crear tabla comparativa
        df_comparison = pd.DataFrame([
            {
                'Modelo': name,
                'Accuracy': f"{r['accuracy']:.4f}",
                'Sharpe': f"{r['sharpe_ratio']:.4f}",
                'Retorno': f"{r['total_return_pct']:.2f}%",
                'Drawdown': f"{r['max_drawdown_pct']:.2f}%",
                'Win Rate': f"{r['win_rate_pct']:.2f}%"
            }
            for name, r in all_results.items()
        ])

        print(df_comparison.to_string(index=False))

        # Mejor modelo por métrica
        print("\n🏆 Mejores modelos por métrica:")

        best_accuracy = max(all_results.items(), key=lambda x: x[1]['accuracy'])
        print(f"  - Mejor Accuracy:  {best_accuracy[0]} ({best_accuracy[1]['accuracy']:.4f})")

        best_sharpe = max(all_results.items(), key=lambda x: x[1]['sharpe_ratio'])
        print(f"  - Mejor Sharpe:    {best_sharpe[0]} ({best_sharpe[1]['sharpe_ratio']:.4f})")

        best_return = max(all_results.items(), key=lambda x: x[1]['total_return'])
        print(f"  - Mejor Retorno:   {best_return[0]} ({best_return[1]['total_return_pct']:.2f}%)")

    def export_results(self, filename: str = 'backtest_results.json') -> str:
        """
        Exporta los resultados a un archivo JSON.

        Args:
            filename: Nombre del archivo

        Returns:
            Ruta del archivo exportado
        """
        import json
        import os

        if not self.results:
            print("⚠️ No hay resultados para exportar")
            return None

        # Crear directorio si no existe
        results_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results')
        os.makedirs(results_dir, exist_ok=True)

        filepath = os.path.join(results_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"💾 Resultados exportados a: {filepath}")

        return filepath
