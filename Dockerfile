# Etapa 1: Builder para baixar e preparar o Spark
FROM openjdk:17-slim AS spark-builder

ARG SPARK_VERSION=3.4.3
ARG HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    wget "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -O /tmp/spark.tgz && \
    mkdir -p /opt && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    rm /tmp/spark.tgz && \
    chmod -R 755 ${SPARK_HOME}

# Etapa 2: Imagem final baseada no Apache Airflow
FROM apache/airflow:2.8.1

USER root

# Instalar dependências necessárias
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV SPARK_VERSION=3.4.3
ENV HADOOP_VERSION=3
ENV SPARK_HOME=/opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}
ENV PATH=${JAVA_HOME}/bin:${SPARK_HOME}/bin:/home/airflow/.local/bin:${PATH}
ENV PYTHONPATH=${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-*.zip:${PYTHONPATH}

# Copiar Spark da imagem builder
COPY --from=spark-builder ${SPARK_HOME} ${SPARK_HOME}

# Ajustar permissões
RUN chmod -R 755 ${SPARK_HOME}

USER airflow

# Instalar bibliotecas Python necessárias
RUN pip install --user --no-cache-dir \
    pyspark==${SPARK_VERSION} \
    delta-spark==2.4.0 \
    apache-airflow-providers-apache-spark