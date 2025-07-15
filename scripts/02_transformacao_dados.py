import json
import os
import sys
from datetime import datetime

class Logger:
    def __init__(self, prefix="transformacao"):
        log_file_path = os.path.join("logs", "transformacao")
        os.makedirs(log_file_path, exist_ok=True)

        # Gera nome do arquivo com data: ex. logs/transformacao_2025-07-14.log
        today = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{prefix}_{today}.log"
        self.log_path = os.path.join(log_file_path, file_name)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}"
        print(line, file=sys.stderr if level in ["WARNING", "ERROR"] else sys.stdout)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

def transform_data(announcement, availability, output, logger):
    try:
        if not os.path.exists(announcement):
            logger.log(f"Arquivo de anúncio não encontrado: {announcement}", level="ERROR")
            raise FileNotFoundError(f"Anúncio ausente: {announcement}")

        if not os.path.exists(availability):
            logger.log(f"Arquivo de disponibilidade de datas não encontrado: {availability}", level="ERROR")
            raise FileNotFoundError(f"Disponibilidade de datas ausente: {availability}")

        logger.log("Carregando arquivos JSON...")
        with open(announcement, "r", encoding="utf-8") as f1, open(availability, "r", encoding="utf-8") as f2:
            announcement_info = json.load(f1)
            availability_info = json.load(f2)

        logger.log("Extraindo metadados do anúncio...")
        info = {
            "airbnb_id": announcement_info.get("id"),
            "name": announcement_info.get("name"),
            "city": announcement_info.get("city"),
            "country": announcement_info.get("country"),
            "property_type": announcement_info.get("property_type"),
            "person_capacity": announcement_info.get("person_capacity"),
            "is_superhost": announcement_info.get("primary_host", {}).get("is_superhost"),
            "price_native": announcement_info.get("price_native")
        }

        logger.log("Gerando linhas com os dados de disponibilidade de datas...")
        availability_date_table = []
        for item in availability_info.get("listing_dates", []):
            registry = {
                "date": item.get("date"),
                "availability": item.get("availability"),
                "min_stay": item.get("min_stay"),
                "pricing_type": item.get("pricing_type", {}).get("string")
            }
            registry.update(info)
            availability_date_table.append(registry)

        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w", encoding="utf-8") as f_out:
            json.dump(availability_date_table, f_out, ensure_ascii=False, indent=2)

        logger.log(f"Arquivo salvo com sucesso: {output}")
    except Exception as e:
        logger.log(f"Falha durante a transformação dos dados: {e}", level="ERROR")
        raise

if __name__ == "__main__":
    logger = Logger()

    base = "data/tmp"
    announcement = os.path.join(base, "announcement_data.json")
    availability = os.path.join(base, "availability_data.json")
    output = os.path.join(base, "transformed_data.json")

    transform_data(announcement, availability, output, logger)
    logger.log("Transformação dos dados finalizada.")

