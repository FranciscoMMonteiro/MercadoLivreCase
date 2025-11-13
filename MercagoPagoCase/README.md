1. Introdução:
Este projeto implementa um pipeline de ETL automatizado para extração de dados da API pública do Mercado Livre, processando informações sobre anúncios do produto Samsung Galaxy S25 na Argentina.
O objetivo é responder perguntas analíticas essenciais como número de anúncios por vendedor, preço médio em dólares, garantias oferecidas e métodos de envio.

2. Arquitetura da Solução:
[Python ETL Scripts]
            ↓ (API Calls)
[Mercado Libre Public APIs]
            ↓
[Raw Tables in BigQuery]
            ↓
[Transformed Analytics View]
            ↓
[Looker Studio Dashboard]

3. Estrutura do Projeto:
MercadoLibreCase/
├── database/
│   ├── bd_connection_variables.json
│   ├── database_connection.py
├── etls/
│   ├── etl_currency_convertion.py
│   ├── etl_items.py
│   ├── etl_product_id.py
│   ├── etl_sellers.py
├── utils/
│   ├── api_functions.py
│   ├── token_functions.py
├── config/
│   ├── settings.env
│   ├── endpoints.json
├── .env
├── config.py
├── etl_orchestrator.log
├── install_env.bat
├── meli_case.yaml
├── README.md
├── run_etls.bat
├── run_etls.py
└── site_ids.json

4. Como Executar o Projeto:
  4.1. Rodar o arquivo "install_env.bat" para instalar as dependências.

  4.2. Configurar as Variaveis de Ambiente:
    a. Entrar no arquivo ".env" e adicionar as variaveis de ambiente:
      - CLIENT_SECRET : senha de acesso da aplicação criada no Site do Mercado Livre Developers
      - CLIENT_ID : ID da aplicação criada no Site do Mercado Livre Developers
      - USER_ID : A conta de usuario associada a aplicação criada
      - REDIRECT_URI : Site para redirecionamento cadastrado durante a criação da aplicação no Site do Mercado Livre Developers
      - ACCESS_TOKEN : Token de acesso OAuth. Esse token é automaticamente renovado durante o etl, porem você precisa pega-lo manualmente a primeira vez na criação da aplicação no Site do Mercado Livre Developers
      - REFRESH_TOKEN : Token de acesso OAuth.Esse token serve para renovar o ACCESS_TOKEN e é automaticamente renovado durante o etl, porém você precisa pega-lo manualmente a primeira vez na criação da aplicação no Site do Mercado e enviando um request POST conforme a documentação do site.

  4.3. Colocar os parametros de preferencia no arquivo "config.py"

  4.4. Rodar o ETL pelo "run_etls.bat"

5. DDL do Banco de Dados no Google BigQuery

CREATE TABLE IF NOT EXISTS `mercadolivrecase.currency_convertion` (
    from_currency_id     STRING      NULLABLE,
    to_currency_id       STRING      NULLABLE,
    rate                 FLOAT64     NULLABLE,
    rate_date            STRING      NULLABLE,
    job_run_timestamp    DATETIME    NULLABLE
);

CREATE TABLE IF NOT EXISTS `mercadolivrecase.items` (
    item_id            STRING     NULLABLE,
    product_id         STRING     NULLABLE,
    product_name       STRING     NULLABLE,
    condition          STRING     NULLABLE,
    category_id        STRING     NULLABLE,
    seller_id          INT64      NULLABLE,
    price              FLOAT64    NULLABLE,
    currency_id        STRING     NULLABLE,
    warranty           STRING     NULLABLE,
    shipping_mode      STRING     NULLABLE,
    job_run_timestamp  DATETIME   NULLABLE
);

CREATE TABLE IF NOT EXISTS `mercadolivrecase.products` (
    product_id         STRING     NULLABLE,
    product_name       STRING     NULLABLE,
    job_run_timestamp  DATETIME   NULLABLE
);

CREATE TABLE IF NOT EXISTS `mercadolivrecase.sellers` (
    seller_id            INT64      NULLABLE,
    nickname             STRING     NULLABLE,
    country_id           STRING     NULLABLE,
    address              STRING     NULLABLE,
    user_type            STRING     NULLABLE,
    site_id              STRING     NULLABLE,
    transactions         INT64      NULLABLE,
    transactions_period  STRING     NULLABLE,
    site_status          STRING     NULLABLE,
    job_run_timestamp    DATETIME   NULLABLE
);

CREATE OR REPLACE VIEW `mercadolivrecase.case_final_table` AS
with usd_currency_convertion as(
  SELECT 
    * 
  FROM 
    mercadolivrecase.currency_convertion 
  WHERE 
    to_currency_id = 'USD'
),

item_table as (
	SELECT
		item.*,
  	ucc.rate*item.price as price_usd
  FROM
		mercadolivrecase.items as item
  LEFT JOIN usd_currency_convertion as ucc ON
  	item.currency_id = ucc.from_currency_id
),

final_table as (
	SELECT
  	it.*,
  	sel.nickname as seller_name,
  	sel.transactions as transactions,
  	sel.transactions_period as transactions_period
  FROM
  	item_table as it
  LEFT JOIN mercadolivrecase.sellers as sel ON
  	it.seller_id = sel.seller_id		
)

SELECT
	*
FROM
	final_table

6. Queries para Responder as perguntas
  6.1. "¿Hay algún vendedor con múltiples publicaciones? En caso de que si, con cuantas?"

    QUERY:
    """
    SELECT
      seller_id,
      seller_name,
      count(DISTINCT item_id) AS listings_per_seller
    FROM
      mercadolivrecase.case_final_table
    GROUP BY
      seller_id,
      seller_name
    ORDER BY
      listings_per_seller DESC
    """

  6.2. ¿Promedio de ventas por seller?
    - Não foi possivel responder essa pergunta pois o endpoint "/items" não traz as vendas do anúncio.
    - Como subistituto eu usei o endpoint "/users" e peguei o numero de transação total dos vendedores que tem pelo menos um anuncio de "Galaxy Samsung S25"

    QUERY:
    """
    SELECT
      seller_id,
      seller_name,
      MAX(transactions) AS transactions
    FROM
      mercadolivrecase.case_final_table
    GROUP BY
      seller_id,
      seller_name
    ORDER BY
      transactions DESC
    """

  6.3 "¿Cuál es el precio promedio en dólares?"
    
    QUERY:
    """
    SELECT
      avg(price_usd) as average_price_usd
    FROM
      mercadolivrecase.case_final_table
    """

  6.4. "¿Porcentaje de artículos con garantía?"

    QUERY:
    """
    SELECT
      (SUM(CASE WHEN warranty <> "Sin garantía" THEN 1 ELSE 0 END))/COUNT(warranty)*100 as warranty_pct 
    FROM
      mercadolivrecase.case_final_table
      WHERE 
        warranty != ""
        AND warranty IS NOT NULL
    """
    OBS: Aqui não levei em conta strings vazios e valor nulo na conta.

  6.5. "¿Métodos de Shipping que ofrecen?"

    QUERY:
    """
    SELECT
      shipping_mode,
      count(shipping_mode) AS count_shipping_method
    FROM
      mercadolivrecase.case_final_table
    GROUP BY
      shipping_mode
    """

  7. Relatorio LookerStudio
  Link:[text](https://lookerstudio.google.com/reporting/cf82f37a-64a3-4cc7-b094-3c520ca33125)
  
  Story Telling:
  O dashboard segue a ordem das perguntas feitas para responder cada uma delas.

  9. Decisões de Design do sistema.
    - Banco de dados: Escolhi banco de dados em BigQuery por ser em nuvem (simulando um ambiente de trabalho) e por ser gratuito.
    - ETL: Criei um ETL para cada endpoint da API para o codigo ficar mais modularizado e no final criei um congregador que orquestra a execução de cada um dos scripts para ficar mais facil de executar tudo e na ordem certa.
    - Decidi puxar as transações do endpoint "/users" pois no endpoint "/items" não vinha as vendas por anuncio.
    - Fiz Upload de cada tabela separadamente no banco de dados para que estejam normalizadas e os relacionamentos sejam feitos em views ou em outros ambientes de acordo com a necessidade.
    - Comecei com o endpoint /search para so coletar os ids de produto que eram relevantes. Depois usei apenas os ids de produtos relevantes para achar os items_ids (anuncios), e com os items_ids puxei apenas os sellers dos items_ids achados do endpoint /users, e por ultimo puxei a conversão das moedas do endpoint /currency_conversions apenas para as moedas que estavam presentes nos anuncios que puxei anteriormente (ou seja nao usei o endpoint /currencies pois nao precisei puxar todas as moedas, decidi puxar so as relevantes para o Case)
    - Separei as variaveis de accesso a api no arquivo .env para nao ficar explicito no codigo e tambem separei as variveis de configuração do case no arquivo config.py para poderem ser facilmente alteradas caso a necessidade mude.

  10. Desafios encontrados
    - Tentei de muitas maneiras puxar a quantidade vendida pela api /items. Quando eu conseguia puxar esse campo nao vinha, e quando eu colocava os "attributes" especificos de sold_quantity a API retornava 403.
    Decidi pegar a quantidade total vendida pelos vendedores que tem pelo menos um anuncio de "Samsung Galaxy S25" pelo endpint /users, porém creio que não seja o que a questão estava solicitando.
    - Criar o sistema de autentificação e renovação de tokens.
    - Organizar o codigo, readme , config, .env, yaml e os bat de forma que fique facil rodar o codigo em outras maquinas pela primeira vez.
    - Primeira vez que mexo no looker, tive que adequar os conhecimentos de PowerBI.

  11. Oportunidades de melhoria
  - Ao invez de ter um script para orquestrar os etls seria melhor criar um pipeline em algum serviço de cloud.
  - Poderia ter uma tela bonita para pegar o input de qual o produto que queremos pegar os dados.
  - Testes unitarios



  
