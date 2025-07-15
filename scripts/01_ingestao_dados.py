import json
import os
import re
import sys
from datetime import datetime

class Logger:
    def __init__(self, prefix="ingestao"):
        log_file_path = os.path.join("logs", "ingestao")
        os.makedirs(log_file_path, exist_ok=True)

        # Gera nome do arquivo com data: ex. logs/ingestao_2025-07-14.log
        today = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{prefix}_{today}.log"
        self.log_path = os.path.join(log_file_path, file_name)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        print(line, file=sys.stderr if level in ["WARNING", "ERROR"] else sys.stdout)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

def load_json_with_validation(json_file_path, logger):
    if not os.path.exists(json_file_path):
        logger.log(f"Arquivo '{json_file_path}' não encontrado!", level="ERROR")
        return None

    logger.log(f"Tentando carregar '{json_file_path}'...")
    with open(json_file_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    try:
        data = json.loads(raw)
        logger.log(f"Arquivo '{json_file_path}' carregado com sucesso.")
        return data
    except json.JSONDecodeError as e:
        logger.log(f"Erro ao carregar '{json_file_path}': {e}", level="WARNING")
        logger.log("Tentando aplicar correções no conteúdo...")

        raw_fixed = re.sub(r",\s*([\]}])", r"\1", raw)
        raw_fixed = raw_fixed.replace("'", '"')
        raw_fixed = re.sub(r"[\x00-\x1F\x7F]", "", raw_fixed)

        try:
            data = json.loads(raw_fixed)
            logger.log(f"Arquivo '{json_file_path}' carregado com sucesso após correção.")
            return data
        except json.JSONDecodeError as e2:
            logger.log(f"Falha ao carregar '{json_file_path}' mesmo após correção: {e2}", level="ERROR")
            raise 

def check_null_values(data, source, logger):
    if isinstance(data, dict):
        for key, value in data.items():
            if value in [None, "", []]:
                logger.log(f"Valor nulo ou vazio no campo '{key}' de '{source}'", level="WARNING")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                for key, value in item.items():
                    if value in [None, "", []]:
                        logger.log(f"Valor nulo ou vazio em '{source}[{i}].{key}'", level="WARNING")

if __name__ == "__main__":
    logger = Logger()

    base_path = "data/raw"
    announcement_file_path = os.path.join(base_path, "listing_scrape.json")
    availability_file_path = os.path.join(base_path, "listing_availability_scrape.json")

    announcement_data = load_json_with_validation(announcement_file_path, logger)
    availability_data = load_json_with_validation(availability_file_path, logger)

    if announcement_data is not None:
        check_null_values(announcement_data, "listagem", logger)

    if availability_data is not None:
        check_null_values(availability_data, "disponibilidade", logger)

    announcement_loaded_file_path = "data/tmp/announcement_data.json"
    availability_loaded_file_path = "data/tmp/availability_data.json"

    if announcement_data is not None:
        with open(announcement_loaded_file_path, "w", encoding="utf-8") as f_out:
            json.dump(announcement_data, f_out, ensure_ascii=False, indent=2)
        logger.log(f"Arquivo salvo: {announcement_loaded_file_path}")

    if availability_data is not None:
        with open(availability_loaded_file_path, "w", encoding="utf-8") as f_out:
            json.dump(availability_data, f_out, ensure_ascii=False, indent=2)
        logger.log(f"Arquivo salvo: {availability_loaded_file_path}")

    logger.log("Processamento finalizado.")