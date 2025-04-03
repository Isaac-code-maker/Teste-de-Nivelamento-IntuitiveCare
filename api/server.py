from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app, resources={
    r"/buscar": {"origins": "*"},
    r"/teste": {"origins": "*"}
})  

# Carrega o DataFrame
df = None
try:
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_arquivo = os.path.join(diretorio_atual, "Relatorio_cadop.csv")
    
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_arquivo}")
    
    # Carrega o CSV com encoding alternativo caso utf-8 falhe
    try:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='utf-8', on_bad_lines='skip')
    except UnicodeDecodeError:
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1', on_bad_lines='skip')
    
    # Normaliza os nomes das colunas para corresponder ao que o front-end espera
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    print("CSV carregado com sucesso!")
    print("Colunas disponíveis:", df.columns.tolist())
except Exception as e:
    print(f"Erro ao carregar o CSV: {str(e)}")
    df = None

@app.route('/teste', methods=['GET'])
def teste():
    return jsonify({
        "status": "ok",
        "mensagem": "Servidor está funcionando!",
        "csv_carregado": df is not None,
        "colunas": df.columns.tolist() if df is not None else []
    })

@app.route('/buscar', methods=['GET'])
def buscar_operadora():
    if df is None:
        return jsonify({
            "erro": "Banco de dados não está disponível",
            "detalhes": "O arquivo CSV não foi carregado corretamente"
        }), 500

    termo = request.args.get('termo', '').lower().strip()
    print(f"Termo de busca recebido: '{termo}'")

    if not termo or len(termo) < 3:
        return jsonify({
            "erro": "Termo de busca é obrigatório",
            "detalhes": "Forneça um termo com pelo menos 3 caracteres"
        }), 400

    try:
        # Filtra os resultados
        colunas_texto = df.select_dtypes(include=['object']).columns
        mask = df[colunas_texto].apply(
            lambda col: col.astype(str).str.lower().str.contains(termo, na=False)
        )
        resultados = df[mask.any(axis=1)]
        
        # Converte para lista de dicionários e trata os valores
        dados = []
        for _, row in resultados.iterrows():
            operadora = {}
            for col in row.index:
                # Converte todos os valores para string e trata valores nulos
                valor = row[col]
                if pd.isna(valor):
                    operadora[col] = None
                elif isinstance(valor, (int, float)):
                    # Formata números sem decimais e mantém zeros à esquerda para CNPJ/Telefone
                    if col in ['CNPJ', 'CEP', 'Telefone', 'DDD', 'Registro_ANS']:
                        operadora[col] = f"{int(valor):0{len(str(int(valor)))}}"
                    else:
                        operadora[col] = str(int(valor))
                else:
                    operadora[col] = str(valor)
            dados.append(operadora)
        
        print(f"Encontrados {len(dados)} resultados")
        if dados:
            print("Exemplo de resultado formatado:", dados[0])
        
        return jsonify(dados)
    except Exception as e:
        print("Erro durante a busca:", str(e))
        return jsonify({
            "erro": "Erro ao buscar operadoras",
            "detalhes": str(e)
        }), 500

    termo = request.args.get('termo', '').lower().strip()
    print(f"Termo de busca recebido: '{termo}'")

    if not termo or len(termo) < 3:
        return jsonify({
            "erro": "Termo de busca é obrigatório",
            "detalhes": "Forneça um termo com pelo menos 3 caracteres"
        }), 400

    try:
        # Filtra considerando apenas colunas textuais
        colunas_texto = df.select_dtypes(include=['object']).columns
        mask = df[colunas_texto].apply(
            lambda col: col.astype(str).str.lower().str.contains(termo, na=False)
        )
        
        resultados = df[mask.any(axis=1)]
        print(f"Encontrados {len(resultados)} resultados")
        
        # Prepara os dados para o front-end
        dados = resultados.where(pd.notnull(resultados), None).to_dict(orient="records")
        
        # Debug: mostrar um resultado exemplo
        if len(dados) > 0:
            print("Exemplo de resultado:", {k: v for k, v in dados[0].items() if v is not None})
        
        return jsonify(dados)
    except Exception as e:
        print("Erro durante a busca:", str(e))
        return jsonify({
            "erro": "Erro ao buscar operadoras",
            "detalhes": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)