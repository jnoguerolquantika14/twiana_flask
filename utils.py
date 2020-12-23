#!/usr/bin/env python
# -*- coding:utf-8 -*-

import config
import difflib


def compute_score(results, p, score): #Suma la puntuación score al partido p en el diccionario results
    results[p[0]] += score
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


def find_sense(list_words): #Devuelve una lista con las palabras positivas y negativas a partir de una lista de palabras
    posi = list()
    nega = list()

    positive_words=open('diccionarios/positivas.txt', encoding='utf8').read().splitlines()#Palabras positivas
    negative_words=open('diccionarios/negativas.txt', encoding='utf8').read().splitlines()#Palabras negativas

    for word in list_words: #Palabras que vienen por parámetro
        for positive in positive_words: 
            if positive.lower() == replace_acentos(remove_badWords(word.lower())): #Si hay una coincidencia
                posi.append(positive)

        for negative in negative_words:
            if negative.lower() == replace_acentos(remove_badWords(word.lower())): #Si hay una coincidencia
                nega.append(negative)

    return posi, nega

def find_words(partidos, file, texto_full, field):
    text = texto_full.split()
    array_words = [] #Array de las palabras de texto_full
    
    for word in text:
        array_words.append(word.lower())

    # Abrimos el archivo y lo recorremos
    f = open(file, "r", encoding='utf8')
    lineas = f.read().splitlines()
    scaned = list()
        
    for line in lineas: #Partido/Hashtag/Palabra del fichero
        words = line.split("|||") #Partido/Hashtag/Palabra del fichero

        for text in array_words: # Cada palabra del tweet
            
            if len(text) > 3 or field == 'username': #Solo se analizan las palabras de más de 3 caracteres o si es un username
                
                if text in words[1].lower() or text in words[1]: #Si la palabra del tweet está contenida en la palabra o hashtag
                    
                    scan = True
                    for sca in scaned: #sca será false si la palabra ya ha sido analizada
                        if text == sca:
                            scan = False
                    if scan:
                        coinciden = 1
                    
                        if len(text) != len(words[1]): #Si no son la misma palabra, se analiza cuánto se parecen
                            try:
                                coinciden = difflib.SequenceMatcher(None, text, words[1]).ratio() #¿Cuánto se parecen?
                            except:
                                coinciden = 0
                        if coinciden > 0.6: #La palabra del tweet supera el umbral para ser parecida a la palabra del fichero
                            scaned.append(text) #Esta palabra ya va a ser analizada
                            #Determinamos la puntuación de esa palabra dependiendo de que parte de los datos de Twitter se trata
                            if field == 'description':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_description)
                            elif field == 'username':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_nombre)
                            elif field == 'account':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_account)

                            elif field == 'tweets-pos' or field == 'tweets-neg' or field == 'tweets-neu':
                                posi, nega = find_sense(array_words)
                                if len(posi) > len(nega) and field == 'tweets-pos':
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_positivo)
                                elif len(posi) < len(nega) and field == 'tweets-neg':
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_negativo)
                                elif len(posi) == len(nega) and field == 'tweets-neu':
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_neutro)
            
    f.close()
    
    return partidos #Devuelve el diccionario con los valores de cada partido

