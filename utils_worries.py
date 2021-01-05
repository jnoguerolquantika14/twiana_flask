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



def find_worries(results, file, texto_full, field):
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
                                results = compute_score(
                                    results, words, config.puntuacion_description)
                            elif field == 'username':
                                results = compute_score(
                                    results, words, config.puntuacion_nombre)
                            elif field == 'account':
                                results = compute_score(
                                    results, words, config.puntuacion_account)
                            elif field == 'tweets':
                                results = compute_score(results, words, config.puntuacion_tweet_worry)

            
    f.close()
    
    return results #Devuelve el diccionario con los valores de cada partido

