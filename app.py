from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json
import twiana_nuevo
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
    json_result=twiana_nuevo.create_json_result(account,tweets_limit)

    id = mongo.db.twiana_twitter.insert_one(
            {'name+limit':json_result['name']+', '+str(tweets_limit),'result' : json_result})
    response = jsonify({
            '_id': str(id),
            'name':json_result['name'],
            'result' : json_result
        })
    response.status_code = 201
    '''
    for x in mongo.db.twiana_twitter.find({'name':account}):
        print(x)'''

    response_json = json_util.dumps(json_result, indent=2)

    print("--- Finished in %s seconds ---" % (time.time() - start_time))
    return Response(response_json, mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
