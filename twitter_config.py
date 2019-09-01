import sys
import time
from pprint import pprint

# Tweepy
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

# def get_api_keys(config_f='../settings/config.txt'):
def get_api_keys(config_f='./config.txt'):
	'''
	Read the file with the keys for Twitter API and return a dictionary with them.
	'''
	try:
		keys_file = open(config_f)
		lines = keys_file.readlines()
	except Exception as e:
		print('Problem found opening the file '+config_f+'.')
		print(e)
		sys.exit(1)
	try:
		consumer_key = lines[0].rstrip().split('=')[1]
		consumer_secret = lines[1].rstrip().split('=')[1]
		access_token = lines[2].rstrip().split('=')[1]
		access_secret = lines[3].rstrip().split('=')[1]
	except Exception as e:
		print('Problem processing the file '+config_f+'.')
		print(e)
		sys.exit(1)

	return {'consumer_key':consumer_key, 
			'consumer_secret':consumer_secret, 
			'access_token':access_token, 
			'access_secret':access_secret
			}


def get_auth_api():
	'''
	Return the API auth token
	'''
	keys = get_api_keys()
	try:
		consumer_key = keys['consumer_key']
		consumer_secret = keys['consumer_secret']
		access_token = keys['access_token']
		access_secret = keys['access_secret']
	except Exception as e:
		print('Problem with the keys imported.')
		print(e)
		sys.exit(1)

	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_secret)

	api = tweepy.API(auth)

	return auth, api



# for test purposes
if __name__ == "__main__":
	# With default file
   	pprint(get_api_keys())

   	# Test the api
   	get_auth_api()
