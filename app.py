from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util

import json
import twiana
import app_utils
import hashlib
import tweepy

from pymongo import MongoClient
import time


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'twiana'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/twiana'
app.config['MONGO_URI'] = 'mongodb+srv://flask:flask@cluster0.r2dhr.mongodb.net/twiana'

mongo = PyMongo(app)

twiana_twitter=mongo.db.twiana_twitter 
twiana_politics_analitycs=mongo.db.twiana_politics_analitycs

    
@app.route('/service/prediction/account/<account>', methods=['GET'])
def account_prediction(account):
    
    start_time = time.time()

    tweets_limit = request.args.get('limit', default = 200, type = int) # El maximo de tweets sin usar cursor son 200 (si se usa llegaría hasta 3200)
    try:
        user_analysis, user_clasif, user_data=twiana.twiana(account,tweets_limit)

        json_clasif=user_clasif.to_dict(orient='records')
        
        name=user_data['name']
        hashed_name=hashlib.md5(name.encode()).hexdigest()
        account=user_data['account']
        hashed_account=hashlib.md5(account.encode()).hexdigest()
        description=user_data['description']
        hashed_description=hashlib.md5(description.encode()).hexdigest()
        tweets=user_data['tweets']
        clasification=json_clasif[0]['clasif2']


        exists_account=app_utils.check_existence(twiana_twitter,'account',hashed_account)

        if exists_account: #Si ya existe en la bbdd, se actualiza ambas bbdd
            app_utils.update_db_twitter(twiana_twitter,hashed_account,hashed_name,hashed_description,tweets)
            twiana_politics_analitycs.update_one({'account':hashed_account},{"$set":{'clasification':clasification}})

        else:
            twiana_twitter.insert_one(
                    {'account':hashed_account, 'name' : hashed_name, 'description':hashed_description, 'tweets':tweets})
            twiana_politics_analitycs.insert_one(
                    {'account':hashed_account, 'clasification' : clasification})
        
        response = jsonify({'account':hashed_account, 'name' : hashed_name, 'description':hashed_description, 'tweets':tweets})
        
        json_user_result={'resultados':user_analysis,'clasificacion':clasification}
        response_json = json_util.dumps(json_user_result, indent=2)

        

        print("--- Finished in %s seconds ---" % (time.time() - start_time))
        return Response(response_json, mimetype="application/json",status=201)
    except tweepy.TweepError as e:
        print(e) 

        return Response(
        "Usuario no válido",
        status=404,
    )



if __name__ == "__main__":
    app.run(debug=True)
