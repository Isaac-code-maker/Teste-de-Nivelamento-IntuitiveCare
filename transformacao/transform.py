import os
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import zipfile
import re

def clean_ocr_text(text):
    """Corrige erros comuns do OCR"""
    corrections = {
        r'ﬁ': 'fi',
        r'ﬂ': 'fl',
        r'~': '-',
        r'éneia': 'ência',
        r'érese': 'érese',
        r'Gu ': 'ou ',
        r'!': 'l',
        r'sirnples': 'simples',
        r'tamis': 'tomia',
        r'\s+': ' '  # Remove múltiplos espaços
    }
    for wrong, correct in corrections.items():
        text = re.sub(wrong, correct, text)
    return text.strip()

def preprocess_image(image):
    """Adicionado: Pré-processamento para melhorar OCR"""
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    return cv2.medianBlur(img, 3)

def extract_table_data(text):
    """Modificado: Regex mais tolerante + limpeza do texto"""
    text = clean_ocr_text(text)
    pattern = r'([A-Z0-9]{4,8}|[^\s]+)\s*(.*?)\s+(OD|AMB|HCO|HSO|DUT)\b'
    
    data = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        codigo = match.group(1)
        procedimento = clean_ocr_text(match.group(2))
        segmentacao = match.group(3).upper()
        
        if len(procedimento) > 4:  # Filtro mais flexível
            data.append({
                'Código': codigo,
                'Procedimento': procedimento,
                'Segmentação': segmentacao
            })
    return data

# Seu código original abaixo (com apenas 2 ajustes):
try:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    print("Convertendo PDF para imagens...")
    images = convert_from_path(
        'nota13_geas_ggras_dipro_17012013.pdf',
        500,
        poppler_path=r'C:\Program Files\Release-24.08.0-0\poppler-24.08.0\Library\bin'
    )
    
    all_data = []
    for i, image in enumerate(images, 1):
        print(f"Processando página {i}...")
        
        # Modificação 1: Adicionado pré-processamento
        processed_img = preprocess_image(image)
        
        # Modificação 2: Configuração otimizada do OCR
        text = pytesseract.image_to_string(
            processed_img,
            lang='por+eng',
            config='--psm 6 --oem 3 -c preserve_interword_spaces=1'
        )
        
        page_data = extract_table_data(text)
        all_data.extend(page_data)
        print(f"Registros encontrados: {len(page_data)}")

    if not all_data:
        raise ValueError("Nenhum dado foi extraído das páginas")
    
    df = pd.DataFrame(all_data)
    df['Segmentação'] = df['Segmentação'].replace({
        'OD': 'Odontológico',
        'AMB': 'Ambulatorial',
        'HCO': 'Hospitalar com Obstetrícia',
        'HSO': 'Hospitalar sem Obstetrícia'
    })
    
    csv_path = 'Rol_de_Procedimentos.csv'
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    zip_path = 'Teste_IsaacAires.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv_path)

    print(f"Processo concluído! Arquivos gerados: {zip_path} e {csv_path}")
    print(f"\nTotal de procedimentos: {len(df)}")
    print(df.head())

except Exception as e:
    print(f"Erro: {str(e)}")
    import traceback
    traceback.print_exc()