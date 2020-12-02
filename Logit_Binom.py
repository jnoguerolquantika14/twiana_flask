import pandas as pd
import json
import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import pickle

def modelo_Logit_binom(json_viejos):
    with open(json_viejos) as f:
        data = json.load(f)
    # Creación de las variables anidadas en las listas
    for user in data:
        # Account
        tamo = user.pop("account")
        user["account_pp"] = tamo["pp"]
        user["account_psoe"] = tamo["psoe"]
        user["account_vox"] = tamo["vox"]
        user["account_podemos"] = tamo["podemos"]
        user["account_cs"] = tamo["cs"]
        user["account_pacma"] = tamo["pacma"]
        # Username
        tamo2 = user.pop("username")
        user["username_pp"] = tamo2["pp"]
        user["username_psoe"] = tamo2["psoe"]
        user["username_vox"] = tamo2["vox"]
        user["username_podemos"] = tamo2["podemos"]
        user["username_cs"] = tamo2["cs"]
        user["username_pacma"] = tamo2["pacma"]
        # Description
        tamo3 = user.pop("description")
        user["description_pp"] = tamo3["pp"]
        user["description_psoe"] = tamo3["psoe"]
        user["description_vox"] = tamo3["vox"]
        user["description_podemos"] = tamo3["podemos"]
        user["description_cs"] = tamo3["cs"]
        user["description_pacma"] = tamo3["pacma"]
        # Tweets - Positivos
        tamo4 = user.pop("tweets-pos")
        user["tweets-pos_pp"] = tamo4["pp"]
        user["tweets-pos_psoe"] = tamo4["psoe"]
        user["tweets-pos_vox"] = tamo4["vox"]
        user["tweets-pos_podemos"] = tamo4["podemos"]
        user["tweets-pos_cs"] = tamo4["cs"]
        user["tweets-pos_pacma"] = tamo4["pacma"]
        # Tweets - Negativos
        tamo5 = user.pop("tweets-neg")
        user["tweets-neg_pp"] = tamo5["pp"]
        user["tweets-neg_psoe"] = tamo5["psoe"]
        user["tweets-neg_vox"] = tamo5["vox"]
        user["tweets-neg_podemos"] = tamo5["podemos"]
        user["tweets-neg_cs"] = tamo5["cs"]
        user["tweets-neg_pacma"] = tamo5["pacma"]
        # Tweets - Neutros
        tamo6 = user.pop("tweets-neu")
        user["tweets-neu_pp"] = tamo6["pp"]
        user["tweets-neu_psoe"] = tamo6["psoe"]
        user["tweets-neu_vox"] = tamo6["vox"]
        user["tweets-neu_podemos"] = tamo6["podemos"]
        user["tweets-neu_cs"] = tamo6["cs"]
        user["tweets-neu_pacma"] = tamo6["pacma"]
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
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    modelos = {}
    data_X_train = datos_final_binom.iloc[:, 7:43]
    escalar = StandardScaler()
    X_train = escalar.fit_transform(data_X_train)
    with open("obj.pickle", "wb") as f:
        pickle.dump(escalar, f)
    for i in range(6):
        Y_train =  datos_final_binom.iloc[:, i + 1]
        LR = LogisticRegression().fit(X_train, Y_train)
        joblib.dump(LR, f'modelo_{partidos[i]}.pkl')


def funcion_ev_Logit_binom(json_nuevos):
    with open(json_nuevos) as f:
        data2 = json.load(f)
    # Creación de las variables anidadas en las listas
    for user in data2:
        # Account
        tamo = user.pop("account")
        user["account_pp"] = tamo["pp"]
        user["account_psoe"] = tamo["psoe"]
        user["account_vox"] = tamo["vox"]
        user["account_podemos"] = tamo["podemos"]
        user["account_cs"] = tamo["cs"]
        user["account_pacma"] = tamo["pacma"]
        # Username
        tamo2 = user.pop("username")
        user["username_pp"] = tamo2["pp"]
        user["username_psoe"] = tamo2["psoe"]
        user["username_vox"] = tamo2["vox"]
        user["username_podemos"] = tamo2["podemos"]
        user["username_cs"] = tamo2["cs"]
        user["username_pacma"] = tamo2["pacma"]
        # Description
        tamo3 = user.pop("description")
        user["description_pp"] = tamo3["pp"]
        user["description_psoe"] = tamo3["psoe"]
        user["description_vox"] = tamo3["vox"]
        user["description_podemos"] = tamo3["podemos"]
        user["description_cs"] = tamo3["cs"]
        user["description_pacma"] = tamo3["pacma"]
        # Tweets - Positivos
        tamo4 = user.pop("tweets-pos")
        user["tweets-pos_pp"] = tamo4["pp"]
        user["tweets-pos_psoe"] = tamo4["psoe"]
        user["tweets-pos_vox"] = tamo4["vox"]
        user["tweets-pos_podemos"] = tamo4["podemos"]
        user["tweets-pos_cs"] = tamo4["cs"]
        user["tweets-pos_pacma"] = tamo4["pacma"]
        # Tweets - Negativos
        tamo5 = user.pop("tweets-neg")
        user["tweets-neg_pp"] = tamo5["pp"]
        user["tweets-neg_psoe"] = tamo5["psoe"]
        user["tweets-neg_vox"] = tamo5["vox"]
        user["tweets-neg_podemos"] = tamo5["podemos"]
        user["tweets-neg_cs"] = tamo5["cs"]
        user["tweets-neg_pacma"] = tamo5["pacma"]
        # Tweets - Neutros
        tamo6 = user.pop("tweets-neu")
        user["tweets-neu_pp"] = tamo6["pp"]
        user["tweets-neu_psoe"] = tamo6["psoe"]
        user["tweets-neu_vox"] = tamo6["vox"]
        user["tweets-neu_podemos"] = tamo6["podemos"]
        user["tweets-neu_cs"] = tamo6["cs"]
        user["tweets-neu_pacma"] = tamo6["pacma"]
    datos_final_nuevos = pd.DataFrame(data2)
    ##########################################################
    partidos = ["pp", "psoe", "vox", "podemos", "cs", "pacma"]
    clasif = pd.DataFrame([])
    probab = pd.DataFrame([])
    clasif['usuario'] = datos_final_nuevos.iloc[:, 0]
    probab['usuario'] = datos_final_nuevos.iloc[:, 0]
    data_X_test = datos_final_nuevos.iloc[:, 1:]
    with open("obj.pickle", "rb") as f:
        escalar = pickle.load(f)
    X_test = escalar.transform(data_X_test)  
    for i in range(6):
        # Modelos Logisticos
        LR = joblib.load(f'modelo_{partidos[i]}.pkl')
        Y_pred = LR.predict(X_test)
        Y_prob = LR.predict_proba(X_test)
        clasif[f'{partidos[i]}'] = Y_pred
        probab[f'{partidos[i]}'] = Y_prob[:, 1]
    clasif["clasif2"] = probab[['pp', 'psoe', 'vox', 'podemos', 'cs', 'pacma']].idxmax(axis = 1)
    print(clasif.iloc[:,[0,7]])


'''
modelos(datos_viejos_json)
funcion_completa2(datos_nuevos_json)
'''