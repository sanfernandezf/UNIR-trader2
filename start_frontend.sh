#!/bin/bash

echo "🎨 Iniciando Frontend UNIR Trader..."
echo ""

cd frontend

# Verificar si existen node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias de Node.js..."
    npm install
fi

echo ""
echo "✅ Frontend listo!"
echo "🌐 Abriendo aplicación en http://localhost:3010"
echo ""

# Iniciar servidor de desarrollo
npm start
