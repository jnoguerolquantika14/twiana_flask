from flask import Flask, request, Response
from flask_pymongo import PyMongo
from bson import json_util

import json
import twiana
import app_utils
import hashlib
import tweepy

import time


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'twiana'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/twiana'
app.config['MONGO_URI'] = 'mongodb+srv://flask:flask@cluster0.r2dhr.mongodb.net/twiana'

mongo = PyMongo(app)

twiana_twitter=mongo.db.twiana_twitter 
twiana_politics_analitycs=mongo.db.twiana_politics_analitycs

@app.route('/service/prediction/account/', methods=['GET'])
def account_prediction():
    
    start_time = time.time()

    account=request.args.get('account', default = 'Quantika14', type = str)
    tweets_limit = request.args.get('limit', default = 200, type = int) # El maximo de tweets sin usar cursor son 200

    try:
        user_analysis, clasif, user_data=twiana.twiana(account,tweets_limit)
        #Tomamos los datos del análisis y los coddificamos
        name=user_data['name']
        hashed_name=hashlib.md5(name.encode()).hexdigest()
        account=user_data['account']
        hashed_account=hashlib.md5(account.encode()).hexdigest()
        description=user_data['description']
        hashed_description=hashlib.md5(description.encode()).hexdigest()
        tweets=user_data['tweets']
        clasification=clasif

        exists_account=app_utils.check_existence(twiana_twitter,'account',hashed_account)

        if exists_account: #Si ya existe en la bbdd, se actualiza ambas bbdd
            document={'account':hashed_account}
            fields_to_update={'clasification':clasification,'analysis':user_analysis}
            app_utils.update_db_twitter(twiana_twitter,hashed_account,hashed_name,hashed_description,tweets)
            app_utils.update_collection(twiana_politics_analitycs,document,fields_to_update)

        else:
            document_twitter={'account':hashed_account, 'name' : hashed_name, 'description':hashed_description, 'tweets':tweets}
            document_politics_analitycs={'account':hashed_account, 'clasification' : clasification,'analysis':user_analysis}
            app_utils.add_document(twiana_twitter,document_twitter)
            app_utils.add_document(twiana_politics_analitycs,document_politics_analitycs)

                
        json_user_result={'resultados':user_analysis,'clasificacion':clasification}
        response_json = json_util.dumps(json_user_result, indent=2)

        print("--- Finished in %s seconds ---" % (time.time() - start_time))
        return Response(response_json, mimetype="application/json",status=201)
    except tweepy.TweepError as e:

        return Response("Usuario no válido",status=404)

if __name__ == "__main__":
    app.run(host= '0.0.0.0')
