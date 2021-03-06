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
import queue
import traceback
import os
# Predicciones
import pandas as pd
#import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import pickle

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


initial_result_worries = {
    "paro": 0,
    "politíca": 0,
    "corrupción": 0,
    "problemas económicos": 0,
    "sanidad": 0,
    "inmigración": 0,
    "problemas sociales": 0,
    "educación": 0,
    "pensiones": 0
}


def restart_result_worries():
    global initial_result_worries
    initial_result_worries = {
        "paro": 0,
        "politíca": 0,
        "corrupción": 0,
        "problemas económicos": 0,
        "sanidad": 0,
        "inmigración": 0,
        "problemas sociales": 0,
        "educación": 0,
        "pensiones": 0
    }


def retrieve_user_data(account, limite_tweets_apionly):
    global API
    global initial_result
    global initial_result_worries
    # 1.- Tomamos la cuenta a analizar

    # Inicializa estructura resultados
    my_results = {}
    my_results['name'] = account
    worries = {}
    worries_joined = None

    print("Analizando => @" + account+' con límite '+str(limite_tweets_apionly))
    # 2.- Seleccióna una API KEY para utilizar
    api_key = select_api_key()
    # 3.- Gestiona la conexión con Tweepy
    connect_tweepy(api_key)

    # 4.- Obtiene User, Timeline y Descripción de la cuenta

    user = API.get_user(account)
    name = user.name
    description = user.description
    location = user.location
    if location=="":
        location="None"

    # Modo extendido para que no se trunquen los tweets
    user_timeline = API.user_timeline(
        account, count=limite_tweets_apionly, tweet_mode='extended')

    user_data = {'account': account, 'name': name,
                 'description': description, 'location':location,'tweets': []}  # Los datos del usuario
    try:

        # 5.- Computa resultados para la Account, Username y Description
        restart_result()
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

        # 6.- Recorre el timeline Tweet a Tweet para computar los resultados de partidos:
        process_timeline(my_results, user_timeline, user_data)

        restart_result_worries()
        worries['account'] = utils.find_worries(
            initial_result_worries, 'diccionarios/worries_words.txt', account, 'account')
        restart_result_worries()
        worries['username'] = utils.find_worries(
            initial_result_worries, 'diccionarios/worries_words.txt', name, 'username')
        restart_result_worries()
        worries['description'] = utils.find_words(
            initial_result_worries, 'diccionarios/worries_words.txt', description, 'description')
        # Recorre el timeline Tweet a Tweet para computar los resultados de preocupaciones:
        process_timeline_worries(worries, user_timeline)
        worries_joined = utils.join_worries(
            worries)  # Unimos los datos de cada field

    except Exception:
        print('Ocurrió una excepción => \n')
        traceback.print_exc()
    return my_results, worries_joined, user_data


def process_timeline(my_results, user_timeline, user_data):
    types = ["tweets-pos", "tweets-neg", "tweets-neu"]
    threads = []
    thread_results = []

    tweets_set = set()
    q = queue.Queue()

    t0 = threading.Thread(target=process_tweet_types, name='Positive tweets', args=(
        my_results, user_timeline, types[0], q, tweets_set))
    threads.append(t0)

    t1 = threading.Thread(target=process_tweet_types, name='Negative tweets', args=(
        my_results, user_timeline, types[1], q, tweets_set))
    threads.append(t1)

    t2 = threading.Thread(target=process_tweet_types, name='Neutral tweets', args=(
        my_results, user_timeline, types[2], q, tweets_set))
    threads.append(t2)

    # Comenzar cada hilo
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)

    # Terminar hilos
    for thread in threads:
        thread.join()

    # Recogemos los tweets (no repetidos) en forma de lista
    user_data['tweets'] = list(tweets_set)


def process_tweet_types(my_results, user_timeline, tweet_type, q, tweets_set):
    # Inicializa el diccionario para este tipo de tweet
    restart_result()
    my_results[tweet_type] = initial_result

    for tweet in user_timeline:

        my_results[tweet_type] = utils.find_words(
            my_results[tweet_type], 'diccionarios/palabras_tweets.txt', tweet.full_text, tweet_type)
        my_results[tweet_type] = utils.find_words(
            my_results[tweet_type], 'diccionarios/compare_accounts.txt', tweet.full_text, tweet_type)

        tweets_set.add(tweet.full_text)
    q.put({tweet_type: my_results[tweet_type]})


def retrieve_user_worries(account, limite_tweets_apionly):
    global API
    global initial_result_worries
    # 1.- Tomamos la cuenta a analizar

    # Inicializa estructura resultados
    worries = {}
    worries_joined = None

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
    user_timeline = API.user_timeline(
        account, count=limite_tweets_apionly, tweet_mode='extended')

    try:
        # Busca las preocupaciones para cada dato de la cuenta
        restart_result_worries()
        worries['account'] = utils.find_worries(
            initial_result_worries, 'diccionarios/worries_words.txt', account, 'account')
        restart_result_worries()
        worries['username'] = utils.find_worries(
            initial_result_worries, 'diccionarios/worries_words.txt', name, 'username')
        restart_result_worries()
        worries['description'] = utils.find_words(
            initial_result_worries, 'diccionarios/worries_words.txt', description, 'description')
        # Recorre el timeline Tweet a Tweet para computar los resultados de preocupaciones:
        process_timeline_worries(worries, user_timeline)
        worries_joined = utils.join_worries(
            worries)  # Unimos los datos de cada field

    except Exception:
        print('Ocurrió una excepción => \n')
        traceback.print_exc()
    return worries_joined


def process_timeline_worries(worries, user_timeline):
    threads = []
    thread_results = []

    tweets_set = set()
    q = queue.Queue()

    chunks_number = 3
    # Divide los tweets en 3 partes para threading
    tweets_chunks = utils.split_tweets(user_timeline, chunks_number)

    for i in range(chunks_number):  # Hacemos un hilo por cada trozo

        ti = threading.Thread(target=process_tweet_worries, name='Tweets {}'.format(
            i), args=(worries, tweets_chunks[i], i, q, tweets_set))
        threads.append(ti)

    # Comenzar cada hilo
    for thread in threads:
        thread.start()
        response = q.get()
        thread_results.append(response)

    worries["tweets"] = utils.join_dicts_in_list(
        thread_results)  # Une el resultado de los hilos
    # Terminar hilos
    for thread in threads:
        thread.join()


def process_tweet_worries(worries, tweets_chunks, chunk_number, q, tweets_set):
    # Inicializa el diccionario para este tipo de tweet
    restart_result_worries()
    worries["tweets"] = initial_result_worries

    for tweet in tweets_chunks:

        worries["tweets"] = utils.find_worries(
            worries["tweets"], 'diccionarios/worries_words.txt', tweet, "tweets")

        tweets_set.add(tweet)
    q.put({chunk_number: worries["tweets"]})


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


# Renombra todos los atributos del diccionario a atributo_partido
def parse_json_attrs(dictionary, politic_parties, attribute):
    tamo = dictionary.pop(attribute)  # Se toma todo el contenido del atributo
    for party in politic_parties:
        # Se extrae el valor de cada array del atributo
        dictionary[attribute+"_"+party] = tamo[party]


def modelo_Logit_binom(json_entrenamiento):
    with open(json_entrenamiento) as f:
        data = json.load(f)

    # Creación de las variables anidadas en las listas
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    for user in data:  # Para cada usuario del json se renombran los atributos
        parse_json_attrs(user, partidos, "account")  # Account
        parse_json_attrs(user, partidos, "username")  # Username
        parse_json_attrs(user, partidos, "description")  # Description
        parse_json_attrs(user, partidos, "tweets-pos")  # Tweets - Positivos
        parse_json_attrs(user, partidos, "tweets-neg")  # Tweets - Negativos
        parse_json_attrs(user, partidos, "tweets-neu")  # Tweets - Neutros

    datos_final = pd.DataFrame(data)  # Creamos una dataframe

    # Arreglo de valores de la variable iv
    datos_final.loc[datos_final['iv'] == 'pp\n', 'iv'] = 'pp'
    datos_final.loc[datos_final['iv'] == 'psoe\n', 'iv'] = 'psoe'
    datos_final.loc[datos_final['iv'] == 'vox\n', 'iv'] = 'vox'
    datos_final.loc[datos_final['iv'] == 'podemos\n', 'iv'] = 'podemos'
    datos_final.loc[datos_final['iv'] == 'cs\n', 'iv'] = 'cs'
    datos_final.loc[datos_final['iv'] == 'pacma\n', 'iv'] = 'pacma'

    # Eliminación de votantes de upyd
    datos_final = datos_final.drop(
        datos_final[datos_final['iv'] == "upyd\n"].index)

    datos_final["iv"] = datos_final["iv"].astype('category')

    datos_final_binom = pd.get_dummies(datos_final, columns=["iv"])

    datos_final_binom = datos_final_binom.reindex(
        columns=["name", "iv_pp", "iv_psoe", "iv_vox", "iv_podemos", "iv_cs", "iv_pacma", 'account_pp',
                 'account_psoe',
                 'account_vox', 'account_podemos',
                 'account_cs', 'account_pacma', 'username_pp', 'username_psoe',
                 'username_vox', 'username_podemos', 'username_cs', 'username_pacma',
                 'description_pp', 'description_psoe', 'description_vox',
                 'description_podemos', 'description_cs', 'description_pacma',
                 'tweets-pos_pp', 'tweets-pos_psoe', 'tweets-pos_vox',
                 'tweets-pos_podemos', 'tweets-pos_cs', 'tweets-pos_pacma',
                 'tweets-neg_pp', 'tweets-neg_psoe', 'tweets-neg_vox',
                 'tweets-neg_podemos', 'tweets-neg_cs', 'tweets-neg_pacma',
                 'tweets-neu_pp', 'tweets-neu_psoe', 'tweets-neu_vox',
                 'tweets-neu_podemos', 'tweets-neu_cs', 'tweets-neu_pacma'])
    datos_final_binom['iv'] = datos_final['iv']

    # Para dejar fuera al nombre y los account_x
    data_X_train = datos_final_binom.iloc[:, 7:43]

    escalar = StandardScaler()
    X_train = escalar.fit_transform(data_X_train)

    with open("obj.pickle", "wb") as f:
        pickle.dump(escalar, f)
    for i in range(len(partidos)):
        Y_train = datos_final_binom.iloc[:, i + 1]

        LR = LogisticRegression().fit(X_train, Y_train)

        joblib.dump(LR, f'modelo_{partidos[i]}.pkl')


def funcion_ev_Logit_binom(user_analysis):

    # Para el usuario del diccionario se renombran los atributos
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    parse_json_attrs(user_analysis, partidos, "account")  # Account
    parse_json_attrs(user_analysis, partidos, "username")  # Username
    parse_json_attrs(user_analysis, partidos, "description")  # Description
    parse_json_attrs(user_analysis, partidos,
                     "tweets-pos")  # Tweets - Positivos
    parse_json_attrs(user_analysis, partidos,
                     "tweets-neg")  # Tweets - Negativos
    parse_json_attrs(user_analysis, partidos, "tweets-neu")  # Tweets - Neutros
    datos_final_nuevos = pd.DataFrame(user_analysis, index=[0])
    ##########################################################

    clasif = pd.DataFrame([])
    probab = pd.DataFrame([])
    clasif['usuario'] = datos_final_nuevos.iloc[:, 0]
    probab['usuario'] = datos_final_nuevos.iloc[:, 0]

    data_X_test = datos_final_nuevos.iloc[:, 1:]  # Quita la columna name

    with open("obj.pickle", "rb") as f:
        escalar = pickle.load(f)
    X_test = escalar.transform(data_X_test)

    for i in range(len(partidos)):
        # Modelos Logisticos
        LR = joblib.load(f'modelo_{partidos[i]}.pkl')
        Y_pred = LR.predict(X_test)  # Predice la etiqueta
        Y_prob = LR.predict_proba(X_test)  # Estimación de probabilidad

        clasif[f'{partidos[i]}'] = Y_pred  # Etiquetas (partidos) más probables
        # Probabilidades de cada partido
        probab[f'{partidos[i]}'] = Y_prob[:, 1]

    clasif["clasif2"] = probab[['pp', 'psoe', 'vox',
                                'podemos', 'cs', 'pacma']].idxmax(axis=1)

    clasif_result = clasif.iloc[:, [0, 7]]
    return clasif_result


global CURR_DIR
CURR_DIR = os.path.dirname(os.path.abspath(__file__))


def twiana(account, limite_tweets_apionly):
    # Devuelve el analisis de la cuenta de Twitter y los datos que se han analizado
    user_analysis, worries, user_data = retrieve_user_data(
        account, limite_tweets_apionly)

    # Si no existen los modelos entrenados
    if not os.path.isfile(CURR_DIR+'/obj.pickle'):
        # Crea los modelos de cada partido a partir del json de entrenamiento
        modelo_Logit_binom(CURR_DIR+'/train.json')

    # Devuelve la clasificacion a partir del analisis de la cuenta de Twitter
    user_clasif = funcion_ev_Logit_binom(user_analysis)

    user_analysis.pop('name')  # Eliminamos el nombre de la cuenta

    # Pasa el dataframe a un diccionario
    clasif = user_clasif.to_dict(orient='records')
    clasif = clasif[0]
    clasif.pop('usuario')  # Eliminamos el nombre de la cuenta

    return user_analysis, worries, clasif['clasif2'], user_data


def twiana_worries(account, limite_tweets_apionly):
    worries = retrieve_user_worries(account, limite_tweets_apionly)
    return worries
