from os import replace
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json
import twiana
import tweepy
from pymongo import MongoClient
import time


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'twiana'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/twiana'
app.config['MONGO_URI'] = 'mongodb+srv://flask:flask@cluster0.r2dhr.mongodb.net/twiana'

mongo = PyMongo(app)
    
@app.route('/service/prediction/account/<account>', methods=['GET'])
def account_prediction(account):
    
    start_time = time.time()
    mongo.db.twiana_twitter.delete_many( { } )

    tweets_limit = request.args.get('limit', default = 200, type = int) # El maximo de tweets sin usar cursor son 200 (si se usa llegaría hasta 3200)
    try:
        json_user, df_result=twiana.twiana(account,tweets_limit)

    
        json_result=df_result.to_dict(orient='records')

        id = mongo.db.twiana_twitter.insert_one(
                {'usuario+limit':json_result[0]['usuario']+', '+str(tweets_limit),'clasificacion' : json_result[0]['clasif2']})
        
        response = jsonify({
                '_id': str(id),
                'usuario':json_result[0]['usuario'],
                'resultados':json_user,
                'clasificacion' : json_result[0]['clasif2']
            })
        
        json_user_result={'resultados':json_user,'clasificacion':json_result[0]['clasif2']}
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
