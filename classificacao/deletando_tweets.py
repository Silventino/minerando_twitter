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

	def getTweets(self, id_tweet=None):
		mycursor = self.getConnection().cursor()
		if(id_tweet == None):
			mycursor.execute(
				"""
				SELECT * FROM tweet 
				WHERE 
				(
					LOCATE('presidente',text) > 0 OR
					LOCATE('mito',text) > 0
				)
				AND
				(
					LOCATE('Bolsonaro',text) = 0 AND
					LOCATE('bolsonaro',text) = 0 AND
					LOCATE('Bolsomito',text) = 0 AND
					LOCATE('bolsomito',text) = 0 AND
					LOCATE('Bozo',text) = 0 AND
					LOCATE('bozo',text) = 0 AND
					LOCATE('Bonoro',text) = 0 AND
					LOCATE('bonoro',text) = 0 AND
					LOCATE('Bozonaro',text) = 0 AND
					LOCATE('bozonaro',text) = 0 AND
					LOCATE('Bonossauro',text) = 0 AND
					LOCATE('bonossauro',text) = 0 AND
					LOCATE('biroliro',text) = 0 AND
					LOCATE('Biroliro',text) = 0 AND
					LOCATE('Jair',text) = 0 AND
					LOCATE('Mitonaro',text) = 0 AND
					LOCATE('Capitão',text) = 0 AND
					LOCATE('Bolodemilho',text) = 0 AND
					LOCATE('bolodemilho',text) = 0 AND
					LOCATE('Bolsonitro',text) = 0 AND
					LOCATE('bolsonitro',text) = 0 AND
					LOCATE('Bonobo',text) = 0 AND
					LOCATE('Jair Bolar',text) = 0 AND
					LOCATE('bonobo',text) = 0 AND
					LOCATE('Salnorabo',text) = 0 AND
					LOCATE('Bonaro',text) = 0 AND
					LOCATE('bonaro',text) = 0 AND
					LOCATE('Boniro',text) = 0 AND
					LOCATE('boniro',text) = 0 AND
					LOCATE('Bonaldo',text) = 0 AND
					LOCATE('bonaldo',text) = 0 AND
					LOCATE('Boçanaro',text) = 0 AND
					LOCATE('boçanaro',text) = 0 AND
					LOCATE('Bosoro',text) = 0 AND
					LOCATE('bosoro',text) = 0 AND
					LOCATE('Bolnossauro',text) = 0 AND
					LOCATE('bolnossauro',text) = 0 AND
					LOCATE('Bolsomario',text) = 0 AND
					LOCATE('bolsomario',text) = 0 AND
					LOCATE('bolsonaristas',text) = 0 AND
					LOCATE('jairbolsonaro',text) = 0 AND
					LOCATE('bozonaro',text) = 0 AND
					LOCATE('burronaro',text) = 0 AND
					LOCATE('bolsonaro',text) = 0 AND
					LOCATE('presidente da república',text) = 0
				)
				ORDER BY id limit 100;
				"""
			)
		else:
			mycursor.execute(
				f"""
				SELECT * FROM tweet 
				WHERE 
				id > {id_tweet} AND 
				(
					LOCATE('presidente',text) > 0 OR
					LOCATE('mito',text) > 0
				)
				AND
				(
					LOCATE('Bolsonaro',text) = 0 AND
					LOCATE('bolsonaro',text) = 0 AND
					LOCATE('Bolsomito',text) = 0 AND
					LOCATE('bolsomito',text) = 0 AND
					LOCATE('Bozo',text) = 0 AND
					LOCATE('bozo',text) = 0 AND
					LOCATE('Bonoro',text) = 0 AND
					LOCATE('bonoro',text) = 0 AND
					LOCATE('Bozonaro',text) = 0 AND
					LOCATE('bozonaro',text) = 0 AND
					LOCATE('Bonossauro',text) = 0 AND
					LOCATE('bonossauro',text) = 0 AND
					LOCATE('biroliro',text) = 0 AND
					LOCATE('Biroliro',text) = 0 AND
					LOCATE('Jair',text) = 0 AND
					LOCATE('Mitonaro',text) = 0 AND
					LOCATE('Capitão',text) = 0 AND
					LOCATE('Bolodemilho',text) = 0 AND
					LOCATE('bolodemilho',text) = 0 AND
					LOCATE('Bolsonitro',text) = 0 AND
					LOCATE('bolsonitro',text) = 0 AND
					LOCATE('Bonobo',text) = 0 AND
					LOCATE('Jair Bolar',text) = 0 AND
					LOCATE('bonobo',text) = 0 AND
					LOCATE('Salnorabo',text) = 0 AND
					LOCATE('Bonaro',text) = 0 AND
					LOCATE('bonaro',text) = 0 AND
					LOCATE('Boniro',text) = 0 AND
					LOCATE('boniro',text) = 0 AND
					LOCATE('Bonaldo',text) = 0 AND
					LOCATE('bonaldo',text) = 0 AND
					LOCATE('Boçanaro',text) = 0 AND
					LOCATE('boçanaro',text) = 0 AND
					LOCATE('Bosoro',text) = 0 AND
					LOCATE('bosoro',text) = 0 AND
					LOCATE('Bolnossauro',text) = 0 AND
					LOCATE('bolnossauro',text) = 0 AND
					LOCATE('Bolsomario',text) = 0 AND
					LOCATE('bolsomario',text) = 0 AND
					LOCATE('bolsonaristas',text) = 0 AND
					LOCATE('jairbolsonaro',text) = 0 AND
					LOCATE('bozonaro',text) = 0 AND
					LOCATE('burronaro',text) = 0 AND
					LOCATE('bolsonaro',text) = 0 AND
					LOCATE('presidente da república',text) = 0
				)
				ORDER BY id limit 100;
				"""
			)

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
		
		mySql_insert_query = """INSERT IGNORE INTO tweet_deletado (id, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, treinamento, sentimento) 
								VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
		recordTuple = (tweet.id, tweet.id_twitter, tweet.user_id, tweet.is_retweet, tweet.is_quote, tweet.text, tweet.ref_quote, tweet.ref_retweet, tweet.quote_count, tweet.reply_count, tweet.retweet_count, tweet.favourites_count, tweet.created_at, tweet.treinamento, tweet.sentimento)
		cursor.execute(mySql_insert_query, recordTuple)

		connection.commit()

		inserted_id = cursor.lastrowid

		return inserted_id
		# except:
		# 	print("Erro ao salvar tweet classificado")
		# 	return 0

	def salvarRetweetDeletado(self, tweet_id, user_id):
		# try:
		connection = self.getConnection()
		cursor = connection.cursor()
		
		mySql_insert_query = """INSERT INTO retweet_deletado (tweet_id, user_id) 
								VALUES (%s, %s) """
		recordTuple = (tweet_id, user_id)
		cursor.execute(mySql_insert_query, recordTuple)

		connection.commit()

		inserted_id = cursor.lastrowid

		return inserted_id
		# except:
		# 	print("Erro ao salvar tweet classificado")
		# 	return 0

	def deletarTweet(self, tweet):
		# print("\n\nVou deletar: ", tweet.text)
		# confirm = input("Pode mandar ver?")
		# if(confirm != "s"):
		# 	return
		
		self.salvarTweetDeletado(tweet)

		connection = self.getConnection()
		cursor = connection.cursor()
		print("DELETE FROM tweet WHERE id=" + str(tweet.id))
		cursor.execute("DELETE FROM tweet WHERE id=" + str(tweet.id))
		print("Principal deleted")


		cursor.execute("SELECT * FROM retweet WHERE tweet_id=" + str(tweet.id))
		retweets = cursor.fetchall()
		for rt in retweets:
			self.salvarRetweetDeletado(rt[0], rt[1])
			print("DELETE FROM retweet WHERE tweet_id=" + str(rt[0]) + " and user_id=" + str(rt[1]))
			cursor.execute("DELETE FROM retweet WHERE tweet_id=" + str(rt[0]) + " and user_id=" + str(rt[1]))


		# result_1 = []
		# if(tweet.ref_retweet != None):
		# 	cursor.execute("SELECT * FROM tweet WHERE ref_retweet=" + str(tweet.ref_retweet))
		# 	result_1 = cursor.fetchall()

		# for t in result_1:
		# 	ref_tweet = Tweet(*t)
		# 	if(not self.filtrar(ref_tweet)):
		# 		self.salvarTweetDeletado(ref_tweet)
		# 		cursor.execute("DELETE FROM tweet WHERE id=" + str(ref_tweet.id))
		# 		print("RT deleted")

		
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
		# print("TWEET APAGADO: ", tweet.text)

		# cursor.execute("DELETE FROM tweet WHERE ref=" + str(tweet.id))
	

			
def classificar():
	x = ClassificadorManual()
	ultimo_id = 0
	while(True):
		print("VOU BUSCAR " + str(ultimo_id))
		tweets = x.getTweets(ultimo_id)
		# print(tweets)
		if(tweets == None or len(tweets) == 0):
			exit(0)
		# print("BUSQUEI")

		for args in tweets:
			tweet = Tweet(*args)
			# print("\n")
			# print(tweet.text)
			# print("\n")

			if(x.filtrar(tweet)):
				ultimo_id = tweet.id
				continue
				
			tweet.treinamento = 1
			# sentimento = input("Pode apagar? (d = apagar)")
			# if(sentimento == "s"):
			# 	tweet.sentimento = 1
			# elif(sentimento == "n"):
			# 	tweet.sentimento = 0
			# if(sentimento == "d"):
			# 	print("VOU APAGAR SAPORRA")
			x.deletarTweet(tweet)
			# continue

			# if(tweet.sentimento != None):
			# 	x.salvarTweet(tweet)
			
			print("Ok.")


classificar()
