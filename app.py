from flask import Flask, request, Response, render_template
from flask_pymongo import PyMongo
from bson import json_util
from forms import SearchForm

import json
import twiana
import app_utils
import hashlib
import tweepy

import time
import os


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'twiana'
#app.config['MONGO_URI'] = 'mongodb://localhost:27017/twiana'
app.config['MONGO_URI'] = 'mongodb+srv://flask:flask@cluster0.r2dhr.mongodb.net/twiana'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

mongo = PyMongo(app)

twiana_twitter = mongo.db.twiana_twitter
twiana_worries = mongo.db.twiana_worries
twiana_politics_analitycs = mongo.db.twiana_politics_analitycs


def retrieve_clasification_worries(account,api):
    start_time = time.time()
    # El maximo de tweets sin usar cursor son 200
    #tweets_limit = request.args.get('limit', default=200, type=int)
    tweets_limit = 200
    try:
        user_analysis, worries, clasif, user_data = twiana.twiana(
            account, tweets_limit)
        # Tomamos los datos del análisis y los codificamos
        name = user_data['name']
        hashed_name = hashlib.md5(name.encode()).hexdigest()
        account = user_data['account']
        hashed_account = hashlib.md5(account.encode()).hexdigest()
        description = user_data['description']
        hashed_description = hashlib.md5(description.encode()).hexdigest()
        location=user_data['location']
        tweets = user_data['tweets']
        clasification = clasif

        exists_account = app_utils.check_existence(
            twiana_twitter, 'account', hashed_account)

        if exists_account:  # Si ya existe en la bbdd, se actualiza ambas bbdd
            document = {'account': hashed_account}
            fields_to_update = {
                'clasification': clasification, 'analysis': user_analysis}
            app_utils.update_db_twitter(
                twiana_twitter, hashed_account, hashed_name, hashed_description,location, tweets)
            app_utils.update_collection(
                twiana_politics_analitycs, document, fields_to_update)
            app_utils.update_db_worries(
                twiana_worries, document, worries)

        else:
            document_twitter = {'account': hashed_account, 'name': hashed_name,
                                'description': hashed_description, 'location':location, 'tweets': tweets}
            document_politics_analitycs = {
                'account': hashed_account, 'clasification': clasification, 'analysis': user_analysis}
            app_utils.add_document(twiana_twitter, document_twitter)
            app_utils.add_document(
                twiana_politics_analitycs, document_politics_analitycs)
            document_worries = {'account': hashed_account, 'worries': worries}
            app_utils.add_document(twiana_worries, document_worries)

        json_user_result = {'resultados': user_analysis,
                            'clasificacion': {"partido":clasification}, 'preocupaciones': worries}
        response_json = json_util.dumps(json_user_result, indent=2)

        print("--- Finished in %s seconds ---" % (time.time() - start_time))
        if api:
            return Response(response_json, mimetype="application/json", status=201)
        else:
            return json_user_result
    except tweepy.TweepError as e:

        return Response("Usuario no válido", status=404)


@app.route('/service/prediction/account_visualizer', methods=['GET', 'POST'])
def account_visualizer_prediction():
    form = SearchForm()
    results = None
    if request.method == 'POST':
        account = form.account.data
        results = retrieve_clasification_worries(account,False)
    return render_template('search_account.html', form=form, results=results)

@app.route('/service/prediction/account/<account>', methods=['GET'])
def account_prediction(account):
    return retrieve_clasification_worries(account,True)
    

@app.route('/service/analytics/account/<account>', methods=['GET'])
def account_analytics(account):

    start_time = time.time()

    # El maximo de tweets sin usar cursor son 200
    tweets_limit = request.args.get('limit', default=200, type=int)

    try:
        worries = twiana.twiana_worries(account, tweets_limit)
        # Tomamos los datos del análisis y los codificamos

        hashed_account = hashlib.md5(account.encode()).hexdigest()

        exists_account = app_utils.check_existence(
            twiana_worries, 'account', hashed_account)

        if exists_account:  # Si ya existe en la bbdd, se actualiza ambas bbdd
            document = {'account': hashed_account}
            app_utils.update_db_worries(
                twiana_worries, document, worries)

        else:

            document_worries = {'account': hashed_account, 'worries': worries}
            app_utils.add_document(twiana_worries, document_worries)

        json_user_result = {'preocupaciones': worries}
        response_json = json_util.dumps(json_user_result, indent=2)

        print("--- Finished in %s seconds ---" % (time.time() - start_time))
        return Response(response_json, mimetype="application/json", status=201)
    except tweepy.TweepError as e:

        return Response("Usuario no válido", status=404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
