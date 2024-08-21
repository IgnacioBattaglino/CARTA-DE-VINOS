# Proyecto de Generación de Carta de Vinos con Python

Este proyecto genera una carta de vinos en formato PDF a partir de los datos almacenados en una hoja de cálculo de Google Sheets. El archivo PDF se actualiza automáticamente y se sube a Google Drive. Además, se crea un código QR que enlaza al archivo PDF.

## Descripción

El proyecto está diseñado para generar una carta de vinos para la cava de Estancia Santa Angela en la provincia de Buenos Aires. Incluye:

- **Configuracion de Google Cloud Console** Se creo perfil comercial y se configuraron las APIs correspondientes para el correcto funcionamiento del script.
- **Lectura de datos** desde una hoja de cálculo en Google Sheets. (De esta manera el propietario puede cambiar los precios y el stock).
- **Generación de un PDF** con un logo, título y tabla de vinos.
- **Subida del PDF a Google Drive** y actualización del archivo si ya existe.
- **Creación de un código QR** que enlaza al PDF en Google Drive, el codigo QR NO cambia cuando el pdf es actualizado. 

## Librerias usadas

- Librerías: `google-auth`, `gspread`, `pandas`, `reportlab`, `qrcode`, `google-api-python-client`


