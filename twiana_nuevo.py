#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Refactor Twiana QK14 data generator
import tweepy
import keys
import config
import utils
import random
import json
import threading
import traceback

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


def retrieve_data(account):
    global API
    global initial_result
    # 1.- Tomamos la cuenta a analizar

    # Inicializa estructura resultados
    my_results = {}
    my_results['name'] = account

    print("Analizando => @" + account)
    # 2.- Seleccióna una API KEY para utilizar
    api_key = select_api_key()
    # 3.- Gestiona la conexión con Tweepy
    connect_tweepy(api_key)

    # 4.- Obtiene User, Timeline y Descripción de la cuenta
    user = API.get_user(account)
    name = user.name
    # profile_image_url=user.profile_image_url
    # Modo extendido para que no se trunquen los tweets
    user_timeline = API.user_timeline(
        account, count=config.limite_tweets_apionly, tweet_mode='extended')
    description = user.description
    try:
        
        # 5.- Computa resultados para la Account, Username y Description
        my_results['account'] = utils.find_words(
            initial_result, 'diccionarios/compare_accounts.txt', account, 'account')
        restart_result()
        my_results['username'] = utils.find_words(
            initial_result, 'diccionarios/palabras_tweets.txt', name, 'username')
        restart_result()
        my_results['description'] = utils.find_words(
                initial_result, 'diccionarios/palabras_tweets.txt', description, 'description')
        my_results['description'] = utils.find_words(
                my_results['description'], 'diccionarios/compare_accounts.txt', description, 'description')
        
        # 6.- Recorre el timeline Tweet a Tweet para computar los resultados de:
        # - Tweets Positivos
        restart_result()
        my_results['tweets-pos'] = initial_result
        for tweet in user_timeline:
            my_results['tweets-pos'] = utils.find_words(
                        my_results['tweets-pos'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_pos')
            my_results['tweets-pos'] = utils.find_words(
                        my_results['tweets-pos'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_pos')
        # - Tweets Negativos
            restart_result()
            my_results['tweets-neg'] = initial_result
            for tweet in user_timeline:
                my_results['tweets-neg'] = utils.find_words(
                my_results['tweets-neg'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_neg')
                my_results['tweets-neg'] = utils.find_words(
                        my_results['tweets-neg'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_neg')
        # - Tweets Neutros
            restart_result()
            my_results['tweets-neu'] = initial_result
            for tweet in user_timeline:
                my_results['tweets-neu'] = utils.find_words(
                        my_results['tweets-neu'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_neu')
                my_results['tweets-neu'] = utils.find_words(
                        my_results['tweets-neu'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_neu')
        
    except Exception as e:
        print('Ocurrió una excepción => \n')
        traceback.print_exc()
    return my_results



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

final_file = open('results.json', 'w')
final_file.write('[\n')

a=retrieve_data('sanchezcastejon')
json.dump(a, final_file, indent = 4, sort_keys = False)

final_file.write(']')
