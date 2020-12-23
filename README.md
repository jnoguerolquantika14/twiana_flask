# twiana20
Versión 2.0 del proyecto Twiana

1. [Instalación](#instalación)
2. [Ejecución: Docker](#docker)
3. [Código](#código)

### Instalación
Con la descarga del proyecto, abriremos una terminal en la carpeta que genera el .zip descargado.
Instalamos docker:
``` python
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
``` python
docker build -t twiana_flask .
```
Docker creará una imagen basada en [python:3.8-slim], a la cual le añadiremos las dependencias del fichero [requirements]. Para ejecutar el contenedor llamado twiana_flask, lo publicaremos en el puerto 5000 (mapeando el puerto de la aplicación dentro del contenedor, qur también es la 5000) ejecutando el siguiente comando:
``` python
docker run -it --publish 5000:5000 twiana_flask
```
Con esto, la aplición quedará en http://localhost:5000/service/prediction/account/. 
Podemos especificar la cuenta a analizar añadiendo el nombre de usuario y opcionalmente, el número de tweets a analizar (máximo 200) http://localhost:5000/service/prediction/account/Quantika14?limit=200.
Si queremos eliminar las imagenes descargadas:
``` python
docker image prune  -a -f ; docker container prune -f ; docker image prune -a -f
```

[python:3.8-slim]: https://github.com/docker-library/python/tree/756285c50c055d06052dd5b6ac34ea965b499c15/3.8/buster/slim
___
### Código
* [app_utils]: Esta clase contiene funciones que se utilizarán en app.py con el fin de operar con las collecciones para actualizar sus documentos y campos.
  * check_existence: determina si en una base de datos, existe un campo con un valor determinados.
  * join_tweets: recibe los tweets que se han analizado y los que ya existen en la colección. Devuelve la lista de la unión de todos estos tweets sin repeticiones.
  * add_document: añade un documento a una colección.
  * update_collection: actualiza el documento de una colección.
  * update_db_twitter: busca el documento en la colección y determina qué campos actualizar.
  






[app_utils]:./app_utils.py
[requirements]:./requirements.txt
[Dockerfile]:./Dockerfile
