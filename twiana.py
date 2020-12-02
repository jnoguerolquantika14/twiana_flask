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

API = None
Threads = 4
recorridos = 0
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


def retrieve_data(accounts):
    global API
    global initial_result
    global recorridos
    # 1.- Tomamos las accounts a analizar del archivo
    # f = open('diccionarios/compare_accounts.txt', 'r')
    final_file = open('results-v3.json', 'a+')

    full_result = list()
    # final_file.write('[\n')
    for line in accounts:
        try:
            line = line.split("|||")
            account = line[1][:-1]
            # Inicializa estructura resultados
            my_results = {}
            my_results['name'] = account
            my_results['iv'] = line[0]

            print("Analizando " + str(recorridos) + ") => " + account)
            recorridos += 1
            # 2.- Seleccióna una API KEY para utilizar
            api_key = select_api_key()
            # 3.- Gestiona la conexión con Tweepy
            connect_tweepy(api_key)

            # 4.- Obtiene User, Timeline y Descripción de la cuenta
            user = API.get_user(account)
            description = user.description
            timeline = API.user_timeline(
                account, count=config.limite_tweets_apionly, tweet_mode='extended')
            # print(user.name)
            # print(description)

            # 5.- Computa resultados para la Account, Username y Description
            my_results['account'] = utils.find_words(
                initial_result, 'diccionarios/compare_accounts.txt', account, 'account')
            restart_result()
            my_results['username'] = utils.find_words(
                initial_result, 'diccionarios/palabras_tweets.txt', user.name, 'username')
            restart_result()
            my_results['description'] = utils.find_words(
                initial_result, 'diccionarios/palabras_tweets.txt', description, 'description')
            my_results['description'] = utils.find_words(
                my_results['description'], 'diccionarios/compare_accounts.txt', description, 'description')

            # 6.- Recorre el timeline Tweet a Tweet para computar los resultados de:
            # - Tweets Positivos
            restart_result()
            my_results['tweets-pos'] = initial_result
            for tweet in timeline:
                my_results['tweets-pos'] = utils.find_words(
                    my_results['tweets-pos'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_pos')
                my_results['tweets-pos'] = utils.find_words(
                    my_results['tweets-pos'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_pos')
            # - Tweets Negativos
            restart_result()
            my_results['tweets-neg'] = initial_result
            for tweet in timeline:
                my_results['tweets-neg'] = utils.find_words(
                    my_results['tweets-neg'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_neg')
                my_results['tweets-neg'] = utils.find_words(
                    my_results['tweets-neg'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_neg')
            # - Tweets Neutros
            restart_result()
            my_results['tweets-neu'] = initial_result
            for tweet in timeline:
                my_results['tweets-neu'] = utils.find_words(
                    my_results['tweets-neu'], 'diccionarios/palabras_tweets.txt', tweet.full_text, 'tweets_neu')
                my_results['tweets-neu'] = utils.find_words(
                    my_results['tweets-neu'], 'diccionarios/compare_accounts.txt', tweet.full_text, 'tweets_neu')
            # print(my_results)

            # full_result.append(my_results)

            # 7.- Vuelca los resultados al fichero de salida
            final_file.write(json.dumps(my_results))
            final_file.write(',\n')
        except:
            print('Ocurrió una excepción con => ' + line[1][:-1])

    # final_file.write(']')


def select_api_key():
    option = random.randint(2, 33)
    return keys.twiana_key(str(option))


def connect_tweepy(api_key):
    global API
    auth = tweepy.OAuthHandler(
        api_key['consumer_key'], api_key['consumer_secret'])
    auth.set_access_token(api_key['access_token_key'],
                          api_key['access_token_secret'])
    API = tweepy.API(auth)


# retrieve_data()

hilos = list()
f = open('diccionarios/compare_accounts.txt', 'r')
lineas = f.readlines()
num_accounts = len(lineas)

final_file = open('results.json', 'a+')
final_file.write('[\n')
for i in range(Threads):
    t = threading.Thread(target=retrieve_data, args=(
        lineas[i*int(num_accounts/4):(i+1)*int(num_accounts/4)],))
    hilos.append(t)
    t.start()
final_file.write(']')
