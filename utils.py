#!/usr/bin/env python
# -*- coding:utf-8 -*-

import config
import difflib
import numpy as np


# Suma la puntuación score al partido p en el diccionario results
def compute_score(results, p, score):
    results[p] += score
    return results


def replace_acentos(text):
    text = text.replace("á", "a")
    text = text.replace("à", "a")
    text = text.replace("ä", "a")
    text = text.replace("é", "e")
    text = text.replace("è", "e")
    text = text.replace("ë", "e")
    text = text.replace("í", "i")
    text = text.replace("ì", "i")
    text = text.replace("ï", "i")
    text = text.replace("ó", "o")
    text = text.replace("ò", "o")
    text = text.replace("ö", "o")
    text = text.replace("ú", "u")
    text = text.replace("ù", "u")
    text = text.replace("ü", "u")
    return text


def remove_badWords(word):
    word = word.replace("#", "").replace("\"", "").replace(
        "@", "").replace(",", "").replace(":", "")
    for char in word:
        if char.isalpha() != True:
            if char.isdigit() != True:
                return "caracter no valido"
    return word


# Devuelve una lista con las palabras positivas y negativas a partir de una lista de palabras
def find_sense(list_words):
    posi = list()
    nega = list()
    f_pos = open('diccionarios/positivas.txt',
                 encoding='utf8')
    f_neg = open('diccionarios/negativas.txt',
                 encoding='utf8')
    positive_words = f_pos.read().splitlines()  # Palabras positivas
    negative_words = f_neg.read().splitlines()  # Palabras negativas

    for word in list_words:  # Palabras que vienen por parámetro
        for positive in positive_words:
            if positive.lower() == replace_acentos(remove_badWords(word.lower())):  # Si hay una coincidencia
                posi.append(positive)

        for negative in negative_words:
            if negative.lower() == replace_acentos(remove_badWords(word.lower())):  # Si hay una coincidencia
                nega.append(negative)

    f_pos.close()
    f_neg.close()
    return posi, nega

def need_scan(text,scanned):
    scan = True
    for sca in scanned:  # sca será false si la palabra ya ha sido analizada
        if text == sca:
            scan = False
    return scan

def score_result_field(results,party,field,mode):
    #Politics
    if mode=='politics' or mode=='worries':
        if field == 'description':
            results = compute_score(results, party, config.puntuacion_description)
        elif field == 'username':
            results = compute_score(results, party, config.puntuacion_nombre)
        elif field == 'account':
            results = compute_score(results, party, config.puntuacion_account)

    #Worries
    if mode=='worries':
        if field == 'tweets':
            results = compute_score(results, party, config.puntuacion_tweet_worry)
    return results

def score_result_tweet_sense(results,party,array_words,field):
    posi, nega = find_sense(array_words)
    if len(posi) > len(nega) and field == 'tweets-pos':
        results = compute_score(results, party, config.puntuacion_tweet_positivo)
    elif len(posi) < len(nega) and field == 'tweets-neg':
        results = compute_score(results, party, config.puntuacion_tweet_negativo)
    elif len(posi) == len(nega) and field == 'tweets-neu':
        results = compute_score(results, party, config.puntuacion_tweet_neutro)
    return results


def find_words(partidos, file, texto_full, field):
    text = texto_full.split()
    array_words = []  # Array de las palabras de texto_full

    for word in text:
        array_words.append(word.lower())

    # Abrimos el archivo y lo recorremos
    f = open(file, "r", encoding='utf8')
    lineas = f.read().splitlines()
    scanned = list()
    f.close()

    for line in lineas:  # Partido/Hashtag/Palabra del fichero
        words = line.split("|||")  # Partido/Hashtag/Palabra del fichero
        party = words[0]
        party_word = words[1]
        for text in array_words:  # Cada palabra del tweet

            # Solo se analizan las palabras de más de 3 caracteres o si es un username
            if len(text) > 3 or field == 'username':

                # Si la palabra del tweet está contenida en la palabra o hashtag
                if party_word.lower() in text or party_word in text:

                    if need_scan(text,scanned): #Si la palabra no ha sido escaneada
                        coinciden = 1

                        # Si no son la misma palabra, se analiza cuánto se parecen
                        if len(text) != len(party_word):
                            try:
                                coinciden = difflib.SequenceMatcher(
                                    None, text, party_word).ratio()  # ¿Cuánto se parecen?
                            except:
                                coinciden = 0
                        if coinciden > 0.6:  # La palabra del tweet supera el umbral para ser parecida a la palabra del fichero
                            # Esta palabra ya va a ser analizada
                            scanned.append(text)
                            # Determinamos la puntuación de esa palabra dependiendo de que parte de los datos de Twitter se trata
                            if field == 'tweets-pos' or field == 'tweets-neg' or field == 'tweets-neu':
                                partidos=score_result_tweet_sense(partidos,party,array_words,field)
                            else:
                                partidos=score_result_field(partidos,party,field,'politics')

                                

    return partidos  # Devuelve el diccionario con los valores de cada partido


def split_tweets(user_timeline, chunks):
    tweets = []  # Almacena los tweets
    for tweet in user_timeline:
        tweets.append(tweet.full_text)
    tweets_splitted = []
    tweets_splitted_numpy = np.array_split(
        np.array(tweets), chunks)  # Los divide en una lista de numpy
    tweets_splitted = {}  # Diccionario numero de particion: particion
    for tweet in tweets_splitted_numpy:
        index = len(tweets_splitted)
        tweets_splitted[index] = tweet.tolist()

    return tweets_splitted


def join_dicts_in_list(list_):
    num_dicts = len(list_)
    new_dict_list = []
    for i in range(num_dicts):
        new_dict_list.append(list_[i][i])
    result = {}
    for d in new_dict_list:
        for k in d.keys():
            result[k] = result.get(k, 0) + d[k]
    return result


def join_worries(dict_worries):

    new_dict_list = []
    for i in dict_worries.keys():
        new_dict_list.append(dict_worries[i])
    result = {}

    for d in new_dict_list:
        for k in d.keys():
            result[k] = result.get(k, 0) + d[k]
    return result


def find_worries(results, file, texto_full, field):
    text = texto_full.split()
    array_words = []  # Array de las palabras de texto_full

    for word in text:
        array_words.append(word.lower())

    # Abrimos el archivo y lo recorremos
    f = open(file, "r", encoding='utf8')
    lineas = f.read().splitlines()
    scanned = list()
    f.close()

    for line in lineas:  # Preocupacion/Hashtag/Palabra del fichero
        words = line.split("|||")  # Preocupacion/Hashtag/Palabra del fichero
        worry = words[0]
        worry_word = words[1]

        for text in array_words:  # Cada palabra del tweet

            # Solo se analizan las palabras de más de 3 caracteres o si es un username
            if len(text) > 3 or field == 'username':

                # Si la palabra del tweet está contenida en la palabra o hashtag
                if text in worry_word.lower() or text in worry_word:

                    if need_scan(text,scanned): #Si la palabra no ha sido escaneada
                        coinciden = 1

                        # Si no son la misma palabra, se analiza cuánto se parecen
                        if len(text) != len(worry_word):
                            try:
                                coinciden = difflib.SequenceMatcher(
                                    None, text, worry_word).ratio()  # ¿Cuánto se parecen?
                            except:
                                coinciden = 0
                        if coinciden > 0.6:  # La palabra del tweet supera el umbral para ser parecida a la palabra del fichero
                            # Esta palabra ya va a ser analizada
                            scanned.append(text)
                            # Determinamos la puntuación de esa palabra dependiendo de que parte de los datos de Twitter se trata
                            results=score_result_field(results,worry,field,'worries')

    return results  # Devuelve el diccionario con los valores de cada preocupacion
