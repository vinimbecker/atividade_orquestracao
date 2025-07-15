import json
import os
import sys
from datetime import datetime

from pyspark.sql import SparkSession

from pyspark.sql.functions import lit, col, udf

from pyspark.sql.types import StringType

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

        logger.log("Iniciando sessão Spark...")

        spark = SparkSession.builder.appName("TransformData").getOrCreate()

        logger.log("Carregando arquivos JSON...")

        with open(announcement, "r", encoding="utf-8") as f:
            announcement_info = json.load(f)

        with open(availability, "r", encoding="utf-8") as f:
            availability_raw = json.load(f)

        # Extrair a lista de datas e salvar como JSON lines
        listing_dates = availability_raw.get("listing_dates", [])
        logger.log(f"Nº de datas encontradas: {len(listing_dates)}")

        temp_file = "availability_spark_ready.json"

        with open(temp_file, "w", encoding="utf-8") as f_out:
            for item in listing_dates:
                f_out.write(json.dumps(item, ensure_ascii=False) + "\n")

        logger.log(f"{len(listing_dates)} linhas salvas em {temp_file}")
        

        logger.log("Preparando metadados do anúncio...")

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

        df_info = spark.createDataFrame([info])

        logger.log("Carregando disponibilidade no formato Spark compatível...")

        df_availability = spark.read.json(temp_file)

        logger.log(f"Nº de datas carregadas: {df_availability.count()}")

        logger.log("Realizando junção cruzada...")

        logger.log(f"Colunas: {df_availability.columns}")
        df_final = df_availability.crossJoin(df_info)

        logger.log("Salvando resultado em JSON...")

        os.makedirs(os.path.dirname(output), exist_ok=True)
        df_final.coalesce(1).write.mode("overwrite").json(output)

        logger.log(f"Arquivo salvo com sucesso: {output}")
        spark.stop()

        # Limpando arquivo temporário
        os.remove(temp_file)

    except Exception as e:
        logger.log(f"Falha durante a transformação dos dados: {e}", level="ERROR")
        raise

if __name__ == "__main__":
    logger = Logger()

    base = "data/tmp"
    announcement = os.path.join(base, "announcement_data.json")
    availability = os.path.join(base, "availability_data.json")
    output = os.path.join(base, "transformed_data")

    transform_data(announcement, availability, output, logger)
    logger.log("Transformação dos dados finalizada.")

