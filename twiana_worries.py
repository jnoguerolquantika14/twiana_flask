#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Refactor Twiana QK14 data generator
import tweepy
import keys
import config
import utils_worries
import random
import json
import threading,queue
import traceback
import os

import numpy as np


API = None
initial_result = {
    "paro": 0,
    "política": 0,
    "corrupción": 0,
    "problemas económicos": 0,
    "sanidad": 0,
    "inmigración": 0,
    "problemas sociales": 0,
    "educación": 0,
    "pensiones": 0
}


def restart_result():
    global initial_result
    initial_result = {
    "paro": 0,
    "política": 0,
    "corrupción": 0,
    "problemas económicos": 0,
    "sanidad": 0,
    "inmigración": 0,
    "problemas sociales": 0,
    "educación": 0,
    "pensiones": 0
}
def retrieve_user_data(account,limite_tweets_apionly):
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

    # Modo extendido para que no se trunquen los tweets
    user_timeline = API.user_timeline(account, count=limite_tweets_apionly, tweet_mode='extended')

    user_data={'account':account,'name':name,'description':description, 'tweets':[]} #Los datos del usuario
    try:
        
        # 5.- Computa resultados para la Account, Username y Description
        my_results['account'] = utils_worries.find_worries(initial_result, 'diccionarios/worries_words.txt', account, 'account')
        restart_result()
        my_results['username'] = utils_worries.find_worries(initial_result, 'diccionarios/worries_words.txt', name, 'username')
        restart_result()
        my_results['description'] = utils_worries.find_worries(initial_result, 'diccionarios/worries_words.txt', description, 'description')
                
        # 6.- Recorre el timeline Tweet a Tweet para computar los resultados de:  
        process_timeline(my_results,user_timeline,user_data)

        
    except Exception as e:
        print('Ocurrió una excepción => \n')
        traceback.print_exc()
    return my_results, user_data

def process_timeline(my_results,user_timeline,user_data):
    threads = []
    thread_results=[]

    tweets_set= set()
    q = queue.Queue()

    chunks_number=3
    tweets_chunks=split_tweets(user_timeline, chunks_number)

    for i in range(chunks_number):

        ti = threading.Thread(target=process_tweet_types, name='Tweets', args=(my_results,tweets_chunks[i],i,q,tweets_set))
        threads.append(ti)    

    #Comenzar cada hilo
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)
    print(len(thread_results))
    my_results["tweets"] = join_dicts_in_list(thread_results)
    #Terminar hilos
    for thread in threads:
        thread.join()

    #Recogemos los tweets (no repetidos) en forma de lista
    user_data['tweets']=list(tweets_set)

def process_tweet_types(my_results,tweets_chunks,chunk_number,q,tweets_set):
    #Inicializa el diccionario para este tipo de tweet
    restart_result()
    my_results["tweets"] = initial_result

    for tweet in tweets_chunks:

        my_results["tweets"] = utils_worries.find_worries(
                        my_results["tweets"], 'diccionarios/worries_words.txt', tweet, "tweets")

        tweets_set.add(tweet)
    q.put({chunk_number:my_results["tweets"]})

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

def split_tweets(user_timeline, chunks):
    tweets=[] #Almacena los tweets
    for tweet in user_timeline:
        tweets.append(tweet.full_text)
    tweets_splitted=[]
    tweets_splitted_numpy=np.array_split(np.array(tweets),chunks) #Los divide en una lista de numpy
    tweets_splitted={}#Diccionario numero de particion: particion
    for tweet in tweets_splitted_numpy:
        index=len(tweets_splitted)
        tweets_splitted[index]=tweet.tolist()

    return tweets_splitted

def join_dicts_in_list(list):
    num_dicts=len(list)
    new_dict_list=[]
    for i in range(num_dicts):
        new_dict_list.append(list[i][i])
    result = {} 
    for d in new_dict_list:
        for k in d.keys(): 
            result[k] = result.get(k, 0) + d[k]
    return result

account='sanchezcastejon'
limit=200
my_results, user_data=retrieve_user_data(account,limit)

print(my_results)


