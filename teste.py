from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB
import db_config
import mysql.connector
from mysql.connector import Error

class Database():
    def __init__(self):
        self.connection = None

    def getConnection(self):
        if(self.connection is None):
            self.connection = mysql.connector.connect(host=db_config.HOST,
                                            database=db_config.DATABASE,
                                            user=db_config.USER,
                                            password=db_config.PASSWORD,
                                            charset=db_config.CHARSET)
        else:
            self.connection.ping(True)
        return self.connection
    def getTweetsTeste(self):
        # try:
        connection = self.getConnection()
        cursor = connection.cursor()
        
        mysql_query = """SELECT * FROM tweet_treinamento"""
        # recordTuple = (id_twitter, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified)
        cursor.execute(mysql_query)
        return cursor.fetchall()
        # except Exception as e:
        #     print("ERRO")
        #     pass
        

def realizar_treinamento(registros_de_treino):
    treino_comentarios = [registro_treino[0] for registro_treino in registros_de_treino]
    treino_respostas = [registro_treino[1] for registro_treino in registros_de_treino]

    treino_comentarios = vetorizador.fit_transform(treino_comentarios)

    return BernoulliNB().fit(treino_comentarios, treino_respostas)

def exibir_resultado(valor):
    frase, resultado = valor
    resultado = "Frase positiva" if resultado[0] == '1' else "Frase negativa"
    print(frase, ":", resultado)

def analisar_frase(classificador, vetorizador, frase):
    return frase, classificador.predict(vetorizador.transform([frase]))

database = Database()
print(database.getTweetsTeste())
# registros_de_treino, registros_para_avaliacao = pre_processamento()
# vetorizador = CountVectorizer(binary = 'true')
# classificador = realizar_treinamento(registros_de_treino, vetorizador)
# resultado = classificador.predict(vetorizador.transform(["love this movie!"])