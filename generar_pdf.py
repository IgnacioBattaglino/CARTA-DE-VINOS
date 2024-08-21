from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
import qrcode
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Configuración de credenciales y acceso a Google Sheets
SERVICE_ACCOUNT_FILE = 'credenciales.json'
SPREADSHEET_ID = '1kiskDtlupm0SV5mmwVF38fpaUsCYgSCDFTDjomv60zM'
LOGO_PATH = 'logo.png'
FILE_ID_PATH = 'file_id.txt'  # Archivo para guardar el ID del archivo PDF

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.file"
]

# Cargar credenciales
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Acceso a Google Sheets
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID)
worksheet = sheet.sheet1

# Leer datos de Google Sheets
data = worksheet.get_all_values()

# Eliminar filas vacías
cleaned_data = [row for row in data if any(cell.strip() for cell in row)]

# Convertir a DataFrame
df = pd.DataFrame(cleaned_data[1:], columns=cleaned_data[0])

# Crear el PDF con logo y título
pdf_buffer = io.BytesIO()
doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
elements = []

# Agregar logo
logo = Image(LOGO_PATH, width=200, height=200)  # Aumentar el tamaño del logo
elements.append(logo)

# Agregar título
styles = getSampleStyleSheet()
title = Paragraph("Carta de vinos", styles['Title'])
elements.append(title)

# Agregar un espacio en blanco 
elements.append(Spacer(1, 50))  

# Verificar si df tiene datos
if not df.empty:
    # Convertir el DataFrame a una lista de listas para la tabla
    table_data = [df.columns.tolist()] + df.values.tolist()

    # Estilo de la tabla
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Crear la tabla
    table = Table(table_data, colWidths=[doc.pagesize[0] / len(df.columns)] * len(df.columns))
    table.setStyle(table_style)
    elements.append(table)

    # Construir el PDF
    doc.build(elements)
    pdf_buffer.seek(0)

# Subir el PDF a Google Drive
drive_service = build('drive', 'v3', credentials=credentials)

# Intentar obtener el ID del archivo del archivo de texto
try:
    with open(FILE_ID_PATH, 'r') as file:
        file_id = file.read().strip()
except FileNotFoundError:
    file_id = None

if file_id:
    # Si el archivo ya existe, actualizarlo
    drive_service.files().update(
        fileId=file_id,
        media_body=MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf')
    ).execute()
else:
    # Si no existe, crear un nuevo archivo
    file_metadata = {
        'name': 'Carta_de_vinos.pdf',
        'parents': ['1-l3bVRKDbsiqeuBeK6xhvG6RTrpVUZDR']
    }
    file = drive_service.files().create(
        body=file_metadata,
        media_body=MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf'),
        fields='id'
    ).execute()
    file_id = file['id']
    # Guardar el ID del archivo en el archivo de texto
    with open(FILE_ID_PATH, 'w') as file:
        file.write(file_id)

# Configurar permisos para que cualquiera con el enlace pueda ver el archivo
permission = {
    'type': 'anyone',
    'role': 'reader'
}
drive_service.permissions().create(fileId=file_id, body=permission).execute()

# Obtener el URL del archivo
pdf_url = f"https://drive.google.com/file/d/{file_id}/view"

# Generar el código QR con el enlace al PDF
qr = qrcode.QRCode(box_size=10, border=5)
qr.add_data(pdf_url)
qr.make(fit=True)
qr_img = qr.make_image(fill='black', back_color='white')

# Guardar el QR en un archivo
qr_img.save('qr_code.png')
