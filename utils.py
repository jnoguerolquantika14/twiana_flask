import config
import difflib


def compute_score(results, p, score):
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


def find_sense(list_words):
    posi = list()
    nega = list()
    for lines in open('diccionarios/positivas.txt').readlines():
        lines = lines.replace("\n", "")
        for word in list_words:
            if lines.lower() == replace_acentos(remove_badWords(word.lower())):
                posi.append(lines)
    for lines in open('diccionarios/negativas.txt').readlines():
        lines = lines.replace("\n", "")
        for word in list_words:
            if lines.lower() == replace_acentos(remove_badWords(word.lower())):
                nega.append(lines)
    return posi, nega


def find_words(partidos, file, texto_full, field):
    text = texto_full.split()
    array_words = []
    for word in text:
        array_words.append(word.lower())

    # Abrimos el archivo y lo recorremos
    f = open(file, "r")
    lineas = f.readlines()
    scaned = list()
    for line in lineas:
        line = line.replace("\n", "")
        words = line.split("|||")
        for text in array_words:
            if len(text) > 3 or field == 'username':
                if text in words[1].lower() or text in words[1]:
                    scan = True
                    for sca in scaned:
                        if text == sca:
                            scan = False
                    if scan:
                        coinciden = 1
                        if len(text) != len(words[1]):
                            try:
                                coinciden = difflib.SequenceMatcher(None, text, words[1]).ratio()
                            except:
                                coinciden = 0
                        if coinciden > 0.9:
                            scaned.append(text)
                            if field == 'description':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_description)
                            elif field == 'username':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_nombre)
                            elif field == 'account':
                                partidos = compute_score(
                                    partidos, words, config.puntuacion_account)
                            elif field == 'tweets_pos' or field == 'tweets_neg' or field == 'tweets_neu':
                                posi, nega = find_sense(array_words)
                                if len(posi) > len(nega) and field == 'tweets_pos':
                                    # print('Tweet positivo: ' + texto_full)
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_positivo)
                                elif len(posi) < len(nega) and field == 'tweets_neg':
                                    # print('Tweet negativo: ' + texto_full)
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_negativo)
                                elif len(posi) == len(nega) and field == 'tweets_neu':
                                    # print('Tweet neutro: ' + texto_full)
                                    partidos = compute_score(
                                        partidos, words, config.puntuacion_tweet_neutro)
    f.close()
    return partidos
