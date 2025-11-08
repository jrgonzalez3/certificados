import os
import shutil
import re
from datetime import datetime
import pytesseract
from PIL import Image
import pdfplumber

src_dir = "archivos/"
dst_dir = "renombrado/"
os.makedirs(dst_dir, exist_ok=True)

academias = ['Udemy', 'Platzi', 'Coursera', 'Edutin', 'Crehana', 'LinkedIn', 'AulaFacil', 'UANATACA', 'Banco', 'Ministerio', 'Familiar', 'INTER']
tecnologias = ['php', 'python', 'angular', 'javascript', 'node', 'react', 'laravel', 'java', 'c#', 'banco', 'educacion']

def extract_text(filename):
    if filename.endswith('.pdf'):
        try:
            with pdfplumber.open(filename) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() or ''
                return text
        except:
            return ''
    elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            text = pytesseract.image_to_string(Image.open(filename))
            return text
        except:
            return ''
    return ''

def buscar_en_texto_y_nombre(texto, nombre, lista):
    for item in lista:
        if item.lower() in texto.lower() or item.lower() in nombre.lower():
            return item
    return ''

def extraer_horas(texto):
    match = re.search(r'(\\d+(\\.\\d+)?)(\\s*h| horas| hs)', texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return ''

def extraer_nombre_curso(texto, nombre):
    # Usa el nombre del archivo si no encuentra nada claro en el texto
    match = re.search(r'Certificado de finalizacion[:]?\\s*(.*)', texto, re.IGNORECASE)
    if match:
        return match.group(1).strip().replace(' ', '_')[:50]
    return nombre.replace(' ', '_')[:50]

def extraer_fecha_texto(texto):
    # Busca patrones de fecha en el texto
    patrones = [
        r'(\\d{1,2}/\\d{1,2}/\\d{4})',
        r'(\\d{1,2} de [A-Za-záéíóú]+ de \\d{4})',
        r'(\\d{4}-\\d{2}-\\d{2})'
    ]
    for p in patrones:
        match = re.search(p, texto)
        if match:
            try:
                dt = datetime.strptime(match.group(1), '%d/%m/%Y')
                return dt.strftime('%Y-%m-%d')
            except:
                try:
                    dt = datetime.strptime(match.group(1), '%Y-%m-%d')
                    return dt.strftime('%Y-%m-%d')
                except:
                    # Si el formato es "25 de julio de 2022"
                    meses = {"enero":1, "febrero":2, "marzo":3, "abril":4,"mayo":5,"junio":6,"julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
                    match2 = re.search(r'(\\d{1,2}) de ([A-Za-záéíóú]+) de (\\d{4})', match.group(1))
                    if match2:
                        day, mes, year = match2.groups()
                        month = meses.get(mes.lower(), 1)
                        fecha = datetime(int(year), month, int(day))
                        return fecha.strftime('%Y-%m-%d')
    return None

def obtener_fecha(file_path, texto):
    fecha = extraer_fecha_texto(texto)
    if fecha:
        return fecha
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

for file in os.listdir(src_dir):
    if not file.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
        continue
    file_path = os.path.join(src_dir, file)
    texto = extract_text(file_path)
    nombre_orig = os.path.splitext(file)[0]
    academia = buscar_en_texto_y_nombre(texto, nombre_orig, academias)
    tecnologia = buscar_en_texto_y_nombre(texto, nombre_orig, tecnologias)
    horas = extraer_horas(texto)
    nombre_curso = extraer_nombre_curso(texto, nombre_orig)
    fecha = obtener_fecha(file_path, texto)
    ext = os.path.splitext(file)[-1]
    nuevo_nombre = f"{fecha}-{academia}-{tecnologia}-{nombre_curso}-{horas}h{ext}".replace(' ', '_')
    shutil.copy(file_path, os.path.join(dst_dir, nuevo_nombre))
    print(f'Renombrado y copiado: {nuevo_nombre}')
