import cv2
import numpy as np
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
import zipfile
import re
import os

# =============================================
# CONFIGURAÇÕES INICIAIS
# =============================================

# Configura o caminho do Tesseract OCR (ajuste para seu computador)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuração do Poppler (para converter PDF em imagens)
POPPLER_PATH = r'C:\Program Files\Release-24.08.0-0\poppler-24.08.0\Library\bin'

# =============================================
# FUNÇÕES DE PROCESSAMENTO
# =============================================

def melhorar_qualidade_imagem(imagem):
    """
    Pré-processa a imagem para melhorar o OCR
    Retorna: Imagem em preto e branco com texto destacado
    """
    # Converte para array numpy
    img_array = np.array(imagem)
    
    # Se for colorida, converte para escala de cinza
    if len(img_array.shape) == 3:
        img_cinza = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        img_cinza = img_array
    
    # Aplica desenfoque Gaussiano para reduzir ruído
    img_desfocada = cv2.GaussianBlur(img_cinza, (3,3), 0)
    
    # Aumenta o contraste
    img_contraste = cv2.convertScaleAbs(img_desfocada, alpha=1.5, beta=0)
    
    # Aplica limiarização adaptativa com parâmetros ajustados
    img_limiar = cv2.adaptiveThreshold(
        img_contraste, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 15, 5
    )
    
    # Remove ruídos pequenos
    kernel = np.ones((2,2), np.uint8)
    img_limpa = cv2.morphologyEx(img_limiar, cv2.MORPH_OPEN, kernel)
    
    # Aplica dilatação para melhorar a legibilidade
    kernel_dilate = np.ones((1,1), np.uint8)
    img_dilatada = cv2.dilate(img_limpa, kernel_dilate, iterations=1)
    
    return img_dilatada

def extrair_texto(imagem):
    """
    Extrai texto de uma imagem usando OCR
    Retorna: Texto extraído
    """
    img_processada = melhorar_qualidade_imagem(imagem)
    
    # Configuração do Tesseract para tabelas médicas
    config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzÀ-ú0123456789-(),. '
    
    try:
        texto = pytesseract.image_to_string(img_processada, lang='por', config=config)
        print(f"Texto extraído: {texto[:200]}...")  # Mostra os primeiros 200 caracteres
        return texto
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return ""

def encontrar_procedimentos(texto):
    """
    Identifica procedimentos e segmentações no texto
    Retorna: Lista de dicionários com os dados
    """
    # Padrões mais específicos para encontrar procedimentos
    padroes = [
        # Padrão para procedimentos com segmentação específica
        r'([A-Za-zÀ-ú][A-Za-zÀ-ú\s\-]+?)\s+(OD|AMB|HCO|HSO|DUT)\b',
        # Padrão para procedimentos com segmentação em maiúsculas
        r'([A-Za-zÀ-ú][A-Za-zÀ-ú\s\-]+?)\s+([A-Z]{2,4})\b',
        # Padrão para procedimentos com segmentação por extenso
        r'([A-Za-zÀ-ú][A-Za-zÀ-ú\s\-]+?)\s+(?:Diretriz|Ambulatorial|Hospitalar)'
    ]
    
    dados = []
    for padrao in padroes:
        try:
            matches = list(re.finditer(padrao, texto, re.IGNORECASE))
            print(f"Encontrados {len(matches)} matches com o padrão: {padrao}")
            
            for match in matches:
                try:
                    procedimento = match.group(1).strip()
                    
                    # Tenta obter a segmentação do grupo 2, se existir
                    if len(match.groups()) > 1:
                        segmentacao = match.group(2).upper()
                    else:
                        # Se não houver grupo 2, tenta encontrar a segmentação no texto
                        segmentacao_match = re.search(r'(OD|AMB|HCO|HSO|DUT|Diretriz|Ambulatorial|Hospitalar)', 
                                                    match.group(0), re.IGNORECASE)
                        if segmentacao_match:
                            segmentacao = segmentacao_match.group(1).upper()
                        else:
                            continue
                    
                    print(f"Match encontrado: {procedimento} -> {segmentacao}")
                    
                    # Validações mais flexíveis
                    if len(procedimento) > 5:  # Reduzido o tamanho mínimo
                        dados.append({
                            "Procedimento": procedimento,
                            "Segmentação": segmentacao
                        })
                except IndexError as e:
                    print(f"Erro ao processar match: {e}")
                    continue
                except Exception as e:
                    print(f"Erro inesperado ao processar match: {e}")
                    continue
                    
        except Exception as e:
            print(f"Erro ao processar padrão {padrao}: {e}")
            continue
    
    return dados

def validar_dados(dados):
    # Lista de segmentações válidas
    segmentacoes_validas = {'OD', 'AMB', 'HCO', 'HSO', 'DUT'}
    
    # Lista de palavras comuns em procedimentos médicos (expandida)
    palavras_validas = {
        'cirurgia', 'exame', 'procedimento', 'consulta', 'terapia',
        'medula', 'cordotomia', 'mielotomia', 'punção', 'lombar',
        'cisternal', 'estimulação', 'medular', 'odontológico', 'ambulatorial',
        'hospitalar', 'diretriz', 'utilização'
    }
    
    dados_validados = []
    for item in dados:
        procedimento = item['Procedimento'].lower()
        segmentacao = item['Segmentação']
        
        # Verifica se a segmentação é válida
        if segmentacao not in segmentacoes_validas:
            print(f"Segmentação inválida ignorada: {segmentacao}")
            continue
            
        # Verifica se o procedimento contém palavras válidas
        if not any(palavra in procedimento for palavra in palavras_validas):
            print(f"Procedimento sem palavras válidas ignorado: {procedimento}")
            continue
            
        dados_validados.append(item)
    
    return dados_validados

# =============================================
# FUNÇÃO PRINCIPAL
# =============================================

def processar_pdf(caminho_pdf, saida_csv, saida_zip):
    try:
        print("\nIniciando processamento do PDF...")
        
        # Configurações do PDF
        imagens = convert_from_path(
            caminho_pdf,
            dpi=300,
            grayscale=True,
            poppler_path=POPPLER_PATH
        )
        
        todos_dados = []
        for num_pagina, imagem in enumerate(imagens, 1):
            print(f"\nProcessando página {num_pagina}/{len(imagens)}")
            
            # Extrai texto
            texto = extrair_texto(imagem)
            
            # Encontra procedimentos
            dados_pagina = encontrar_procedimentos(texto)
            
            # Valida os dados
            dados_validados = validar_dados(dados_pagina)
            todos_dados.extend(dados_validados)
            
            print(f"Encontrados {len(dados_validados)} procedimentos válidos")
        
        # Cria DataFrame mesmo se não houver dados
        df = pd.DataFrame(todos_dados)
        
        # Se não houver dados, cria um DataFrame vazio com as colunas corretas
        if df.empty:
            df = pd.DataFrame(columns=['Procedimento', 'Segmentação'])
            print("Nenhum procedimento encontrado. Criando arquivo CSV vazio.")
        
        # Remove duplicatas se houver dados
        if not df.empty:
            df = df.drop_duplicates(subset=['Procedimento', 'Segmentação'])
        
        # Traduz abreviações
        traducao = {
            'OD': 'Odontológico',
            'AMB': 'Ambulatorial',
            'HCO': 'Hospitalar com Obstetrícia',
            'HSO': 'Hospitalar sem Obstetrícia',
            'DUT': 'Diretriz de Utilização'
        }
        df['Segmentação'] = df['Segmentação'].map(traducao)
        
        # Salva resultados
        df.to_csv(saida_csv, index=False, encoding='utf-8-sig')
        print(f"\nArquivo CSV salvo em: {saida_csv}")
        
        with zipfile.ZipFile(saida_zip, 'w') as zipf:
            zipf.write(saida_csv)
        print(f"Arquivo ZIP criado em: {saida_zip}")
        
        return df
        
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        import traceback
        print(traceback.format_exc())  # Mostra o stack trace completo
        return None

# =============================================
# EXECUÇÃO PRINCIPAL
# =============================================

if __name__ == "__main__":
    # Configurações (ajuste conforme necessário)
    ARQUIVO_PDF = "nota13_geas_ggras_dipro_17012013.pdf"  # Nome do seu arquivo PDF
    ARQUIVO_CSV = "Rol_de_Procedimentos.csv"
    ARQUIVO_ZIP = "Teste_SEU_NOME.zip"  # 👈 Substitua SEU_NOME pelo seu nome
    
    # Verifica se o PDF existe
    if not os.path.exists(ARQUIVO_PDF):
        print(f"\n❌ Arquivo {ARQUIVO_PDF} não encontrado!")
        print("Coloque o PDF na mesma pasta deste script ou ajuste o caminho.")
    else:
        # Executa o processamento
        dados = processar_pdf(ARQUIVO_PDF, ARQUIVO_CSV, ARQUIVO_ZIP)
        
        # Mostra os primeiros resultados (opcional)
        if dados is not None:
            print("\n🔍 Primeiros registros extraídos:")
            print(dados.head(10))