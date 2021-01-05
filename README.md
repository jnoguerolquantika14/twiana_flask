# twiana20
Versión 2.0 del proyecto Twiana

1. [Instalación](#instalación)
2. [Ejecución: Docker](#docker)
3. [Código](#código)

### Instalación
Con la descarga del proyecto, abriremos una terminal en la carpeta que genera el .zip descargado.
Instalamos docker:
``` bash
#Desinstalamos versiones antiguas:
sudo apt-get remove docker docker-engine docker.io containerd runc

#Instalamos dependencias
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

# Instalamos llave de cifrado
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Añadimos el repositorio
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

# Instalamos docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
``` 
___
### Docker
Podemos montar un contenedor en [Docker](https://www.docker.com/), donde se instalen las dependencias necesarias para que la aplicación funcione.
Para ello, dentro de la carpeta del proyecto (donde se ubica el fichero [Dockerfile]) ejecutamos el comando de construcción del contenedor (nótese que es importante tener la terminal abierta en el directorio donde se encuentra el [Dockerfile]).
``` bash
docker build -t twiana_flask .
```
Docker creará una imagen basada en [python:3.8-slim], a la cual le añadiremos las dependencias del fichero [requirements]. Para ejecutar el contenedor llamado twiana_flask, lo publicaremos en el puerto 5000 (mapeando el puerto de la aplicación dentro del contenedor, qur también es la 5000) ejecutando el siguiente comando:
``` bash
docker run -it --publish 5000:5000 twiana_flask
```
Con esto, la aplición quedará en http://localhost:5000/service/prediction/account/<account>. 
Podemos especificar la cuenta a analizar añadiendo el nombre de usuario y opcionalmente, el número de tweets a analizar (máximo 200) http://localhost:5000/service/prediction/account/Quantika14?limit=200. Si queremos ejecutar el contenedor como un proceso habría que añadir la opción `-d`.

Si queremos eliminar las imagenes descargadas:
``` bash
docker image prune  -a -f ; docker container prune -f ; docker image prune -a -f
```

[python:3.8-slim]: https://github.com/docker-library/python/tree/756285c50c055d06052dd5b6ac34ea965b499c15/3.8/buster/slim
___
### Código
* [app_utils]: Esta clase contiene funciones que se utilizarán en [app] con el fin de operar con las collecciones para actualizar sus documentos y campos.
  * check_existence: determina si en una base de datos, existe un campo con un valor determinados.
  * join_tweets: recibe los tweets que se han analizado y los que ya existen en la colección. Devuelve la lista de la unión de todos estos tweets sin repeticiones.
  * add_document: añade un documento a una colección.
  * update_collection: actualiza el documento de una colección.
  * update_db_twitter: busca el documento en la colección y determina qué campos actualizar.
  
* [app]: se conecta la base de datos de [MongoDB](https://www.mongodb.com/) y sus colecciones con la aplicación de Flask. Al ejecutar este fichero se arrancará la aplicación.
  * account_prediction: toma los datos del análisis de la cuenta y los almacena en las colecciones. Si la cuenta ya ha sido analizada, tendrá que actualizarse. Si es la primera vez que se analiza, se añade como un documento nuevo en las colecciones.
	
* [config]: se define la puntuación que asignará a nombre, cuenta, descripción o cuando el algoritmo encuentre un tipo de tweet determinado.

* [Dockerfile]: crea el contenedor docker.

* [keys]: almacena las claves que necesita la aplicación para consultar Twitter.

* [requirements]: contiene las dependencias necesarias para que funcione la aplicación.

* [train]: contiene varios análisis para generar los modelos de entrenamiento que se usará para determinar un resultado.

* [twiana]:
  * retrieve_user_data: construye el diccionario del análisis del usuario indicado. Para ello, obtiene los datos de la API y analiza cuenta, nombre, descripción y tweets.
  * process_timeline: paraleliza el análisis de los tweets positivos, negativos y neutros.
  * process_tweet_types: analiza los tweets del tipo de tweet indicado.
  * select_api_key: selecciona una api aleatoria de [keys].
  * connect_tweepy: hace la conexión con la api de Twitter.
  * parse_json_attrs: renombra todos los atributos del diccionario  que resulta del análisis.
  * modelo_Logit_binom: genera los modelos para que los use el algoritmo de clasificación.
  * funcion_ev_Logit_binom: clasifica un usuario a partir del análisis de sus tweets.
  * twiana: ejecuta las funciones de análisis y clasificación y devuelve los resultados.
	

* [utils]:
  * compute_score: suma la puntuación score al partido p en el diccionario de resultados.
  * replace_acentos: elimina los acentos de las palabras que se van a analizar.
  * remove_badWords: elimina signos de puntuación y otros caracteres que no sean útiles de las palabras que se van a analizar.
  * find_sense: devuelve una lista con las palabras positivas y negativas a partir de una lista de palabras.
  * find_words: devuelve el diccionario con los valores de cada partido.


[app_utils]:./app_utils.py
[app]:./app.py
[config]:./config.py
[Dockerfile]:./Dockerfile
[keys]:./keys.py
[requirements]:./requirements.txt
[train]:./train.json
[twiana]:./twiana.py
[utils]:./utils.py
