import pandas as pd
import json
import os
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pickle

global CURR_DIR
CURR_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_json_attrs(user,politic_parties,attribute):
    tamo = user.pop(attribute) #Se toma todo el contenido del atributo
    for party in politic_parties:
        user[attribute+"_"+party] = tamo[party] #Se extrae el valor de cada array del atributo

def modelo_Logit_binom(json_entrenamiento):
    with open(json_entrenamiento) as f:
        data = json.load(f)
    # Creación de las variables anidadas en las listas
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    for user in data:
        parse_json_attrs(user,partidos,"account") # Account
        parse_json_attrs(user,partidos,"username") # Username
        parse_json_attrs(user,partidos,"description") # Description
        parse_json_attrs(user,partidos,"tweets-pos") # Tweets - Positivos
        parse_json_attrs(user,partidos,"tweets-neg") # Tweets - Negativos
        parse_json_attrs(user,partidos,"tweets-neu") # Tweets - Neutros
        
    datos_final = pd.DataFrame(data)
    
    # Arreglo de valores de la variable iv
    datos_final.loc[datos_final['iv'] == 'pp\n', 'iv'] = 'pp'
    datos_final.loc[datos_final['iv'] == 'psoe\n', 'iv'] = 'psoe'
    datos_final.loc[datos_final['iv'] == 'vox\n', 'iv'] = 'vox'
    datos_final.loc[datos_final['iv'] == 'podemos\n', 'iv'] = 'podemos'
    datos_final.loc[datos_final['iv'] == 'cs\n', 'iv'] = 'cs'
    datos_final.loc[datos_final['iv'] == 'pacma\n', 'iv'] = 'pacma'
    
    # Eliminación de votantes de upyd
    datos_final = datos_final.drop(datos_final[datos_final['iv'] == "upyd\n"].index)
    
    datos_final["iv"] = datos_final["iv"].astype('category')
    
    datos_final_binom = pd.get_dummies(datos_final, columns = ["iv"])
    
    datos_final_binom = datos_final_binom.reindex(
        columns = ["name", "iv_pp", "iv_psoe", "iv_vox", "iv_podemos", "iv_cs", "iv_pacma", 'account_pp',
                   'account_psoe',
                   'account_vox', 'account_podemos',
                   'account_cs', 'account_pacma', 'username_pp', 'username_psoe',
                   'username_vox', 'username_podemos', 'username_cs', 'username_pacma',
                   'description_pp', 'description_psoe', 'description_vox',
                   'description_podemos', 'description_cs', 'description_pacma',
                   'tweets-pos_pp', 'tweets-pos_psoe', 'tweets-pos_vox',
                   'tweets-pos_podemos', 'tweets-pos_cs', 'tweets-pos_pacma',
                   'tweets-neg_pp', 'tweets-neg_psoe', 'tweets-neg_vox',
                   'tweets-neg_podemos', 'tweets-neg_cs', 'tweets-neg_pacma',
                   'tweets-neu_pp', 'tweets-neu_psoe', 'tweets-neu_vox',
                   'tweets-neu_podemos', 'tweets-neu_cs', 'tweets-neu_pacma'])
    datos_final_binom['iv'] = datos_final['iv']

    modelos = {}
    
    data_X_train = datos_final_binom.iloc[:, 7:43] #Para dejar fuera al nombre y los account_x
    
    escalar = StandardScaler()
    X_train = escalar.fit_transform(data_X_train)
    print(data_X_train)
    with open("obj.pickle", "wb") as f:
        pickle.dump(escalar, f)
    for i in range(len(partidos)):
        Y_train =  datos_final_binom.iloc[:, i + 1]
        
        LR = LogisticRegression().fit(X_train, Y_train)
        
        joblib.dump(LR, f'modelo_{partidos[i]}.pkl')


def funcion_ev_Logit_binom(json_user):
    with open(json_user) as f:
        data2 = json.load(f)
    # Creación de las variables anidadas en las listas
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    for user in data2:
        parse_json_attrs(user,partidos,"account") # Account
        parse_json_attrs(user,partidos,"username") # Username
        parse_json_attrs(user,partidos,"description") # Description
        parse_json_attrs(user,partidos,"tweets-pos") # Tweets - Positivos
        parse_json_attrs(user,partidos,"tweets-neg") # Tweets - Negativos
        parse_json_attrs(user,partidos,"tweets-neu") # Tweets - Neutros
    datos_final_nuevos = pd.DataFrame(data2)
    ##########################################################
    
    clasif = pd.DataFrame([])
    probab = pd.DataFrame([])
    clasif['usuario'] = datos_final_nuevos.iloc[:, 0]
    probab['usuario'] = datos_final_nuevos.iloc[:, 0]
    
    data_X_test = datos_final_nuevos.iloc[:, 1:] # Quita la columna name

    with open("obj.pickle", "rb") as f:
        escalar = pickle.load(f)
    X_test = escalar.transform(data_X_test)  

    for i in range(len(partidos)):
        # Modelos Logisticos
        LR = joblib.load(f'modelo_{partidos[i]}.pkl')
        Y_pred = LR.predict(X_test) # Predice la etiqueta
        Y_prob = LR.predict_proba(X_test) # Estimación de probabilidad
        
        clasif[f'{partidos[i]}'] = Y_pred  # Etiquetas (partidos) más probables
        probab[f'{partidos[i]}'] = Y_prob[:, 1] # Probabilidades de cada partido

    clasif["clasif2"] = probab[['pp', 'psoe', 'vox', 'podemos', 'cs', 'pacma']].idxmax(axis = 1)

    pred=clasif.iloc[:,[0,7]]
    print(pred)