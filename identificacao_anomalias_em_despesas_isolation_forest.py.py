pip install unidecode

import pandas as pd
import numpy as np
from unidecode import unidecode

from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from sklearn.preprocessing import LabelEncoder

import math

# Pacotes gráficos
import matplotlib.pyplot as plt
import seaborn as sns

# Pacotes de manipulação de textos
import re
import string

df = pd.read_excel('RConferencia_Despesa_Empenho_excel_30_09_2024_09_48_25.xlsx')

df.head(10)

df.columns = df.iloc[8]  # Definindo a primeira linha como cabeçalho
df = df.reset_index(drop=True)

def to_snake_case(column_name):
    column_name = unidecode(column_name)  # Remove acentos
    column_name = column_name.strip().lower().replace(" ", "_").replace("-", "_")
    return ''.join(e for e in column_name if e.isalnum() or e == '_')

# Renomeando as colunas usando a função to_snake_case
df.columns = [to_snake_case(col) for col in df.columns]

df = df.iloc[9:]
df = df.iloc[:-2]

df['numempano'].fillna(method='ffill', inplace=True)

df = df.dropna(subset=['tipo'])

df = df.reset_index(drop=True)

# Filtrando as linhas onde a coluna 'numempano' é diferente de "DESCRIÇÃO:"
df_empenhos = df[~df['numempano'].isin(["DESCRIÇÃO:"])]

df_empenhos = df_empenhos.reset_index(drop=True)
df_empenhos.head(5)

# Lista para armazenar resultados
resultados = []
concat_str = ''

# Percorrer as linhas do DataFrame
for index, row in df.iterrows():
    if row['numempano'] == 'DESCRIÇÃO:':
        # Continuar a concatenação
        concat_str += str(row['tipo']) + ' '
    elif row['numempano'] != 'DESCRIÇÃO:':
        # Finalizar concatenação e adicionar ao resultado
        if concat_str:
            resultados.append(concat_str.strip())
        concat_str = ''

# Se ainda houver algo concatenado (última linha não foi ORDEM DE CONSUMO:)
if concat_str:
    resultados.append(concat_str.strip())

# Criar novo DataFrame com os resultados
df_descricoes = pd.DataFrame(resultados, columns=['descricao'])

# Exibir o resultado
df_descricoes.head(5)

df_descricoes.shape

df_despesas = pd.concat([df_empenhos, df_descricoes], axis=1)
df_despesas[['reduzido','dotacao']] = df_despesas['dotacao'].str.split(' - ', expand=True)

# Converter a coluna 'data' para o tipo datetime
df_despesas['data'] = pd.to_datetime(df_despesas['data'], format='%d/%m/%Y')

# Extrair componentes da data
df_despesas['mes'] = df_despesas['data'].dt.month

df_despesas['valor'] = pd.to_numeric(df_despesas['valor'])

df_despesas['elemento_despesa'] = df_despesas['dotacao'].str[-10:]

df_despesas['dotacao'] = df_despesas['dotacao'].str[:-10]

df_despesas['orgao_unidade'] = df_despesas['dotacao'].str[:2]

df_despesas['dotacao'] = df_despesas['dotacao'].str[5:]

df_despesas = df_despesas.rename(columns={'dotacao': 'funcional_programatica'})

df_despesas.head(5)

df_despesas.shape

# Seleção das variáveis para NLP
df_nlp = df_despesas[['descricao']].copy()
df_nlp

pip install -U spacy

!python -m spacy download pt_core_news_sm

import spacy
modelo_spacy = spacy.load('pt_core_news_sm')

#modelo_spacy.Defaults.stop_words.clear()

modelo_spacy.Defaults.stop_words

def preproc_nlp(texto, modelo_spacy=modelo_spacy):

    # Aplicação do modelo no texto original
    texto_spacy = list(modelo_spacy(texto))

    # Lista de tokens após preparação
    texto_result = list()

    for t in texto_spacy:
        # Remoção de pontuação
        if t.is_punct:
            continue
        # Remoção de números
        if t.is_digit:
            continue
        # Remoção de espaços extras
        if t.is_space:
            continue
        # Remoção de stopwords
        if t.is_stop:
            continue
        # Conversão para minúsculas e lematização
        texto_result.append(t.lemma_.lower())

    texto_result = ' '.join(texto_result)

    return texto_result

df_nlp['descricao_clean'] = df_nlp['descricao'].apply(preproc_nlp)

from wordcloud import WordCloud

# Função para geração da WordCloud
def plot_wordcloud(wc):
    plt.figure(figsize=(20,10))
    plt.imshow(wc)
    plt.axis("off")

wc_texto = WordCloud(width = 1000, height = 500)\
    .generate_from_text(' '.join(df_nlp['descricao_clean'].to_list()))

plot_wordcloud(wc_texto)

# Adição de tokens na lista de stopwords
modelo_spacy.Defaults.stop_words |= {"sendo","instalar","pedreiro","servente","despesa","despesas","empenha","orçamento", "anexo","prestação","prestacao","referente","serviço","servicos","pequenos","reparo","conforme","atender","necessidade","inexigibilidade","conta","credenciamento","manutenção"}

df_nlp['descricao_clean'] = df_nlp['descricao'].apply(preproc_nlp)

wc_texto = WordCloud(width = 1000, height = 500)\
    .generate_from_text(' '.join(df_nlp['descricao_clean'].to_list()))

plot_wordcloud(wc_texto)

from sklearn.feature_extraction.text import TfidfVectorizer

tfidfvec = TfidfVectorizer(ngram_range=(1,2))
tfidfvec_data = tfidfvec.fit_transform(df_nlp['descricao_clean'])

tfidfvec.vocabulary_

df_tfidf_desc = pd.DataFrame(data=tfidfvec_data.toarray(),
                        index=df_nlp.index,
                        columns=tfidfvec.get_feature_names_out())
df_tfidf_desc

#Atualizar os nomes das colunas para refletir que são representações TF-IDF
df_tfidf_desc.columns = [f'descricao_tfidf_{i}' for i in range(df_tfidf_desc.shape[1])]

df_despesas.head(2)

le = LabelEncoder()
df_despesas['cnpj_encoded'] = le.fit_transform(df_despesas['credor'])
df_despesas['elemento_despesa_encoded'] = le.fit_transform(df_despesas['elemento_despesa'])
df_despesas['funcional_programatica_encoded'] = le.fit_transform(df_despesas['funcional_programatica'])

num = ['valor']
scaler = StandardScaler()
df_num = scaler.fit_transform(df_despesas[num])
df_num = pd.DataFrame(df_num, columns=num)

df_modelo = pd.concat([df_despesas[['orgao_unidade','mes','cnpj_encoded','elemento_despesa_encoded','funcional_programatica_encoded']], df_num, df_tfidf_desc], axis=1)
df_modelo

#df_modelo = df_modelo.sample(frac=0.1, random_state=42)
#df_modelo.shape

X_train, X_test = train_test_split(df_modelo, test_size=0.3, random_state=42)

model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X_train)

isoforest_train_anomaly_score = model.decision_function(X_train)
isoforest_train_outlier_pred = model.predict(X_train)

isoforest_test_anomaly_score = model.decision_function(X_test)
isoforest_test_outlier_pred = model.predict(X_test)

# Construção do DataFrame de resultados
isoforest_train_outlier = pd.concat([pd.DataFrame(isoforest_train_outlier_pred,
                                                  columns=['outlier_pred'],
                                                  index=X_train.index),
                                     pd.DataFrame(isoforest_train_anomaly_score,
                                                  columns=['anomaly_score'],
                                                  index=X_train.index)],
                                    axis=1)

isoforest_train_outlier

isoforest_test_outlier = pd.concat([pd.DataFrame(isoforest_test_outlier_pred,
                                                 columns=['outlier_pred'],
                                                 index=X_test.index),
                                    pd.DataFrame(isoforest_test_anomaly_score,
                                                 columns=['anomaly_score'],
                                                 index=X_test.index)],
                                   axis=1)

isoforest_test_outlier

# Incorporação da predição de outliers
df_scored_isoforest_train = df_despesas.join(isoforest_train_outlier)
df_scored_isoforest_test = df_despesas.join(isoforest_test_outlier)

# Concatenar os dataframes filtrados

df_scored_isoforest_train.dropna(inplace=True)
df_scored_isoforest_test.dropna(inplace=True)

base = pd.concat([df_scored_isoforest_train, df_scored_isoforest_test], ignore_index=True)

base

# Filtrar apenas as linhas onde outlier_pred = -1
anomalias_train = df_scored_isoforest_train[df_scored_isoforest_train['outlier_pred'] == -1]
anomalias_test = df_scored_isoforest_test[df_scored_isoforest_test['outlier_pred'] == -1]

# Concatenar os dataframes filtrados
anomalias = pd.concat([anomalias_train, anomalias_test], ignore_index=True)

anomalias.head()

anomalias.shape

anomalias.to_excel('anomalias.xlsx', index=False)

