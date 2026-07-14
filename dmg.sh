#!/bin/bash

# Nombre de la aplicación y del archivo DMG
APP_NAME="Diagramador de Flujo Pro.app"
DMG_NAME="Diagramador_de_Flujo_Pro.dmg"

# Rutas dentro de la carpeta dist
APP_PATH="dist/$APP_NAME"
DMG_PATH="dist/$DMG_NAME"

echo "🚀 Iniciando la creación del DMG para tu Diagramador..."

# 1. Verificar que create-dmg esté instalado
if ! command -v create-dmg &> /dev/null
then
    echo "❌ Error: 'create-dmg' no está instalado."
    echo "Por favor, instálalo primero desde la terminal usando: brew install create-dmg"
    exit 1
fi

# 2. Verificar que la app exista en la carpeta dist/
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Error: No se encuentra la aplicación en $APP_PATH"
    echo "Asegúrate de haber compilado primero con PyInstaller."
    exit 1
fi

# 3. Eliminar el DMG anterior si existe (para evitar errores)
if [ -f "$DMG_PATH" ]; then
    echo "🗑️ Eliminando versión anterior del DMG..."
    rm "$DMG_PATH"
fi

# 4. Crear el DMG mágico
echo "📦 Empaquetando la aplicación..."
create-dmg \
  --volname "Instalador Diagramador" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "$APP_NAME" 175 120 \
  --hide-extension "$APP_NAME" \
  --app-drop-link 425 120 \
  "$DMG_PATH" \
  "$APP_PATH"

echo "✅ ¡Listo! DMG creado con éxito en: $DMG_PATH"