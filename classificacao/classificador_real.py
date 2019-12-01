from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import db_config
import mysql.connector
from mysql.connector import Error
from pprint import pprint
import re
import matplotlib.pyplot as plt
from pprint import pprint

import numpy as np
np.set_printoptions(suppress=True)


STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 
'ali', 'lo', 'lhe', 'aí']

def get_connection():
    return mysql.connector.connect(
        host=db_config.HOST,
        database=db_config.DATABASE,
        user=db_config.USER,
        password=db_config.PASSWORD,
        charset=db_config.CHARSET
    )

class Classificador:
    def __init__(self, alfa, tolerancia = 0):
        self.alfa = alfa
        self.tolerancia = tolerancia
        self.vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)
        self.dados, self.respostas = self.pre_processamento()
        self.realizar_treinamento()


    def obter_dados(self):
        connection = get_connection()
        
        cursor = connection.cursor()

        cursor.execute("SELECT text, sentimento FROM tweet_treinamento")
        result = cursor.fetchall()

        return result


    def dividir_dados(self, dados):
        dados_X = [dado[0] for dado in dados]
        dados_y = [dado[1] for dado in dados]
        return dados_X, dados_y

    def pre_processamento(self):
        dados = self.obter_dados()
        retorno = []
        for i in range(len(dados)):
            texto = dados[i][0]
            texto = re.sub("@jairbolsonaro", "jairbolsonaro", texto)
            texto = re.sub("@\w", "", texto)
            texto = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\$)*\b', "http", texto)
            retorno.append([texto, dados[i][1]])

        return self.dividir_dados(dados)
    
    def realizar_treinamento(self):
        self.dados = self.vetorizador.fit_transform(self.dados)
        # return BernoulliNB(alpha=alfa).fit(dados, respostas)
        self.classificador = MultinomialNB(alpha=self.alfa).fit(self.dados, self.respostas)

    def analisar_frase_tolerancia(self, frase):
        dados_avaliacao_2 = self.vetorizador.transform([frase])
        probabilidades = self.classificador.predict_proba(dados_avaliacao_2)
        predicoes = []
        guess = {
            0: -1,
            1: 0,
            2: 1
        }
        for prob in probabilidades:
            prob_list = list(prob)
            if max(prob_list) < self.tolerancia:
                predicoes.append(0)
            else:
                predicoes.append(guess[prob_list.index(max(prob_list))])

        return predicoes[0]

    def analisar_frase(self, frase):
        return self.classificador.predict(self.vetorizador.transform([frase]))[0]

class Tweet:
    def __init__(self, id, text, user_id):
        self.id = id
        self.text = text
        self.user_id = user_id
        self.sentimento_normal = 0
        self.sentimento = 0

def get_tweets():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, text, user_id FROM tweet WHERE sentimento is null LIMIT 100")
    result = cursor.fetchall()

    retorno = []
    for args in result:
        retorno.append(Tweet(*args))
    return retorno

def update_tweet(tweet):
    print(f"UPDATE tweet SET sentimento = {tweet.sentimento}, sentimento_normal = {tweet.sentimento_normal} WHERE id = {tweet.id}")
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"UPDATE tweet SET sentimento = {tweet.sentimento}, sentimento_normal = {tweet.sentimento_normal} WHERE id = {tweet.id}")
    connection.commit()

def converter_sentimento(sentimento):
    sentimento_retorno = "+ 0"
    if sentimento == -1:
        sentimento_retorno = "- 1"
    elif sentimento == 1:
        sentimento_retorno = "+ 1"
    return sentimento_retorno

def update_user(tweet):
    print(f"UPDATE user SET sentimento = sentimento {converter_sentimento(tweet.sentimento)}, sentimento_normal = sentimento_normal {converter_sentimento(tweet.sentimento_normal)} WHERE id = {tweet.user_id}")
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(f"UPDATE user SET sentimento = {converter_sentimento(tweet.sentimento)}, sentimento_normal = {converter_sentimento(tweet.sentimento_normal)} WHERE id = {tweet.user_id};")
    connection.commit()


classificador_normal = Classificador(0.2)
classificador_tolerancia = Classificador(0.5, 0.7)

while True:
    tweets = get_tweets()
    print("ahoy")
    for tweet in tweets:
        # classificar
        tweet.sentimento_normal = classificador_normal.analisar_frase(tweet.text)
        tweet.sentimento = classificador_tolerancia.analisar_frase_tolerancia(tweet.text)
        
        # update tweet
        update_tweet(tweet)

        # update usuario
        update_user(tweet)

        exit(0)

print(classificador_normal.analisar_frase("BIROLIRO FDP"))