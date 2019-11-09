# total = 0
# for i in range(36):
#     total += 1000
#     total = total * 1.0045
# print(total)



import tweepy
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

class Fixer:

	def __init__(self, api = None):
		# That sets the api
		self.api = api
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

		if("quote_count" not in tweet.keys()):
			tweet["quote_count"] = 0
		if("reply_count" not in tweet.keys()):
			tweet["reply_count"] = 0
    	
		tweet_id = self.insertTweet(tweet["id"], user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, tweet["quote_count"], tweet["reply_count"], tweet["retweet_count"], tweet["favorite_count"], created_at)
		return tweet_id

	def insertTweet(self, id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at):
		print("insertTweet", ref_retweet)
		try:
			connection = self.getConnection()
			cursor = connection.cursor()

			mySql_insert_query = """INSERT INTO tweet (id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, treinamento, sentimento) 
									VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
									ON DUPLICATE KEY UPDATE text=%s, ref_quote=%s, ref_retweet=%s, quote_count=%s, reply_count=%s, retweet_count=%s, favourites_count=%s, ref_retweet=%s, ref_quote=%s, user_id=%s, id=LAST_INSERT_ID(id)"""
			recordTuple = (id_twitter, user_id, is_retweet, is_quote, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, created_at, None, None, text, ref_quote, ref_retweet, quote_count, reply_count, retweet_count, favourites_count, ref_retweet, ref_quote, user_id)
			cursor.execute(mySql_insert_query, recordTuple)

			connection.commit()

			inserted_id = cursor.lastrowid

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


	def getTweetsZoados(self):
		connection = self.getConnection()
		cursor = connection.cursor()
		cursor.execute("SELECT id_twitter, is_retweet FROM tweet where user_id=0 limit 100")
		result = cursor.fetchall()
		new_result = []
		for r in result:
			new_result.append(r[0])
		cursor.close()
		print(new_result)
		return new_result

	def deletar(self, id_twitter):
		connection = self.getConnection()
		cursor = connection.cursor()
		cursor.execute("DELETE FROM tweet WHERE id_twitter=" + str(id_twitter))
		connection.commit()

	def on_data(self, data):
		# print("Data received")
		try:
			# data = data.encode("utf8", "ignore")
			# data = data.decode("utf8")
			
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
				print("CRIEI RT", ref_retweet)


			ref_quote = None
			if("quoted_status" in data.keys()):
				tweet_qt = data["quoted_status"]
				user_rt = tweet_qt["user"]
				user_rt_id = self.createUser(user_rt)
				ref_quote = self.createTweet(tweet_qt, user_rt_id, None, None)
			
			
			id_tweet = self.createTweet(data, user_id, ref_quote, ref_retweet)
			
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




# Create a mining function
def start_mining():
    fixer = Fixer()
    api = get_auth_api()[1]
    tweets_zoados = fixer.getTweetsZoados()
    # print(tweets_zoados)
    while(tweets_zoados != None):
        try:
            tweets = api.statuses_lookup(tweets_zoados) # id_list is the list of tweet ids
            for tw in tweets:
                fixer.on_data(tw._json)
                print("fixed!\n")
            tweets_zoados = fixer.getTweetsZoados()
        except Exception as e:
            print("ERRO", e)
            print("COD ERRO", e.api_code)
			
            if(e.api_code == None):
                print("sleeping")
                time.sleep(60 * 15)
                





# for test purposes
if __name__ == "__main__":
	#start_mining(['python', '#Python'])
	start_mining()

