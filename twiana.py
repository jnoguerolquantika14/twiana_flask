#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Refactor Twiana QK14 data generator
import tweepy
import keys
import config
import utils
import random
import json
import threading,queue
import traceback
import time

API = None
initial_result = {
    "pp": 0,
    "psoe": 0,
    "vox": 0,
    "podemos": 0,
    "cs": 0,
    "pacma": 0,
    "upyd": 0
}


def restart_result():
    global initial_result
    initial_result = {
        "pp": 0,
        "psoe": 0,
        "vox": 0,
        "podemos": 0,
        "cs": 0,
        "pacma": 0,
        "upyd": 0
    }


def retrieve_data(account,limite_tweets_apionly):
    global API
    global initial_result
    # 1.- Tomamos la cuenta a analizar

    # Inicializa estructura resultados
    my_results = {}
    my_results['name'] = account

    print("Analizando => @" + account+' con límite '+str(limite_tweets_apionly))
    # 2.- Seleccióna una API KEY para utilizar
    api_key = select_api_key()
    # 3.- Gestiona la conexión con Tweepy
    connect_tweepy(api_key)

    # 4.- Obtiene User, Timeline y Descripción de la cuenta
    user = API.get_user(account)
    name = user.name
    description = user.description

    # profile_image_url=user.profile_image_url
    # Modo extendido para que no se trunquen los tweets

    user_timeline = API.user_timeline(account, count=limite_tweets_apionly, tweet_mode='extended')
    
    try:
        
        # 5.- Computa resultados para la Account, Username y Description
        my_results['account'] = utils.find_words(initial_result, 'diccionarios/compare_accounts.txt', account, 'account')
        restart_result()
        my_results['username'] = utils.find_words(initial_result, 'diccionarios/palabras_tweets.txt', name, 'username')
        restart_result()
        my_results['description'] = utils.find_words(initial_result, 'diccionarios/palabras_tweets.txt', description, 'description')
        my_results['description'] = utils.find_words(my_results['description'], 'diccionarios/compare_accounts.txt', description, 'description')
                
        # 6.- Recorre el timeline Tweet a Tweet para computar los resultados de:  
        process_timeline(my_results,user_timeline)

    except Exception as e:
        print('Ocurrió una excepción => \n')
        traceback.print_exc()
    return my_results

def process_timeline(my_results,user_timeline):
    types = ["tweets-pos", "tweets-neg", "tweets-neu"]
    threads = []
    thread_results=[]

    q = queue.Queue()

    t0 = threading.Thread(target=process_tweet_types, name='Positive tweets', args=(my_results,user_timeline,types[0],q))
    threads.append(t0)
    
    t1 = threading.Thread(target=process_tweet_types, name='Negative tweets', args=(my_results,user_timeline,types[1],q))
    threads.append(t1)
    
    t2 = threading.Thread(target=process_tweet_types, name='Neutral tweets', args=(my_results,user_timeline,types[2],q))
    threads.append(t2)

    #Comenzar cada hilo
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)

    #Terminar hilos
    for thread in threads:
        thread.join()


def process_tweet_types(my_results,user_timeline,tweet_type,q):

    restart_result()
    my_results[tweet_type] = initial_result

    for tweet in user_timeline:

        my_results[tweet_type] = utils.find_words(
                        my_results[tweet_type], 'diccionarios/palabras_tweets.txt', tweet.full_text, tweet_type)
        my_results[tweet_type] = utils.find_words(
                        my_results[tweet_type], 'diccionarios/compare_accounts.txt', tweet.full_text, tweet_type)
    
    q.put({tweet_type:my_results[tweet_type]})


def select_api_key():
    option = random.randint(1, 8)
    return keys.twiana_key(str(option))

def connect_tweepy(api_key):
    global API
    auth = tweepy.OAuthHandler(
        api_key['consumer_key'], api_key['consumer_secret'])
    auth.set_access_token(api_key['access_token_key'],
                          api_key['access_token_secret'])
    API = tweepy.API(auth)


def create_json_result(account,tweets_limit):
    final_file = open('results.json', 'w')
    final_file.write('[\n')
    json_result=retrieve_data(account,tweets_limit)
    json.dump(json_result, final_file, indent = 4, sort_keys = False)

    final_file.write(']')
    return json_result
