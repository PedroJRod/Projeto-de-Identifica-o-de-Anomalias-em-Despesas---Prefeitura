# Projeto de Identificação de Anomalias em Despesas - Prefeitura

## Sumário

Este projeto visa identificar despesas com potencial de anomalia relacionadas ao credenciamento com objeto de prestação de serviços de pequenos reparos, reformas e manutenções corretivas e preventivas na Prefeitura. A análise é baseada no modelo `Isolation Forest` para detectar transações anômalas, reduzindo a amostra de despesas para verificação mais detalhada.

## Metodologia CRISP-DM

### 1. **Entendimento do Negócio**
   Como controlador interno da Prefeitura, o objetivo deste projeto é identificar despesas anômalas no credenciamento de serviços de pequenos reparos e manutenções. O foco é reduzir a amostra de transações suspeitas para otimizar a verificação manual, possibilitando maior eficiência e controle sobre o processo de gastos públicos.

   - **Contexto**: Verificação de despesas relacionadas a credenciamentos de serviços de manutenção e reparos.
   - **Objetivo**: Reduzir a amostra para verificação, identificando potenciais anomalias.
   - **Desafios**: Grandes volumes de dados podem ocultar transações fora do padrão, aumentando a necessidade de métodos automáticos de detecção de anomalias.

### 2. **Entendimento dos Dados**
   Os dados analisados foram extraídos de um relatório em Excel emitido pelo sistema administrativo da Prefeitura de **01/01/2024** até o dia **26/09/2024**, abrangendo **230 despesas**. Este relatório contém informações como Número de Empenho/Ano, Descrição, Data, Código da Dotação, Credor (Fornecedor) e Valor (R$).

   - **Fontes de Dados**: Relatório da Conferência da Despesas emitido pelo sistema administrativo.
   
### 3. **Preparação dos Dados**
   A preparação dos dados incluiu:

   - **Limpeza e Estruturação dos Dados**: 
     - Foi realizado tratamento do relatório com a remoção de linhas vazias e cabeçalhos desnecessários.
     - As descrições disponibilizadas abaixo das linhas de empenho foram movidas para uma nova coluna, associada ao empenho correspondente.
     - Colunas como data, valor e cnpj foram convertidas para seus respectivos tipos (datetime, float, string).
     
   - **Pré-processamento de Texto**:
     - Utilizou-se a biblioteca SpaCy para processar e limpar as descrições das despesas.
     - Foram removidas stopwords, pontuações e tokens irrelevantes, e aplicada a técnica de lematização para melhorar a análise textual.
     - Criação de uma **nuvem de palavras** para visualizar termos mais frequentes nas descrições.

   - **Feature Engineering**:
     - Extração de atributos como órgão, mês, valor da despesa e codificação dos atributos categóricos (`LabelEncoder`).
     - Conversão de valores textuais para vetores TF-IDF, o que permitiu usar representações textuais como variáveis no modelo.

### 4. **Modelagem**
   A técnica escolhida foi o `Isolation Forest`, um algoritmo eficiente para detecção de anomalias. Foi utilizado para identificar despesas fora do padrão com base nos seguintes atributos:

   - **Variáveis Consideradas no Modelo**:
     - Órgão responsável
     - Mês da despesa
     - Credor (codificado)
     - Elemento de despesa (codificado)
     - Funcional Programática (codificada)
     - Valor da despesa
     - Representações TF-IDF das descrições

   - **Parâmetros do Modelo**:
     - Contaminação definida em `0.1` (assumindo que 10% dos dados podem ser anômalos).
     - Semente aleatória (`random_state=42`) para replicabilidade.

### 5. **Avaliação**
   Após a execução do modelo, foram identificadas **16 despesas** com características anômalas, reduzindo significativamente a amostra de verificação de 230 para 16 despesas.

   - **Resultados**:
     - **Número de Transações Originais**: 230
     - **Número de Transações Anômalas**: 16
     - O algoritmo ajudou a otimizar a investigação manual, permitindo um foco mais detalhado nas despesas com maior potencial de inconsistências.

### 6. **Implantação**
   Os resultados foram exportados em formato Excel para posterior revisão e análise pelos auditores internos da Prefeitura.

   - **Exportação**: Arquivo gerado com as despesas identificadas como anômalas (`anomalias.xlsx`), que será utilizado no processo de verificação.

## Tecnologias Utilizadas
- **Linguagem**: Python
- **Bibliotecas**:
  - Pandas, Numpy (manipulação de dados)
  - Scikit-learn (modelagem e pré-processamento)
  - Matplotlib, Seaborn (visualização de dados)
  - SpaCy (processamento de linguagem natural)
  - WordCloud (geração de nuvens de palavras)
  - Isolation Forest (detecção de anomalias)

## Conclusão
Este projeto demonstrou a eficácia da aplicação de modelos de detecção de anomalias no controle interno de despesas da Prefeitura. A utilização de técnicas como `Isolation Forest` em conjunto com o pré-processamento textual permitiu reduzir a amostra de despesas de 230 para 16, facilitando a identificação de possíveis irregularidades e otimizando o tempo de análise dos auditores.
