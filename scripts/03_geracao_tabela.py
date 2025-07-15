import json
import os
import sys
import pandas as pd
from datetime import datetime

class Logger:
    def __init__(self, prefix="geracao_tabela"):
        log_file_path = os.path.join("logs", "geracao_tabela")
        os.makedirs(log_file_path, exist_ok=True)

        # Gera nome do arquivo com data: ex. logs/geracao_tabela_2025-07-14.log
        today = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{prefix}_{today}.log"
        self.log_path = os.path.join(log_file_path, file_name)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        print(line, file=sys.stderr if level in ["WARNING", "ERROR"] else sys.stdout)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

def process_json_to_parquet(file_input, file_output, logger):
    if not os.path.exists(file_input):
        logger.log(f"Arquivo de entrada '{file_input}' não encontrado!", level="ERROR")
        raise FileNotFoundError(f"Arquivo ausente: {file_input}")

    logger.log(f"Lendo JSON transformado de '{file_input}'...")
    try:
        with open(file_input, "r", encoding="utf-8") as f:
            dados = json.load(f)

        df = pd.json_normalize(dados)
        logger.log("JSON convertido em DataFrame.")

        os.makedirs(os.path.dirname(file_output), exist_ok=True)
        df.to_parquet(file_output, index=False)

        logger.log(f"Arquivo Parquet salvo em: '{file_output}'")
    except Exception as e:
        logger.log(f"Falha ao processar/gerar parquet do arquivo: {e}", level="ERROR")
        raise

# Exemplo de uso
if __name__ == "__main__":
    logger = Logger()

    input = "data/tmp/transformed_data.json"
    output = "data/processed/final_data.parquet"

    process_json_to_parquet(input, output, logger)
    logger.log("Finalizado.")