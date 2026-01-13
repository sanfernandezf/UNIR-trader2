#!/bin/bash

echo "🚀 Iniciando Backend UNIR Trader..."
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "backend/venv" ]; then
    echo "📦 Creando entorno virtual..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activar entorno virtual e instalar dependencias
echo "📥 Instalando dependencias..."
cd backend
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Backend listo!"
echo "🌐 Iniciando servidor en http://localhost:8000"
echo "📚 Documentación API: http://localhost:8000/docs"
echo ""

# Iniciar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
