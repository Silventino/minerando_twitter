
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import sys
import json
import mysql.connector
from mysql.connector import Error
# from pprint import pprint
import datetime

from twitter_config import get_auth_api
import db_config
# import mongodb_config as mdb


# def fix_text(text):
# 	'''
# 	To correct the problem with: 'ascii' codec can't encode character
# 	'''
# 	return u''.text.encode('utf-8').strip()

# def get_queries(queries_f='../settings/queries.txt'):

TIMES = [ 'Flamengo', 'Palmeiras', 'Santos', 'Grêmio', 'São Paulo', 'Corinthians', 'Athletico', 'Goiás', 'Bahia', 'Atlético', 'galo', 'Vasco', 'Ceará', 'Fortaleza', 'Fluminense', 'flu', 'Cruzeiro', 'zero', 'Botafogo', 'CSA', 'Chapecoense', 'Chapeco', 'Avaí']
QUERIES_CERTEZA = [ "Bolsonaro", "bolsonaro", "Bolsomito", "bolsomito", "Bozo", "bozo", "Bonoro", "bonoro", "Bozonaro", "bozonaro", "Bonossauro", "bonossauro", "Biroliro", "biroliro", "Jair", "Mitonaro", "Capitão", "Bolodemilho", "bolodemilho", "Bolsonitro", "bolsonitro", "Bonobo", "Jair Bolar", "bonobo", "Salnorabo", "Bonaro", "bonaro", "Boniro", "boniro", "Bonaldo", "bonaldo", "Boçanaro", "boçanaro", "Bosoro", "bosoro", "Bolnossauro", "bolnossauro", "Bolsomario", "bolsomario", "bolsonaristas", "jairbolsonaro", "bozonaro", "burronaro", "bolsonaro", "miliciano", "Boloro" ]
def get_queries(queries_f='./queries.txt'):
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

# Create a streamer object
class StdOutListener(StreamListener):
	
	# Define a function that initialized when the miner is called
	def __init__(self, api = None):
		# That sets the api
		self.api = api
		self.connection = None
		self.counter_user = 0
		self.counter_tweets = 0
		# self.counter_json = 0

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

	def contemTime(self, text):
		lower_text = text.lower()
		tem_time = any(q.lower() in lower_text for q in TIMES)
		if(not tem_time):
			return False
		tem_bolsonaro = any(q.lower() in lower_text for q in QUERIES_CERTEZA)
		return (not tem_bolsonaro)

	def createUser(self, user):
		
		created_at = user["created_at"]
		created_at = created_at.split(" ")
		del created_at[4]
		del created_at[0]
		created_at = " ".join(created_at)
		created_at = datetime.datetime.strptime(created_at, '%b %d %H:%M:%S %Y')

		user_id = self.insertUser(user["id"], user["name"], user["screen_name"], user["description"], user["followers_count"], user["friends_count"], user["listed_count"], user["favourites_count"], user["statuses_count"], user["verified"], created_at, user["location"])
		return user_id

	def insertUser(self, id_twitter, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location):
		# print("insertUser")
		try:
			connection = self.getConnection()
			cursor = connection.cursor()

			# cursor.execute("SELECT id FROM user where id_twitter=" + str(id_twitter))
			# result = cursor.fetchone()
			# if(result != None):
			# 	# print("achei user duplicado")
			# 	cursor.execute ("""
			# 		UPDATE user
			# 		SET nome=%s, username=%s, description=%s, followers_count=%s, friends_count=%s, listed_count=%s, favourites_count=%s, statuses_count=%s, verified=%s, created_at=%s, location=%s
			# 		WHERE id_twitter=%s
			# 	""", (nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location, id_twitter))
			# 	return result[0]


			mySql_insert_query = """INSERT INTO user (id_twitter, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location) 
									VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
									ON DUPLICATE KEY UPDATE nome=%s, username=%s, description=%s, followers_count=%s, friends_count=%s, listed_count=%s, favourites_count=%s, statuses_count=%s, verified=%s, id=LAST_INSERT_ID(id)
									"""
			recordTuple = (id_twitter, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location, nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified)
			cursor.execute(mySql_insert_query, recordTuple)
			

			# print("COMMITED USERS")
			connection.commit()
			# self.counter_user = self.counter_user + 1
			# if(self.counter_user > 20):
			# 	self.counter_user = 0
			# 	print("COMMITED USERS")
			# 	connection.commit()
    				
			inserted_id = cursor.lastrowid

			# cursor.close()
			# connection.close()
			return inserted_id
		except mysql.connector.Error as error:
			print("Failed to insert into MySQL table {}".format(error))
			# try:
			# 	cursor.execute("SELECT id FROM user where id_twitter=" + str(id_twitter))
			# 	result = cursor.fetchone()
			# 	cursor.execute ("""
			# 			UPDATE user
			# 			SET nome=%s, username=%s, description=%s, followers_count=%s, friends_count=%s, listed_count=%s, favourites_count=%s, statuses_count=%s, verified=%s, created_at=%s, location=%s
			# 			WHERE id=%s
			# 		""", (nome, username, description, followers_count, friends_count, listed_count, favourites_count, statuses_count, verified, created_at, location, result[0]))


			# 	return result[0]
			# except mysql.connector.Error as error:
			#	return 0
			return 0
		

	def createTweet(self, tweet, user_id, ref_quote, ref_retweet):
		if(user_id == 0):
			print("ERRO USER ID = 0  ", tweet)
			return 0

		created_at = tweet["created_at"]
		created_at = created_at.split(" ")
		del created_at[4]
		del created_at[0]
		created_at = " ".join(created_at)
		created_at = datetime.datetime.strptime(created_at, '%b %d %H:%M:%S %Y')
		
		text = tweet["text"]
		if("extended_tweet" in tweet.keys()):
			text = tweet["extended_tweet"]["full_text"]
			# print("achei extended  ", text)

		is_retweet = False
		if("retweeted_status" in tweet.keys()):
			is_retweet = True
			if(ref_retweet == 0):
				print("ERRO REF RT = 0  ", tweet)
				return 0
		
		is_quote = False
		if("quoted_status" in tweet.keys()):
			is_quote = True
			if(ref_quote == 0):
				print("ERRO REF QUOTE = 0  ", tweet)
				return 0

		second_text = ""
		if("full_text" in tweet.keys()):
			second_text = tweet["full_text"]
		
		if(len(second_text) > len(text)):
			text = second_text
		
    	
		tweet_id = self.insertTweet(tweet["id"], user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, tweet["quote_count"], tweet["reply_count"], tweet["retweet_count"], tweet["favorite_count"], created_at)
		return tweet_id

	def insertTweet(self, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at):
		# print("insertTweet")
		try:
			connection = self.getConnection()
			cursor = connection.cursor()

			mySql_insert_query = """INSERT INTO tweet (id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, treinamento, sentimento) 
									VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
									ON DUPLICATE KEY UPDATE text=%s, ref_quote=%s, ref_retweet=%s, quote_count=%s, reply_count=%s, retweet_count=%s, favourites_count=%s, id=LAST_INSERT_ID(id)"""
			recordTuple = (id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, None, None, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count)
			cursor.execute(mySql_insert_query, recordTuple)


			# print("COMMITED TWEETS")
			# print(cursor.statement)
			connection.commit()
			# self.counter_tweets = self.counter_tweets + 1
			# if(self.counter_tweets > 20):
			# 	self.counter_tweets = 0
			# 	connection.commit()
			# 	print("COMMITED TWEETS")

			inserted_id = cursor.lastrowid
			# cursor.close()
			# connection.close()
			return inserted_id
		except mysql.connector.Error as error:
			print("Failed to insert into MySQL table {}".format(error))
			# try:
			# 	cursor.execute("SELECT id FROM tweet where id_twitter=" + str(id_twitter))
			# 	result = cursor.fetchone()
			# 	cursor.execute ("""
			# 		UPDATE tweet
			# 		SET user_id=%s, is_retweet=%s, is_quote=%s, text=%s, ref_quote=%s, ref_retweet=%s, quote_count=%s, reply_count=%s, retweet_count=%s, favourites_count=%s, created_at=%s
			# 		WHERE id=%s
			# 	""", (user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, result[0]))
			# 	return result[0]
			
			# except mysql.connector.Error as error:
			# 	return 0
			return 0

	def insertRetweet(self, user_id, tweet_id):
		# print("insertTweet")
		try:
			connection = self.getConnection()
			cursor = connection.cursor()

			mySql_insert_query = """INSERT IGNORE INTO retweet (tweet_id, user_id) 
									VALUES (%s, %s)"""
			recordTuple = (tweet_id, user_id)
			cursor.execute(mySql_insert_query, recordTuple)

			connection.commit()

			inserted_id = cursor.lastrowid

			cursor.close()
			# connection.close()
			return inserted_id
		except mysql.connector.Error as error:
			print("Failed to insert into MySQL table {}".format(error))
			return 0



	def on_data(self, data):
		# print("Data received")
		try:
			# data = data.encode("utf8", "ignore")
			# data = data.decode("utf8")
			data = json.loads(data)

			

			if("retweeted_status" in data.keys()):
				teste = data["retweeted_status"]
			else:
				teste = data

			text = teste["text"]

			if("extended_tweet" in teste.keys()):
				text = teste["extended_tweet"]["full_text"]
				# print("achei extended  ", text)
			if("quoted_status" in teste.keys()):
				if("extended_tweet" in teste["quoted_status"].keys()):
					text += teste["quoted_status"]["extended_tweet"]["full_text"]
				else:
					text += teste["quoted_status"]["text"]
			if(self.contemTime(text)):
				# print("Contem time")
				# print(text)
				return True
			
			user = data["user"]
			user_id = self.createUser(user)
			ref_retweet = None
			if("retweeted_status" in data.keys()):
				# with open('./teste.json', 'a+', encoding='utf-8') as f:
				# 	data = json.dumps(data, ensure_ascii=False) + "\n\n"
				# 	f.write(data)

				tweet_rt = data["retweeted_status"]
				user_rt = tweet_rt["user"]
				user_rt_id = self.createUser(user_rt)
				ref_retweet = self.createTweet(tweet_rt, user_rt_id, None, None)


			ref_quote = None
			if("quoted_status" in data.keys()):
				tweet_qt = data["quoted_status"]
				user_rt = tweet_qt["user"]
				user_rt_id = self.createUser(user_rt)
				ref_quote = self.createTweet(tweet_qt, user_rt_id, None, None)
			
			if(ref_retweet == None):
				id_tweet = self.createTweet(data, user_id, ref_quote, ref_retweet)
			else:
				id_retweet = self.insertRetweet(user_id, ref_retweet)
			# print("Tweet criado ", id_t)
			# if(self.counter_json < 20):
			# 	with open('./teste.json', 'a+', encoding='utf-8') as f:
			# 		data = json.dumps(data, ensure_ascii=False) + "\n\n"
			# 		f.write(data)
			# else:
			# 	self.counter_json = self.counter_json + 1

			return True
		except BaseException as e:
			print("Error on_data: %s" % str(e))
		return True

	# When an error occurs
	def on_error(self, status_code):
		# Print the error code
		print('Encountered error with status code:', status_code)
		
		# If the error code is 401, which is the error for bad credentials
		if status_code == 401:
			# End the stream
			return False

	# When a deleted tweet appears
	def on_delete(self, status_id, user_id):
		
		# Print message
		print("Delete notice")
		
		# Return nothing
		return

	# When reach the rate limit
	def on_limit(self, track):
		
		# Print rate limiting error
		print("Rate limited, continuing")
		
		# Continue mining tweets
		return True

	# When timed out
	def on_timeout(self):
		
		# Print timeout message
		print(sys.stderr, 'Timeout...')
		
		# Wait 10 seconds
		time.sleep(10)
		
		# Return nothing
		return


# Create a mining function
def start_mining(queries=None):
	'''
	Inputs list of strings. Returns tweets containing those strings.
	'''
	if queries is None:
		queries = get_queries()

	# Create a listener
	l = StdOutListener()
	
	auth = get_auth_api()[0]
	
	# Create a stream object with listener and authorization
	stream = Stream(auth, l)

	# Run the stream object using the user defined queries
	stream.filter(track=queries, languages=["pt"])


# for test purposes
if __name__ == "__main__":
	#start_mining(['python', '#Python'])
	start_mining()

