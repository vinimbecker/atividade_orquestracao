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

import glob

def process_json_to_parquet(folder_input, file_output, logger):
    if not os.path.exists(folder_input):
        logger.log(f"Pasta de entrada '{folder_input}' não encontrada!", level="ERROR")
        raise FileNotFoundError(f"Pasta ausente: {folder_input}")

    logger.log(f"Lendo arquivos JSON da pasta '{folder_input}'...")
    try:
        files = glob.glob(os.path.join(folder_input, "part-*.json"))

        if not files:
            logger.log(f"Nenhum arquivo JSON encontrado na pasta '{folder_input}'!", level="ERROR")
            raise ValueError("Pasta de entrada vazia ou sem arquivos part-*.json")

        dfs = []
        for f in files:
            with open(f, "r", encoding="utf-8") as f_in:
                # Pode haver múltiplos registros por arquivo
                for line in f_in:
                    obj = json.loads(line)
                    dfs.append(obj)

        df = pd.json_normalize(dfs)
        logger.log("Arquivos combinados em DataFrame.")

        os.makedirs(os.path.dirname(file_output), exist_ok=True)
        df.to_parquet(file_output, index=False)

        logger.log(f"Arquivo Parquet salvo em: '{file_output}'")
    except Exception as e:
        logger.log(f"Falha ao processar/gerar Parquet: {e}", level="ERROR")
        raise


# Exemplo de uso
if __name__ == "__main__":
    logger = Logger()

    input_folder = "data/tmp/transformed_data"  # Agora é uma pasta, não um arquivo
    output_file = "data/processed/final_data.parquet"

    process_json_to_parquet(input_folder, output_file, logger)
    logger.log("Finalizado.")
