import os
from IPython.core import display as ICD
import pandas as pd
from flask import Flask, jsonify, request, Response, render_template
from flask_pymongo import PyMongo
from bson import json_util
from bson.objectid import ObjectId
import json

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')

app.config['MONGO_URI'] = 'mongodb://localhost:27017/twianamongodb'

mongo = PyMongo(app)

global CURR_DIR
CURR_DIR = os.path.dirname(os.path.abspath(__file__))


# Para crear una tabla a partir de un diccionario
def tabla_diccionario(diccionario, key_diccionario_input, value_diccionario_input, key_diccionario_output, value_diccionario_output):
    # Se especifica el diccionario, su key y value, y la key y value que tendrá en la tabla resultante
    longitud_diccionario = len(diccionario)
    # Creamos las filas para los nuevos key y value
    nuevo_key = [0]*(longitud_diccionario)
    nuevo_value = [0]*(longitud_diccionario)
    for i in range(longitud_diccionario):
        # Defimos cada valor de las 2 filas del diccionario
        nuevo_key[i] = diccionario[i][key_diccionario_input]
        nuevo_value[i] = diccionario[i][value_diccionario_input]

    # Metodo para crear una tabla: https://stackoverflow.com/questions/60076770/power-bi-dataframe-table-visualization
    dataset = pd.DataFrame({key_diccionario_output: nuevo_key,
                            value_diccionario_output: nuevo_value}, index=['']*longitud_diccionario)
    return dataset


def plot_rendimiento(indices, valores):
    import matplotlib.pyplot as plt
    # this is for plotting purpose
    indexes = indices
    values = valores

    plt.figure(figsize=(20, 5))

    plt.bar(indexes, values)
    plt.xlabel('Partidos', fontsize=8)
    plt.ylabel('Resultados', fontsize=8)
    plt.xticks(indexes, fontsize=10, rotation=30)
    plt.title('Gráfico de resultados')
    return plt.show()


@app.route('/service/analytics/city/<city>', methods=['GET'])
def city_analytics(city):
    f = open(CURR_DIR+'/data_ejemplo.json')
    data_ejemplo = json.load(f)
    json_data = data_ejemplo['data']
    json_worries = data_ejemplo['worries']
    json_undecided = data_ejemplo['undecided']
    # json_dict={'json_data':json_data,'json_worries':json_worries,'json_undecided':json_undecided}
    #json_dict = (json_data, json_worries, json_undecided)
    # tabla=tabla_diccionario(json_data,)
    # tabla=ICD.display(json_data)

    #response = json_util.dumps(json_data, indent=2)
    #tabla_dir=os.path.join(os.getcwd(), 'templates', 'tabla.html')

    # return render_template("tabla.html",result=json_data)
    # return ICD.display(json_data)

    indices = list(json_data.keys())
    valores = list(json_data.values())
    response = plot_rendimiento(indices, valores)
    return Response(response)


if __name__ == "__main__":
    app.run(debug=True)
