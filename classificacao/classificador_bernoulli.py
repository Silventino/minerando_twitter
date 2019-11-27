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
from pprint import pprint

STOPWORDS = ['de', 'a', 'o', 'que', 'e', 'é', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 'por', 'mais', 'as', 'dos', 'como', 'mas', 'ao', 'ele', 'das', 'à', 'seu', 'sua', 'ou', 'quando', 'muito', 'nos', 'já', 'eu', 'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'depois', 'sem', 'mesmo', 'aos', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'você', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'numa', 'pelos', 'elas', 'qual', 'nós', 'lhe', 'deles', 'essas', 'esses', 'pelas', 'este', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 'estivermos', 'estiverem', 'hei', 'há', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 'teríamos', 'teriam', 
'ali', 'lo', 'lhe', 'aí']


def obter_dados():
    connection = mysql.connector.connect(host=db_config.HOST,
                                    database=db_config.DATABASE,
                                    user=db_config.USER,
                                    password=db_config.PASSWORD,
                                    charset=db_config.CHARSET)
	
    cursor = connection.cursor()

    cursor.execute("SELECT text, sentimento FROM tweet_treinamento where sentimento=1 limit 200")
    result = cursor.fetchall()

    cursor.execute("SELECT text, sentimento FROM tweet_treinamento where sentimento=0 limit 100")
    result.extend(cursor.fetchall())

    cursor.execute("SELECT text, sentimento FROM tweet_treinamento where sentimento=-1 limit 200")
    result.extend(cursor.fetchall())

    # cursor.execute("SELECT text, sentimento FROM tweet_treinamento")
    # result = cursor.fetchall()

    # cursor.execute("SELECT text, sentimento FROM tweet_treinamento where ")
    # result = cursor.fetchall()

    # pprint(result)
    return result


def dividir_dados_para_treino_e_validacao(dados, test_size,stratify = True):
    dados_X = [dado[0] for dado in dados]
    dados_y = [dado[1] for dado in dados]
    if(stratify):
        X_train, X_test, y_train, y_test = train_test_split(dados_X, dados_y, test_size=test_size, random_state=123, stratify=dados_y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(dados_X, dados_y, test_size=test_size, random_state=123)

    return X_train, X_test, y_train, y_test

def pre_processamento(test_size, stratify = True):
    dados = obter_dados()
    retorno = []
    for i in range(len(dados)):
        texto = dados[i][0]
        texto = re.sub("@\w", "", texto)
        texto = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\$)*\b', "http", texto)
        retorno.append([texto, dados[i][1]])

    return dividir_dados_para_treino_e_validacao(dados, test_size, stratify)
    
def realizar_treinamento(dados_treino, respostas_treino, vetorizador, alfa = 0.5):
    dados_treino = vetorizador.fit_transform(dados_treino)
    return BernoulliNB(alpha=alfa).fit(dados_treino, respostas_treino)

def realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador):
    dados_avaliacao = vetorizador.transform(dados_avaliacao)
    return classificador.predict(dados_avaliacao), classificador.score(dados_avaliacao, respostas_avaliacao)

def realizar_teste_novo(dados_avaliacao, respostas_avaliacao, classificador, vetorizador):
    dados_avaliacao = vetorizador.transform(dados_avaliacao)
    probabilidades = classificador.predict_proba(dados_avaliacao)
    predicoes = []
    guess = {
        0: -1,
        1: 0,
        2: 1
    }
    for prob in probabilidades:
        prob_list = list(prob)
        if max(prob_list) < 0.6:
            predicoes.append(0)
        else:
            
            predicoes.append(guess[prob_list.index(max(prob_list))])
    
    acertos = 0
    for i in range(len(predicoes)):
        if(predicoes[i] == respostas_avaliacao[i]):
            acertos = acertos + 1

    return predicoes, acertos/len(predicoes)

def testar_prob(dados_avaliacao, respostas_avaliacao, classificador, vetorizador):
    dados_avaliacao = vetorizador.transform(dados_avaliacao)
    return classificador.predict_proba(dados_avaliacao)

def testar_predict(dados_avaliacao, respostas_avaliacao, classificador, vetorizador):
    dados_avaliacao = vetorizador.transform(dados_avaliacao)
    return classificador.predict(dados_avaliacao)

def exibir_resultado(valor):
    frase, resultado = valor
    print(frase, ":", resultado[0])

def analisar_frase_prob(classificador, vetorizador, frase):
    return frase, classificador.predict_proba(vetorizador.transform([frase]))

def analisar_frase(classificador, vetorizador, frase):
    return frase, classificador.predict(vetorizador.transform([frase]))

def calcular_estatisticas(predicoes, respostas):

    # POSIÇÕES
    # 0 -> Negativo
    # 1 -> Neutro
    # 2 -> Positivo
    posicoes = {
        -1:0,
        0:1,
        1:2
    }
    matriz = [
        [0,0,0],
        [0,0,0],
        [0,0,0]
    ]
    for i in range(len(predicoes)):
        matriz[posicoes[predicoes[i]]][posicoes[respostas[i]]] += 1


    return matriz

def plotar_heatmap(matriz_1, matriz_2):
    labels = ["Positivo", "Neutro", "Negativo"]
    matriz_1 = np.array(matriz_1)

    fig, ax = plt.subplots(2)
    im = ax[0].imshow(matriz_1)

    # We want to show all ticks...
    ax[0].set_xticks(np.arange(len(labels)))
    ax[0].set_yticks(np.arange(len(labels)))
    # ... and label them with the respective list entries
    ax[0].set_xticklabels(labels)
    ax[0].set_yticklabels(labels)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax[0].get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax[0].text(j, i, matriz_1[i, j],
                        ha="center", va="center", color="w")

    ax[0].set_title("Harvest of local farmers (in tons/year)")


    

    matriz_2 = np.array(matriz_2)

    im = ax[1].imshow(matriz_1)

    # We want to show all ticks...
    ax[1].set_xticks(np.arange(len(labels)))
    ax[1].set_yticks(np.arange(len(labels)))
    # ... and label them with the respective list entries
    ax[1].set_xticklabels(labels)
    ax[1].set_yticklabels(labels)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax[1].get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax[1].text(j, i, matriz_2[i, j],
                        ha="center", va="center", color="w")

    ax[1].set_title("Harvest of local farmers (in tons/year)")



    fig.tight_layout()
    
    plt.show()
    



np.set_printoptions(suppress=True)
# alfas= [0.2]
alfas= []
alfa = 0
variacao_alfa = 0.1
while alfa <= 1:
    alfas.append(alfa)
    alfa = round(alfa + variacao_alfa, 2)


################# GRAFICO VARIANDO TEST SIZE ########################
sizes = [0.2]
# sizes = []
# test_size = 0.1
# variacao_teste_size = 0.1
# while test_size < 1:
#     sizes.append(test_size)
#     test_size = round(test_size + variacao_teste_size, 1)


resultados = []
for test_size in sizes:
    dados_treino, dados_avaliacao, respostas_treino, respostas_avaliacao = pre_processamento(test_size ,True)
    # dados_avaliacao = [dados_avaliacao[i] for i in range(len(dados_avaliacao)) if respostas_avaliacao[i] != 0]
    # dados_treino = [dados_treino[i] for i in range(len(dados_treino)) if respostas_treino[i] != 0]
    # respostas_avaliacao = [respostas_avaliacao[i] for i in range(len(respostas_avaliacao)) if respostas_avaliacao[i] != 0]
    # respostas_treino = [respostas_treino[i] for i in range(len(respostas_treino)) if respostas_treino[i] != 0]
    vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)

    resultado = []
    for alfa in alfas:
        classificador = realizar_treinamento(dados_treino, respostas_treino, vetorizador, alfa)
        predicoes_1, acuracia_1 = realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
        print(acuracia_1)
        matriz_1 = calcular_estatisticas(predicoes_1, respostas_avaliacao)

        predicoes_2, acuracia_2 = realizar_teste_novo(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
        print(acuracia_2)
        matriz_2 = calcular_estatisticas(predicoes_2, respostas_avaliacao)

        plotar_heatmap(matriz_1, matriz_2)
        # prob = testar_prob(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
        # pred = testar_predict(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
        # prob = [prob[i] for i in range(len(pred)) if pred[i] != 0]
        # printar = [dados_avaliacao[i] for i in range(len(pred)) if pred[i] != 0]
        # pred = [pred[i] for i in range(len(pred)) if pred[i] != 0]
        # for i in range(len(pred)):
        #     print(printar[i])
        #     print(pred[i])
        #     print(prob[i])
        #     print("\n")

        # resultado.append(acuracia)
    # resultados.append(resultado)
    
    

fig, ax = plt.subplots()
plt.xlabel("Alfa")
plt.ylabel("Acurácia")

for i in range(len(resultados)):
    line, = ax.plot(alfas, resultados[i], label='Tamanho teste: ' + str(sizes[i]))

ax.legend()
# plt.show()
#####################################################################



################  GRAFICOS VARIANDO O ALFA E ESTRATIFICACAO ########################
# dados_treino, dados_avaliacao, respostas_treino, respostas_avaliacao = pre_processamento(True)
# vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)

# alfas = []
# resultados = []
# alfa = 0
# variacao_alfa = 0.05
# while alfa <= 1:
#     alfas.append(alfa)
#     classificador = realizar_treinamento(dados_treino, respostas_treino, vetorizador, alfa)
#     acuracia = realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador)
#     resultados.append(acuracia)
#     print("ALFA", alfa)
#     print("ACURACIA", acuracia)
#     alfa = alfa + variacao_alfa


# dados_treino, dados_avaliacao, respostas_treino, respostas_avaliacao = pre_processamento(False)
# vetorizador_2 = CountVectorizer(binary = 'true', stop_words=STOPWORDS)

# alfas_2 = []
# resultados_2 = []
# alfa = 0
# while alfa <= 1:
#     alfas_2.append(alfa)
#     classificador = realizar_treinamento(dados_treino, respostas_treino, vetorizador_2, alfa)
#     acuracia = realizar_teste(dados_avaliacao, respostas_avaliacao, classificador, vetorizador_2)
#     resultados_2.append(acuracia)
#     print("ALFA", alfa)
#     print("ACURACIA", acuracia)
#     alfa = round(alfa + variacao_alfa, 2)

# fig, ax = plt.subplots()

# line1, = ax.plot(alfas, resultados, label='Usando estratificação')
# line2, = ax.plot(alfas_2, resultados_2, label='Não usando estratificação')

# plt.xlabel("Alfa")
# plt.ylabel("Acurácia")

# ax.legend()
# plt.show()
###########################################################################################



# dados_treino, dados_avaliacao, respostas_treino, respostas_avaliacao = pre_processamento(0.2, True)
# vetorizador = CountVectorizer(binary = 'true', stop_words=STOPWORDS)
# classificador = realizar_treinamento(dados_treino, respostas_treino, vetorizador, 0.5)
# print( analisar_frase_prob(classificador, vetorizador," EU AMO ESSE PRESIDENTE #BolsonaroPresidenteAte2026"))
# print( analisar_frase(classificador, vetorizador," EU AMO ESSE PRESIDENTE #BolsonaroPresidenteAte2026"))
# print( analisar_frase_prob(classificador, vetorizador,"Hoje eu queria comer lasanha"))
# print( analisar_frase(classificador, vetorizador,"Hoje eu queria comer lasanha"))


# # print(classificador.get_params())
# # print(classificador.feature_log_prob_)
# pos_class_prob_sorted = classificador.feature_log_prob_[1, :].argsort()
# words = np.take(vetorizador.get_feature_names(), pos_class_prob_sorted[:10])
# print(words)
# # print(vetorizador.get_feature_names())
