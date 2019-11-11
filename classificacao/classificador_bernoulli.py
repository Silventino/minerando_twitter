from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
import db_config
import mysql.connector
from mysql.connector import Error
import numpy as np
from pprint import pprint
import re

STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 
'ali', 'lo', 'lhe', 'aí']


def obter_dados():
    connection = mysql.connector.connect(host=db_config.HOST,
                                    database=db_config.DATABASE,
                                    user=db_config.USER,
                                    password=db_config.PASSWORD,
                                    charset=db_config.CHARSET)
	
    cursor = connection.cursor()
    cursor.execute("SELECT text, sentimento FROM tweet_treinamento")
    result = cursor.fetchall()
    # pprint(result)
    return result



def dividir_dados_para_treino_e_validacao(dados):
    quantidade_total = len(dados)
    percentual_para_treino = 0.75
    treino = []
    validacao = []

    for indice in range(0, quantidade_total):
        if indice < quantidade_total * percentual_para_treino:
            treino.append(dados[indice])
        else:
            validacao.append(dados[indice])

    return treino, validacao

def pre_processamento():
    dados = obter_dados()
    retorno = []
    for i in range(len(dados)):
        texto = dados[i][0]
        texto = re.sub("@\w", "", texto)
        texto = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\$)*\b', "", texto)
        retorno.append([texto, dados[i][1]])
        print(texto)

    # return dividir_dados_para_treino_e_validacao(dados)
    
    return retorno, retorno


def realizar_treinamento(registros_de_treino, vetorizador):
    treino_comentarios = [registro_treino[0] for registro_treino in registros_de_treino]
    treino_respostas = [registro_treino[1] for registro_treino in registros_de_treino]

    treino_comentarios = vetorizador.fit_transform(treino_comentarios)

    return BernoulliNB(alpha=0).fit(treino_comentarios, treino_respostas)
    # return BernoulliNB(alpha=100.0, fit_prior=True).fit(treino_comentarios, treino_respostas)
    # return BernoulliNB().fit(treino_comentarios, treino_respostas)

def exibir_resultado(valor):
    frase, resultado = valor
    print(frase, ":", resultado[0])
    # resultado = "Frase positiva" if resultado[0] == '1' else "Frase negativa"
    # print(frase, ":", resultado)

def analisar_frase(classificador, vetorizador, frase):
    return frase, classificador.predict(vetorizador.transform([frase]))


registros_de_treino, registros_para_avaliacao = pre_processamento()
# vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)
vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)
classificador = realizar_treinamento(registros_de_treino, vetorizador)

# print(classificador.get_params())
# print(classificador.feature_log_prob_)
pos_class_prob_sorted = classificador.feature_log_prob_[1, :].argsort()
words = np.take(vetorizador.get_feature_names(), pos_class_prob_sorted[:10])
print(words)
# print(vetorizador.get_feature_names())

# exibir_resultado( analisar_frase(classificador, vetorizador,"this is the best movie"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"this is the worst movie"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"awesome!"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"10/10"))
exibir_resultado( analisar_frase(classificador, vetorizador,"Eu te amo Jair você é um mito"))
# print( analisar_frase(classificador, vetorizador,"janeiro janeiro familicia"))
exibir_resultado( analisar_frase(classificador, vetorizador,"bozo bozonaro"))
exibir_resultado( analisar_frase(classificador, vetorizador,"#BolsonaroPresidenteAte2026"))

# print(vetorizador.transform(["tesando i 2 3 4"]))
