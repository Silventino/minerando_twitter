from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import db_config
import mysql.connector
from mysql.connector import Error
import numpy as np
from pprint import pprint
import re
import numpy as np
import matplotlib.pyplot as plt

STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 
'ali', 'lo', 'lhe', 'aí']


def obter_dados():
    connection = mysql.connector.connect(host=db_config.HOST,
                                    database=db_config.DATABASE,
                                    user=db_config.USER,
                                    password=db_config.PASSWORD,
                                    charset=db_config.CHARSET)
	
    cursor = connection.cursor()
    cursor.execute("SELECT text, sentimento FROM tweet_treinamento where sentimento=1 or sentimento=-1")
    result = cursor.fetchall()
    # pprint(result)
    return result



def dividir_dados_para_treino_e_validacao(dados, stratify = True):
    dados_X = [dado[0] for dado in dados]
    dados_y = [dado[1] for dado in dados]
    if(stratify):
        X_train, X_test, y_train, y_test = train_test_split(dados_X, dados_y, test_size=0.2, random_state=123, stratify=dados_y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(dados_X, dados_y, test_size=0.2, random_state=123)

    return X_train, X_test, y_train, y_test
    # dados = shuf
    # quantidade_total = len(dados)
    # percentual_para_treino = 0.50
    # treino = []
    # validacao = []

    # for indice in range(0, quantidade_total):
    #     if indice < quantidade_total * percentual_para_treino:
    #         treino.append(dados[indice])
    #     else:
    #         validacao.append(dados[indice])

    # return treino, validacao

def pre_processamento():
    dados = obter_dados()
    retorno = []
    for i in range(len(dados)):
        texto = dados[i][0]
        texto = re.sub("@\w", "", texto)
        texto = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\$)*\b', "", texto)
        retorno.append([texto, dados[i][1]])
        # retorno.append(["banana", 2])
        # print(texto)

    return dividir_dados_para_treino_e_validacao(dados)
    
    # return retorno, retorno


def realizar_treinamento(dados_treino, respostas_treino, vetorizador, alfa = 0.5):
    # dados_treino = [registro_treino[0] for registro_treino in registros_de_treino]
    # respostas_treino = [registro_treino[1] for registro_treino in registros_de_treino]
    dados_treino = vetorizador.fit_transform(dados_treino)
    return BernoulliNB(alpha=alfa).fit(dados_treino, respostas_treino)
    # return BernoulliNB(alpha=100.0, fit_prior=True).fit(dados_treino, respostas_treino)
    # return BernoulliNB().fit(dados_treino, respostas_treino)


def realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador):
    # dados_avaliacao = [registro_teste[0] for registro_teste in registros_de_teste]
    # respostas_avaliacao = [registro_teste[1] for registro_teste in registros_de_teste]

    dados_avaliacao = vetorizador.transform(dados_avaliacao)

    return classificador.score(dados_avaliacao, respostas_avaliacao)

def exibir_resultado(valor):
    frase, resultado = valor
    print(frase, ":", resultado[0])
    # resultado = "Frase positiva" if resultado[0] == '1' else "Frase negativa"
    # print(frase, ":", resultado)

def analisar_frase(classificador, vetorizador, frase):
    return frase, classificador.predict(vetorizador.transform([frase]))


dados_treino, dados_avaliacao, respostas_treino, respostas_avaliacao = pre_processamento()

print("quantidade treino:", len(dados_treino))
print("quantidade avaliacao:", len(dados_avaliacao))
# vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)
vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)

alfas = []
resultados = []
alfa = 0
while alfa <= 1:
    alfas.append(alfa)
    classificador = realizar_treinamento(dados_treino, respostas_treino, vetorizador, alfa)
    acuracia = realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
    resultados.append(acuracia)
    print("ALFA", alfa)
    print("ACURACIA", acuracia)
    alfa = alfa + 0.05



# x = np.linspace(0, 10, 500)
# y = np.sin(x)

fig, ax = plt.subplots()

# Using set_dashes() to modify dashing of an existing line
line1, = ax.plot(alfas, resultados, label='Using set_dashes()')
# line1.set_dashes([2, 2, 10, 2])  # 2pt line, 2pt break, 10pt line, 2pt break

# Using plot(..., dashes=...) to set the dashing when creating a line
# line2, = ax.plot(x, y - 0.2, label='Using the dashes parameter')

ax.legend()
plt.show()

# # print(classificador.get_params())
# # print(classificador.feature_log_prob_)
# pos_class_prob_sorted = classificador.feature_log_prob_[1, :].argsort()
# words = np.take(vetorizador.get_feature_names(), pos_class_prob_sorted[:10])
# print(words)
# # print(vetorizador.get_feature_names())

# # exibir_resultado( analisar_frase(classificador, vetorizador,"this is the best movie"))
# # exibir_resultado( analisar_frase(classificador, vetorizador,"this is the worst movie"))
# # exibir_resultado( analisar_frase(classificador, vetorizador,"awesome!"))
# # exibir_resultado( analisar_frase(classificador, vetorizador,"10/10"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"Eu te amo Jair você é um mito"))
# # print( analisar_frase(classificador, vetorizador,"janeiro janeiro familicia"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"bozo bozonaro"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"#BolsonaroPresidenteAte2026"))
# exibir_resultado( analisar_frase(classificador, vetorizador,"banana"))

# # print(vetorizador.transform(["tesando i 2 3 4"]))
