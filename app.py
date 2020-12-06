import os
from IPython.core import display as ICD
import pandas as pd
from flask import Flask, jsonify, request, Response
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config['MONGO_URI'] = 'mongodb://localhost:27017/twianamongodb'

mongo = PyMongo(app)

global CURR_DIR
CURR_DIR = os.path.dirname(os.path.abspath(__file__))

def tabla_diccionario(diccionario,key_diccionario_input,value_diccionario_input,key_diccionario_output,value_diccionario_output): #Para crear una tabla a partir de un diccionario
    #Se especifica el diccionario, su key y value, y la key y value que tendrá en la tabla resultante
    longitud_diccionario=len(diccionario)
    #Creamos las filas para los nuevos key y value
    nuevo_key=[0]*(longitud_diccionario)
    nuevo_value=[0]*(longitud_diccionario)
    for i in range(longitud_diccionario):
        #Defimos cada valor de las 2 filas del diccionario
        nuevo_key[i]=diccionario[i][key_diccionario_input]
        nuevo_value[i]=diccionario[i][value_diccionario_input]

    # Metodo para crear una tabla: https://stackoverflow.com/questions/60076770/power-bi-dataframe-table-visualization
    dataset = pd.DataFrame({key_diccionario_output: nuevo_key, value_diccionario_output: nuevo_value},index=['']*longitud_diccionario)
    return dataset


@app.route('/data_ejemplo', methods=['GET'])
def get_data():
    f = open(CURR_DIR+'/data_ejemplo.json')
    data_ejemplo = json.load(f)

    response = json_util.dumps(data_ejemplo, indent=2)
    # print(response)
    
    return Response(response, mimetype="application/json")


'''
@app.route('/service/prediction/account', methods=['POST'])
def account_prediction:
    return 
'''


@app.route('/service/analytics/city/<city>', methods=['GET'])
def city_analytics(city):
    f = open(CURR_DIR+'/data_ejemplo.json')
    data_ejemplo = json.load(f)
    json_data = data_ejemplo['data']
    json_worries = data_ejemplo['worries']
    json_undecided = data_ejemplo['undecided']
    # json_dict={'json_data':json_data,'json_worries':json_worries,'json_undecided':json_undecided}
    #json_dict = (json_data, json_worries, json_undecided)
    tabla=tabla_diccionario(json_data,)
    ICD.display()
    
    response = json_util.dumps(json_data, indent=2)
    return Response(response)


if __name__ == "__main__":
    app.run(debug=True)
