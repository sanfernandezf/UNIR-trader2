import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

const API_BASE_URL = '/api/v1';

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [dataStatus, setDataStatus] = useState(null);
  const [trainingResults, setTrainingResults] = useState(null);
  const [backtestResults, setBacktestResults] = useState(null);
  const [error, setError] = useState(null);

  const steps = [
    {
      id: 0,
      title: '1. Descarga de Datos',
      description: 'Descargamos datos históricos de Bitcoin desde Binance',
      explanation: 'Utilizamos la API de Binance para obtener datos OHLC (Open, High, Low, Close) de Bitcoin/USD de los últimos 5 años. Estos datos serán la base para entrenar nuestros modelos.',
      action: downloadData
    },
    {
      id: 1,
      title: '2. Ingeniería de Características',
      description: 'Generamos indicadores técnicos: RSI, MACD, Bollinger Bands',
      explanation: 'Creamos características adicionales a partir de los datos brutos. Calculamos indicadores técnicos como RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), Bandas de Bollinger, y más. Estas características ayudan a los modelos a identificar patrones.',
      action: engineerFeatures
    },
    {
      id: 2,
      title: '3. Entrenamiento de Modelos',
      description: 'Entrenamos múltiples modelos de ML en paralelo',
      explanation: 'Entrenamos tres tipos de modelos diferentes: Random Forest (árboles de decisión), XGBoost (gradient boosting), y LSTM (redes neuronales recurrentes). Cada modelo aprende patrones diferentes de los datos.',
      action: trainModels
    },
    {
      id: 3,
      title: '4. Backtesting',
      description: 'Evaluamos el rendimiento de los modelos',
      explanation: 'Probamos cómo habrían funcionado los modelos en datos históricos que no vieron durante el entrenamiento. Calculamos métricas como accuracy, ratio de Sharpe, rentabilidad, y matriz de confusión.',
      action: runBacktest
    }
  ];

  async function downloadData() {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/data/download`, {
        symbol: 'BTCUSDT',
        lookback_days: 1825,
        train_years: 4,
        test_years: 1
      });
      setDataStatus(response.data.data);
      setCurrentStep(1);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error descargando datos');
    } finally {
      setLoading(false);
    }
  }

  async function engineerFeatures() {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/features/engineer`);
      setDataStatus({ ...dataStatus, ...response.data.data });
      setCurrentStep(2);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generando características');
    } finally {
      setLoading(false);
    }
  }

  async function trainModels() {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/models/train`, {
        parallel: true
      });
      setTrainingResults(response.data.data);
      setCurrentStep(3);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error entrenando modelos');
    } finally {
      setLoading(false);
    }
  }

  async function runBacktest() {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/backtest/run`);
      setBacktestResults(response.data.data);
      setCurrentStep(4);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error ejecutando backtesting');
    } finally {
      setLoading(false);
    }
  }

  async function runFullPipeline() {
    setLoading(true);
    setError(null);
    try {
      await downloadData();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await engineerFeatures();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await trainModels();
      await new Promise(resolve => setTimeout(resolve, 1000));
      await runBacktest();
    } catch (err) {
      setError('Error ejecutando el pipeline completo');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🚀 UNIR Trader</h1>
          <h2>Sistema de Predicción de Bitcoin usando Machine Learning</h2>
          <p style={{ color: '#fff', marginTop: '10px' }}>
            Aplicación didáctica que explica cada paso del proceso de análisis y predicción
          </p>
        </header>

        <div className="card">
          <h3>¿Qué es este proyecto?</h3>
          <div className="explanation">
            <p>
              Este sistema utiliza <strong>Machine Learning</strong> para predecir movimientos del precio de Bitcoin.
              El proceso completo incluye:
            </p>
            <ul style={{ marginTop: '10px', marginLeft: '20px' }}>
              <li>📊 Descarga de datos históricos de Binance (5 años)</li>
              <li>🔧 Ingeniería de características (RSI, MACD, Bollinger Bands)</li>
              <li>🤖 Entrenamiento de múltiples modelos en paralelo (Random Forest, XGBoost, LSTM)</li>
              <li>📈 Backtesting con métricas financieras (Sharpe, rentabilidad, drawdown)</li>
            </ul>
          </div>

          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              className="btn btn-primary"
              onClick={runFullPipeline}
              disabled={loading}
            >
              {loading ? '⏳ Procesando...' : '▶️ Ejecutar Pipeline Completo'}
            </button>
          </div>
        </div>

        {/* Progress Steps */}
        <div className="steps-container">
          {steps.map((step, index) => (
            <div key={step.id} className={`step-card ${currentStep >= index ? 'active' : ''}`}>
              <div className="step-header">
                <div className={`step-number ${currentStep > index ? 'completed' : ''}`}>
                  {currentStep > index ? '✓' : index + 1}
                </div>
                <h3>{step.title}</h3>
              </div>

              <p className="step-description">{step.description}</p>

              {currentStep >= index && (
                <div className="explanation">
                  <h4>💡 Explicación:</h4>
                  <p>{step.explanation}</p>
                </div>
              )}

              {currentStep === index && (
                <button
                  className="btn btn-primary"
                  onClick={step.action}
                  disabled={loading}
                >
                  {loading ? '⏳ Procesando...' : `Ejecutar ${step.title}`}
                </button>
              )}

              {/* Show results */}
              {index === 0 && dataStatus && currentStep > 0 && (
                <div className="results">
                  <h4>✅ Resultados:</h4>
                  <div className="metric">
                    <span className="metric-label">Total de registros:</span>
                    <span className="metric-value">{dataStatus.total_records}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Registros de entrenamiento:</span>
                    <span className="metric-value">{dataStatus.train_records}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Registros de prueba:</span>
                    <span className="metric-value">{dataStatus.test_records}</span>
                  </div>
                </div>
              )}

              {index === 1 && dataStatus && currentStep > 1 && dataStatus.total_features && (
                <div className="results">
                  <h4>✅ Resultados:</h4>
                  <div className="metric">
                    <span className="metric-label">Características generadas:</span>
                    <span className="metric-value">{dataStatus.total_features}</span>
                  </div>
                  <div className="metric">
                    <span className="metric-label">Muestras de entrenamiento:</span>
                    <span className="metric-value">{dataStatus.train_samples}</span>
                  </div>
                </div>
              )}

              {index === 2 && trainingResults && currentStep > 2 && (
                <div className="results">
                  <h4>✅ Resultados del entrenamiento:</h4>
                  {Object.entries(trainingResults).map(([modelName, result]) => (
                    <div key={modelName} className="metric">
                      <span className="metric-label">{modelName}:</span>
                      <span className="metric-value">
                        {result.success ? `✓ ${result.training_time}` : '✗ Error'}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {index === 3 && backtestResults && currentStep > 3 && (
                <div className="results">
                  <h4>✅ Resultados del backtesting:</h4>
                  {Object.entries(backtestResults).map(([modelName, result]) => (
                    <div key={modelName} className="model-results">
                      <h5>{modelName.toUpperCase()}</h5>
                      <div className="grid">
                        <div className="metric">
                          <span className="metric-label">Accuracy:</span>
                          <span className="metric-value">{(result.accuracy * 100).toFixed(2)}%</span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Sharpe Ratio:</span>
                          <span className="metric-value">{result.sharpe_ratio.toFixed(4)}</span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Rentabilidad:</span>
                          <span className="metric-value" style={{ color: result.total_return_pct > 0 ? '#10b981' : '#ef4444' }}>
                            {result.total_return_pct.toFixed(2)}%
                          </span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Max Drawdown:</span>
                          <span className="metric-value">{result.max_drawdown_pct.toFixed(2)}%</span>
                        </div>
                        <div className="metric">
                          <span className="metric-label">Win Rate:</span>
                          <span className="metric-value">{result.win_rate_pct.toFixed(2)}%</span>
                        </div>
                      </div>
                    </div>
                  ))}

                  <div className="explanation" style={{ marginTop: '20px' }}>
                    <h4>📊 Interpretación de Métricas:</h4>
                    <ul style={{ marginLeft: '20px', marginTop: '10px' }}>
                      <li><strong>Accuracy:</strong> Porcentaje de predicciones correctas</li>
                      <li><strong>Sharpe Ratio:</strong> Retorno ajustado por riesgo (mayor es mejor, &gt;1 es bueno)</li>
                      <li><strong>Rentabilidad:</strong> Ganancia/pérdida total del capital invertido</li>
                      <li><strong>Max Drawdown:</strong> Mayor caída desde un máximo (menor es mejor)</li>
                      <li><strong>Win Rate:</strong> Porcentaje de operaciones ganadoras</li>
                    </ul>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {error && (
          <div className="card" style={{ background: '#fee2e2', border: '2px solid #ef4444' }}>
            <h3 style={{ color: '#ef4444' }}>❌ Error</h3>
            <p style={{ color: '#991b1b' }}>{error}</p>
          </div>
        )}

        {loading && (
          <div className="card">
            <div className="loading">
              <div className="spinner"></div>
              <p>Procesando... Por favor espera</p>
            </div>
          </div>
        )}

        <footer className="footer">
          <p style={{ color: '#fff', textAlign: 'center', marginTop: '40px' }}>
            © 2024 UNIR Trader - Proyecto Educativo de Machine Learning
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
