create database testenivelamento;
use testenivelamento;


SHOW VARIABLES LIKE 'secure_file_priv';

-- Estrutura da tabela para armazenar os dados contábeis das operadoras
CREATE TABLE demonstracoes_contabeis (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    reg_ans INT NOT NULL,
    cd_conta_contabil BIGINT NOT NULL,
    descricao TEXT NOT NULL,
    vl_saldo_inicial DECIMAL(15,2) NOT NULL,
    vl_saldo_final DECIMAL(15,2) NOT NULL
);

-- Comando para importar dados do CSV (PostgreSQL)
COPY demonstracoes_contabeis(data, reg_ans, cd_conta_contabil, descricao, vl_saldo_inicial, vl_saldo_final)
FROM '/caminho/para/arquivo.csv'
DELIMITER ';'
CSV HEADER;

-- Comando para importar dados do CSV (MySQL)
LOAD DATA INFILE 'C:\\ProgramData\\MySQL\\MySQL Server 8.0\\Uploads\\4T2024.csv'
INTO TABLE demonstracoes_contabeis
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(data, reg_ans, cd_conta_contabil, descricao, @vl_saldo_inicial, @vl_saldo_final)
SET vl_saldo_inicial = REPLACE(@vl_saldo_inicial, ',', '.'),
    vl_saldo_final = REPLACE(@vl_saldo_final, ',', '.');


-- Query analítica para encontrar as 10 operadoras com maiores despesas no último trimestre
SELECT reg_ans, 
       SUM(COALESCE(vl_saldo_final, 0) - COALESCE(vl_saldo_inicial, 0)) AS total_despesas
FROM demonstracoes_contabeis
WHERE LOWER(descricao) LIKE '%sinistro%'
AND data >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY reg_ans
ORDER BY total_despesas DESC
LIMIT 10;

SELECT MIN(data) AS primeira_data, MAX(data) AS ultima_data FROM demonstracoes_contabeis;




-- Query analítica para encontrar as 10 operadoras com maiores despesas no último ano
SELECT reg_ans, 
       SUM(COALESCE(vl_saldo_final, 0) - COALESCE(vl_saldo_inicial, 0)) AS total_despesas
FROM demonstracoes_contabeis
WHERE LOWER(descricao) LIKE '%sinistro%'
AND data >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
GROUP BY reg_ans
ORDER BY total_despesas DESC
LIMIT 10;

