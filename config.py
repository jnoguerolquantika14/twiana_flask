# CONF TWIANA
mongo = True
log = True
friends = False
verbose = False
path_log = ""

##-----------------VARIABLES TWIANA---------------------##

# DIFERENCIAS
dif_nor = 2  # Diferencia de puntos para adjudicar resultado al usuario

# API
# Limite de tweets de la API cuando el usuario no se encuentra en la db
limite_tweets_apionly = 100
# Limite de tweets de la API cuando el usuario se encuentra en la db
limite_tweets_apiupdate = 100
limite_friends = 20  # Limite de friends de la API

# BD
# Limite de tweets para analizar de la DB (sin limite, modules/analiticsOperations.py para activarlo)
limite_tweets_db = 100

# PUNTUACIONES
puntuacion_tweet_positivo = 1
puntuacion_tweet_negativo = 1
puntuacion_tweet_neutro = 1
puntuacion_description = 26
puntuacion_nombre = 100
puntuacion_account = 100
puntuacion_friends_description = 10
puntuacion_friends_name = 5