import os
import mysql.connector
from mysql.connector import Error

try:
    # Configuração da conexão
    conn = mysql.connector.connect(
        host="localhost",  
        user="root",
        password="root",
        database="testenivelamento"
    )
    
    if conn.is_connected():
        print("Conexão com o MySQL estabelecida com sucesso!")
        
        cursor = conn.cursor()
        
        # Caminho onde os arquivos CSV estão
        pasta = "C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/"
        
        # Verifica se a pasta existe
        if not os.path.exists(pasta):
            print(f"Erro: A pasta {pasta} não existe!")
            exit(1)
            
        # Itera sobre os arquivos na pasta
        arquivos_processados = 0
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(".csv"):
                caminho_arquivo = os.path.join(pasta, arquivo).replace("\\", "/")
                print(f"\nProcessando arquivo: {arquivo}")
                
                sql = f"""
                LOAD DATA INFILE '{caminho_arquivo}'
                INTO TABLE demonstracoes_contabeis
                FIELDS TERMINATED BY ';'
                ENCLOSED BY '"'
                LINES TERMINATED BY '\\n'
                IGNORE 1 ROWS
                (data, reg_ans, cd_conta_contabil, descricao, @vl_saldo_inicial, @vl_saldo_final)
                SET vl_saldo_inicial = REPLACE(@vl_saldo_inicial, ',', '.'),
                    vl_saldo_final = REPLACE(@vl_saldo_final, ',', '.');
                """
                
                try:
                    cursor.execute(sql)
                    conn.commit()
                    print(f"✅ Arquivo importado com sucesso: {arquivo}")
                    arquivos_processados += 1
                except Error as err:
                    print(f"❌ Erro ao importar {arquivo}: {err}")
                    continue
        
        print(f"\nProcessamento concluído! {arquivos_processados} arquivos processados com sucesso.")

except Error as e:
    print(f"❌ Erro ao conectar ao MySQL: {e}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("\nConexão com o MySQL fechada.")
