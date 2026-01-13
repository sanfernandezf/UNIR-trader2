# Guía de Despliegue en cubelabs.co/UNIR2

Esta guía te ayudará a desplegar la aplicación UNIR Trader en tu servidor en la ruta `cubelabs.co/UNIR2`.

## Requisitos del Servidor

- Ubuntu/Debian Linux
- Node.js 14+
- Python 3.8+
- Nginx
- PM2 (para gestionar procesos)
- SSL (Let's Encrypt recomendado)

## Paso 1: Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx

# Instalar PM2 globalmente
sudo npm install -g pm2
```

## Paso 2: Clonar el Repositorio

```bash
# Crear directorio
sudo mkdir -p /var/www/unir-trader
cd /var/www/unir-trader

# Clonar repositorio
sudo git clone https://github.com/sanfernandezf/UNIR-trader2.git .

# Cambiar permisos
sudo chown -R $USER:$USER /var/www/unir-trader
```

## Paso 3: Configurar Backend

```bash
cd /var/www/unir-trader/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus credenciales de Binance

# Probar backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Paso 4: Configurar Backend con PM2

Crear archivo de configuración PM2:

```bash
nano /var/www/unir-trader/ecosystem.config.js
```

Contenido:

```javascript
module.exports = {
  apps: [{
    name: 'unir-trader-api',
    cwd: '/var/www/unir-trader/backend',
    script: 'venv/bin/uvicorn',
    args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 4',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production'
    }
  }]
};
```

Iniciar backend:

```bash
cd /var/www/unir-trader
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Seguir instrucciones para inicio automático
```

## Paso 5: Construir Frontend

```bash
cd /var/www/unir-trader/frontend

# Instalar dependencias
npm install

# Configurar base path para /UNIR2
# Editar package.json y añadir:
# "homepage": "/UNIR2"

# Construir para producción
npm run build
```

## Paso 6: Configurar Frontend para Subfolder

Editar [frontend/package.json](frontend/package.json):

```json
{
  "name": "unir-trader-frontend",
  "version": "1.0.0",
  "homepage": "/UNIR2",
  ...
}
```

Crear archivo [frontend/src/setupProxy.js](frontend/src/setupProxy.js):

```javascript
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
    })
  );
};
```

Reconstruir:

```bash
npm run build
```

## Paso 7: Configurar Nginx

```bash
# Copiar configuración
sudo cp /var/www/unir-trader/nginx-cubelabs.conf /etc/nginx/sites-available/cubelabs.co

# Crear enlace simbólico
sudo ln -s /etc/nginx/sites-available/cubelabs.co /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

## Paso 8: Configurar SSL (HTTPS)

```bash
# Obtener certificados SSL de Let's Encrypt
sudo certbot --nginx -d cubelabs.co -d www.cubelabs.co

# Certbot configurará automáticamente HTTPS
# Si no, descomentar la sección HTTPS en nginx-cubelabs.conf

# Probar renovación automática
sudo certbot renew --dry-run
```

## Paso 9: Verificar Despliegue

1. **Frontend**: https://cubelabs.co/UNIR2
2. **API**: https://cubelabs.co/UNIR2/api/v1/
3. **Docs**: https://cubelabs.co/UNIR2/api/v1/docs (no funcionará con subfolder, usar IP:8000/docs)

## Paso 10: Monitoreo y Logs

```bash
# Ver logs del backend
pm2 logs unir-trader-api

# Ver logs de Nginx
sudo tail -f /var/log/nginx/cubelabs-access.log
sudo tail -f /var/log/nginx/cubelabs-error.log

# Ver estado de PM2
pm2 status
pm2 monit
```

## Actualización del Código

Para actualizar la aplicación:

```bash
cd /var/www/unir-trader

# Descargar últimos cambios
git pull origin main

# Actualizar backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart unir-trader-api

# Actualizar frontend
cd ../frontend
npm install
npm run build

# Recargar Nginx
sudo systemctl reload nginx
```

## Troubleshooting

### Error: Backend no responde

```bash
# Verificar que PM2 está corriendo
pm2 status

# Reiniciar backend
pm2 restart unir-trader-api

# Ver logs
pm2 logs unir-trader-api
```

### Error: Frontend no carga

```bash
# Verificar que el build existe
ls -la /var/www/unir-trader/frontend/build

# Verificar permisos
sudo chown -R www-data:www-data /var/www/unir-trader/frontend/build

# Verificar configuración de Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Error: 404 en rutas de React

Asegúrate de que la configuración de Nginx tiene:

```nginx
location /UNIR2 {
    alias /var/www/unir-trader/frontend/build;
    try_files $uri $uri/ /UNIR2/index.html;
}
```

### Error: API no responde

```bash
# Verificar que el puerto 8000 está abierto
sudo netstat -tulpn | grep 8000

# Verificar que PM2 está corriendo
pm2 list

# Probar backend directamente
curl http://localhost:8000/api/v1/
```

## Configuración de Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable

# Verificar estado
sudo ufw status
```

## Backup

Crear script de backup:

```bash
sudo nano /usr/local/bin/backup-unir-trader.sh
```

Contenido:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/unir-trader"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup de código
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /var/www/unir-trader

# Backup de datos
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /var/www/unir-trader/data /var/www/unir-trader/models_saved

# Mantener solo últimos 7 días
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completado: $DATE"
```

Hacer ejecutable y programar:

```bash
sudo chmod +x /usr/local/bin/backup-unir-trader.sh

# Añadir a crontab (backup diario a las 2 AM)
sudo crontab -e
# Añadir: 0 2 * * * /usr/local/bin/backup-unir-trader.sh
```

## Seguridad

1. **Firewall**: Configurado con UFW
2. **SSL**: Certificados Let's Encrypt
3. **API Keys**: Nunca exponer en el código
4. **Permisos**: Restringir acceso a archivos sensibles
5. **Updates**: Mantener sistema actualizado

```bash
# Restringir acceso a .env
chmod 600 /var/www/unir-trader/backend/.env

# Actualizar sistema regularmente
sudo apt update && sudo apt upgrade -y
```

## Recursos y Monitoreo

- **PM2 Web**: `pm2 web` (puerto 9615)
- **Logs centralizados**: Considerar usar Logrotate
- **Monitoreo**: Usar PM2 Plus o similar para monitoreo avanzado

## Soporte

Para problemas o preguntas:
- GitHub Issues: https://github.com/sanfernandezf/UNIR-trader2/issues
- Logs del sistema: `/var/log/nginx/` y `pm2 logs`
