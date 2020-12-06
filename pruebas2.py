#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import tweepy
import keys
import config
import utils
import random
import json
import threading


def select_api_key():
    option = random.randint(1, 7)
    option = str(option)
    print('KEY:', option)
    return keys.twiana_key(option)


def connect_tweepy(api_key):
    auth = tweepy.OAuthHandler(
        api_key['consumer_key'], api_key['consumer_secret'])
    auth.set_access_token(api_key['access_token_key'],
                          api_key['access_token_secret'])
    api = tweepy.API(auth)
    return api


# 2.- Seleccióna una API KEY para utilizar
api_key = select_api_key()
# 3.- Gestiona la conexión con Tweepy
API = connect_tweepy(api_key)
account = "juannoguerol_"
user = API.get_user(account)
name = user.name
account_name = user.screen_name
# profile_image_url=user.profile_image_url
description = user.description
# Modo extendido para que no se trunquen los tweets
user_timeline = API.user_timeline(
    account, count=config.limite_tweets_apionly, tweet_mode='extended')
#print(json.dumps(user_timeline, indent=4))
# print(user_timeline._json['screen_name'])
#print(json.dumps(user_timeline._json, indent=4))

with open('data.json', 'w') as file1:
    for tweet in user_timeline:
        json.dump(tweet._json,  file1, indent=4)

compare_accounts_dir = tabla_dir = os.path.join(
    os.getcwd(), 'diccionarios', 'compare_accounts.txt-')

f = open('diccionarios/compare_accounts.txt-', 'r')
lineas = f.readlines()
num_accounts=len(lineas)



a=open('diccionarios/positivas.txt', encoding='utf8').readlines()
