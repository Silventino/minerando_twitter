import mysql.connector
from mysql.connector import Error
import db_config
import random

class Tweet():
	def __init__(self, id, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, favourites_count, retweet_count, quote_count, reply_count, created_at, treinamento, sentimento):
		self.id = id
		self.id_twitter = id_twitter
		self.user_id = user_id
		self.is_retweet = is_retweet
		self.is_quote = is_quote
		self.text = text
		self.ref_quote = ref_quote
		self.ref_retweet = ref_retweet
		self.favourites_count = favourites_count
		self.retweet_count = retweet_count
		self.quote_count = quote_count
		self.reply_count = reply_count
		self.created_at = created_at
		self.treinamento = treinamento
		self.sentimento = sentimento




class ClassificadorManual():
	def __init__(self, api = None):
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

	def getTweet(self):
		mycursor = self.getConnection().cursor()
		achou = False
		while(not achou):
			id_random = random.randint(1, 26000000)
			# print(id_random)
			mycursor.execute("SELECT * FROM tweet WHERE id=" + str(id_random) + " LIMIT 1")
			myresult = mycursor.fetchall()

			if(len(myresult) > 0):
				args = myresult[0]
				tweet = Tweet(*args)
				# print(tweet.text)
				if(tweet.is_retweet == 1):
					# print("IS RT")
					mycursor.execute("SELECT * FROM tweet WHERE id=" + str(tweet.ref_retweet) + " LIMIT 1")
					myresult = mycursor.fetchall()
					args = myresult[0]
					tweet_rt = Tweet(*args)
					tweet.text = tweet_rt.text

				return tweet
	
	def salvarTweet(self, tweet):
		# try:
		connection = self.getConnection()
		cursor = connection.cursor()
		
		mySql_insert_query = """INSERT INTO tweet_treinamento (id, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, treinamento, sentimento) 
								VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
		recordTuple = (tweet.id, tweet.id_twitter, tweet.user_id, tweet.is_retweet, tweet.is_quote, tweet.text, tweet.ref_quote, tweet.ref_retweet, tweet.quote_count, tweet.reply_count, tweet.retweet_count, tweet.favourites_count, tweet.created_at, tweet.treinamento, tweet.sentimento)
		cursor.execute(mySql_insert_query, recordTuple)

		connection.commit()

		inserted_id = cursor.lastrowid

		return inserted_id
		# except:
		# 	print("Erro ao salvar tweet classificado")
		# 	return 0

			
def classificar():
	x = ClassificadorManual()
	while(True):
		tweet = x.getTweet()

		print("\n")
		print(tweet.text)
		print("\n")
		desejaClassificar = input("Deseja classificar o Tweet? (s/n)")
		if(desejaClassificar == "s"):
			tweet.treinamento = 1
			sentimento = input("O sentimento do Tweet é positivo ou negativo? (s = positivo/ n = negativo)")
			if(sentimento == "s"):
				tweet.sentimento = 1
			elif(sentimento == "n"):
				tweet.sentimento = 0

			if(tweet.sentimento != None):
				x.salvarTweet(tweet)
		else:
			print("Ok.")


classificar()