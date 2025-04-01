from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Carregar o CSV
try:
    df = pd.read_csv("Relatorio_cadop.csv", sep=';')  # Arquivo está no mesmo diretório e usa ponto e vírgula como separador
    print("CSV carregado com sucesso!")
except Exception as e:
    print(f"Erro ao carregar o CSV: {str(e)}")
    df = None

@app.route('/teste', methods=['GET'])
def teste():
    return jsonify({"status": "ok", "mensagem": "Servidor está funcionando!"})

@app.route('/buscar', methods=['GET'])
def buscar_operadora():
    if df is None:
        return jsonify({"erro": "Banco de dados não está disponível"}), 500

    termo = request.args.get('termo', '').lower()

    if not termo:
        return jsonify({"erro": "Termo de busca é obrigatório"}), 400

    try:
        # Filtra os resultados que contêm o termo pesquisado
        resultados = df[df.apply(lambda row: row.astype(str).str.contains(termo, case=False).any(), axis=1)]
        return jsonify(resultados.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar operadoras: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
