import mysql.connector
from mysql.connector import Error
import db_config
import random
import sys

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
		self.queries = self.getQueries()
	
	def getQueries(self, queries_f='./queries.txt'):
		'''
		Read the file with the keys for Twitter API and return a dictionary with them.
		'''
		try:
			queries_file = open(queries_f)
			queries = queries_file.readlines()
			# Clean \n
			queries = [query.rstrip() for query in queries]
		except Exception as e:
			print('Problem found opening the file '+ queries_f +'.')
			print(e)
			sys.exit(1)

		return queries

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

	def getTweet(self, id):
		mycursor = self.getConnection().cursor()
		achou = False
		while(not achou):
			id_random = random.randint(1, 136130373)
			# print(id_random)
			mycursor.execute("SELECT * FROM tweet WHERE LOCATE('https://t.co/',text) > 0 AND id > " + str(id) + " LIMIT 1")
			myresult = mycursor.fetchall()

			return myresult

	def getUsuario(self, id):
		mycursor = self.getConnection().cursor()
		achou = False
		while(not achou):
			id_random = random.randint(1, 136130373)
			# print(id_random)
			mycursor.execute("SELECT * FROM user WHERE id=" + str(id))
			myresult = mycursor.fetchall()

			return myresult

	# retorna TRUE se o tweet taokei
	def filtrar(self, tweet):
		lower_text = tweet.text.lower()
		return any(q.lower() in lower_text for q in self.queries)

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

	def salvarTweetDeletado(self, tweet):
		# try:
		connection = self.getConnection()
		cursor = connection.cursor()
		
		mySql_insert_query = """INSERT INTO tweet_deletado (id, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, treinamento, sentimento) 
								VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
		recordTuple = (tweet.id, tweet.id_twitter, tweet.user_id, tweet.is_retweet, tweet.is_quote, tweet.text, tweet.ref_quote, tweet.ref_retweet, tweet.quote_count, tweet.reply_count, tweet.retweet_count, tweet.favourites_count, tweet.created_at, tweet.treinamento, tweet.sentimento)
		cursor.execute(mySql_insert_query, recordTuple)

		connection.commit()

		inserted_id = cursor.lastrowid

		return inserted_id
		# except:
		# 	print("Erro ao salvar tweet classificado")
		# 	return 0

	def deletarTweet(self, tweet):
		print("\n\nVou deletar: ", tweet.text)
		confirm = input("Pode mandar ver?")
		if(confirm != "s"):
			return
		
		self.salvarTweetDeletado(tweet)

		connection = self.getConnection()
		cursor = connection.cursor()
		cursor.execute("DELETE FROM tweet WHERE id=" + str(tweet.id))
		print("Principal deleted")

		result_1 = []
		if(tweet.ref_retweet != None):
			cursor.execute("SELECT * FROM tweet WHERE ref_retweet=" + str(tweet.ref_retweet))
			result_1 = cursor.fetchall()

		for t in result_1:
			ref_tweet = Tweet(*t)
			if(not self.filtrar(ref_tweet)):
				self.salvarTweetDeletado(ref_tweet)
				cursor.execute("DELETE FROM tweet WHERE id=" + str(ref_tweet.id))
				print("RT deleted")

		
		# result_2 = []
		# if(tweet.ref_quote != None):
		# 	cursor.execute("SELECT * FROM tweet WHERE ref_quote=" + str(tweet.ref_quote))
		# 	result_2 = cursor.fetchall()

		# for t in result_2:
		# 	ref_tweet = Tweet(*t)
		# 	if(not self.filtrar(ref_tweet)):
		# 		self.salvarTweetDeletado(ref_tweet)
		# 		cursor.execute("DELETE FROM tweet WHERE id=" + str(ref_tweet.id))
		

		connection.commit()
		print("TWEET APAGADO: ", tweet.text)

		# cursor.execute("DELETE FROM tweet WHERE ref=" + str(tweet.id))
	

			
def classificar():
	ultimo_id_tweet = 0
	# ultimo_id_user = 0
	
	x = ClassificadorManual()
	while(True):
		tweets = x.getTweet(ultimo_id_tweet)
		if(tweets == None):
			continue

		for args in tweets:
			tweet = Tweet(*args)
			ultimo_id_tweet = tweet.id
			print("\n")
			print(tweet.text)
			print("\n")

			user = x.getUsuario(tweet.user_id)[0]
			# ultimo_id_user = user[0]
			print(user[2])
			print(user[3])
			print("\n")

			
			tweet.treinamento = 1
			sentimento = input("O sentimento do Tweet é positivo ou negativo? (s = positivo/ n = negativo)")
			if(sentimento == "s"):
				tweet.sentimento = 1
			elif(sentimento == "n"):
				tweet.sentimento = 0
			elif(sentimento == "d"):
				print("VOU APAGAR SAPORRA")
				# x.deletarTweet(tweet)
				continue

			# if(tweet.sentimento != None):
			# 	x.salvarTweet(tweet)
			
			print("Ok.")


classificar()
