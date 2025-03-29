import requests
from bs4 import BeautifulSoup
import zipfile
import os

# Criar pasta para downloads no diretório atual
pasta_downloads = os.path.join(os.path.dirname(__file__), "downloads")
if not os.path.exists(pasta_downloads):
    os.makedirs(pasta_downloads)

url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
try:
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
except requests.exceptions.Timeout:
    print("O site demorou muito para responder. Tente novamente mais tarde.")
except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar o site: {e}")

# Encontrar links dos Anexos I e II (ajuste conforme o HTML do site)
pdf_links = []
for link in soup.find_all('a', href=True):
    if 'Nota sobre Terminologias' in link.text or 'Correlação TUSS x Rol' in link.text:
        pdf_links.append(link['href'])

# Baixar os PDFs
for pdf_link in pdf_links:
    pdf_name = os.path.join(pasta_downloads, pdf_link.split('/')[-1])
    try:
        response = requests.get(pdf_link, timeout=30)
        if response.status_code == 200:
            with open(pdf_name, 'wb') as f:
                f.write(response.content)
            print(f"PDF baixado com sucesso: {pdf_name}")
        else:
            print(f"Erro ao baixar {pdf_name}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar {pdf_name}: {e}")

# Compactar em ZIP apenas se houver PDFs
pdfs_na_pasta = [f for f in os.listdir(pasta_downloads) if f.endswith('.pdf')]
if pdfs_na_pasta:
    zip_path = os.path.join(pasta_downloads, 'Anexos.zip')
    try:
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for arquivo in pdfs_na_pasta:
                caminho_completo = os.path.join(pasta_downloads, arquivo)
                zipf.write(caminho_completo, arquivo)
        print(f"Arquivo ZIP criado com sucesso: {zip_path}")
    except Exception as e:
        print(f"Erro ao criar arquivo ZIP: {e}")
else:
    print("Nenhum PDF foi encontrado para compactar")