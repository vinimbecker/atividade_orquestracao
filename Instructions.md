# Instruções de Configuração e Execução

 

## Visão Geral da Estrutura

 

Este projeto implementa um pipeline de orquestração utilizando Apache Airflow para processar dados JSON do Airbnb. A estrutura está organizada da seguinte forma:

 

```

atividade_orquestracao/

├── docker-compose.yaml      # Configuração do Docker Compose

├── Dockerfile              # Imagem Docker customizada

├── README.md               # Documentação principal

├── instructions.md         # Este arquivo com instruções detalhadas

├── dags/                   # DAGs do Airflow

│   └── dag_atividade_orquestracao.py

├── data/                   # Dados de entrada e saída

│   ├── raw/               # Dados brutos de entrada

│   │   ├── listing_scrape.json

│   │   └── listing_availability_scrape.json

│   ├── tmp/               # Dados temporários processados

│   │   ├── announcement_data.json

│   │   ├── availability_data.json

│   │   └── transformed_data.json

│   └── processed/         # Dados finais processados

│       └── final_data.parquet

└── scripts/               # Scripts Python do pipeline

    ├── 01_ingestao_dados.py

    ├── 02_transformacao_dados.py

    └── 03_geracao_tabela.py

```

 

## Pré-requisitos

 

- Docker Desktop instalado

- Docker Compose instalado

- Git instalado

- Pelo menos 4GB de RAM disponível

 

## Passos para Configuração

 

### 1. Clone o Repositório

 

```bash

git clone <url-do-repositorio>

cd atividade_orquestracao

```

 

### 2. Subir a Estrutura com Docker

 

Execute o comando para inicializar o ambiente Airflow:

 

```bash

docker-compose up -d

```

 

Este comando irá:

- Baixar as imagens necessárias do Airflow

- Criar os containers (webserver, scheduler, database, etc.)

- Configurar o banco de dados do Airflow

- Expor o webserver na porta 8080

 

### 3. Aguardar Inicialização

 

Aguarde alguns minutos para que todos os serviços inicializem completamente. Você pode acompanhar o progresso com:

 

```bash

docker-compose logs -f

```

 

### 4. Acessar o Airflow

 

Acesse o Airflow Web UI em: [http://localhost:8080](http://localhost:8080)

 

**Credenciais padrão:**

- Usuário: `airflow`

- Senha: `airflow`

 

## Estrutura do Pipeline

 

### Componentes Principais

 

1. **DAG Principal** (`dag_atividade_orquestracao.py`):

   - Orquestra todo o pipeline

   - Define dependências entre tasks

   - Configurado para executar diariamente

 

2. **Scripts de Processamento**:

   - `01_ingestao_dados.py`: Carrega dados JSON brutos

   - `02_transformacao_dados.py`: Transforma e combina dados

   - `03_geracao_tabela.py`: Gera tabela final em Parquet

 

### Fluxo de Dados

 

```

Dados RAW (JSON) → Ingestão → Transformação → Geração Final (Parquet)

```

 

1. **Ingestão**: Lê arquivos JSON da pasta `data/raw/`

2. **Transformação**: Combina dados de anúncios e disponibilidade

3. **Geração**: Salva resultado final em `data/processed/`

 

## Como Executar o Pipeline

 

### 1. Via Interface Web

 

1. Acesse [http://localhost:8080](http://localhost:8080)

2. Encontre a DAG `atividade_orquestracao`

3. Clique no botão "Play" para executar

 

### 2. Via Linha de Comando

 

```bash

# Listar DAGs

docker-compose exec airflow-webserver airflow dags list

 

# Executar DAG específica

docker-compose exec airflow-webserver airflow dags trigger atividade_orquestracao

```

 

## Monitoramento

 

### Logs do Pipeline

 

Os logs são salvos automaticamente em:

- `logs/transformacao/` - Logs específicos da transformação

- Interface web do Airflow - Logs completos de cada task

 

### Verificação de Resultados

 

1. **Dados Temporários**: Verifique `data/tmp/` para arquivos intermediários

2. **Resultado Final**: Verifique `data/processed/final_data.parquet`

 

## Troubleshooting

 

### Problemas Comuns

 

1. **Porta 8080 ocupada**:

   ```bash

   # Altere a porta no docker-compose.yaml

   ports:

     - "8081:8080"  # Use 8081 em vez de 8080

   ```

 

2. **Containers não inicializam**:

   ```bash

   # Reinicie os containers

   docker-compose down

   docker-compose up -d

   ```

 

3. **Problemas de permissão**:

   ```bash

   # Ajuste permissões das pastas

   chmod -R 755 data/

   chmod -R 755 logs/

   ```

 

### Comandos Úteis

 

```bash

# Ver status dos containers

docker-compose ps

 

# Parar todos os serviços

docker-compose down

 

# Reiniciar serviços

docker-compose restart

 

# Ver logs em tempo real

docker-compose logs -f

 

# Limpar volumes (cuidado: remove dados)

docker-compose down -v

```

 

## Estrutura de Logs

 

O sistema gera logs estruturados com:

- Timestamp

- Nível (INFO, WARNING, ERROR)

- Mensagem detalhada

- Arquivo de log rotativo por data

 

## Dados de Entrada

 

### Arquivos Esperados

 

1. **`listing_scrape.json`**: Contém informações dos anúncios

   - ID do anúncio

   - Nome, cidade, país

   - Tipo de propriedade

   - Capacidade de pessoas

   - Informações do host

   - Preço

 

2. **`listing_availability_scrape.json`**: Contém disponibilidade por data

   - Datas disponíveis

   - Disponibilidade (true/false)

   - Mínimo de noites

   - Tipo de preço

 

### Dados de Saída

 

- **`final_data.parquet`**: Tabela consolidada em formato Parquet

- Estrutura combinada com dados de anúncios e disponibilidade

- Otimizado para análise e consultas

 

## Próximos Passos

 

1. Execute o pipeline e verifique os resultados

2. Explore os logs para entender o fluxo

3. Modifique os scripts conforme necessário

4. Teste diferentes cenários de dados

 

Para mais detalhes técnicos, consulte o [README.md](README.md) principal.