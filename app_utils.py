def check_existence(db, field, value):
    if db.find_one({field: value}):
        return True
    else:
        return False


def join_tweets(tweets_db, tweets):  # Une las dos listas de tweets y elimina los repetidos
    tweets_db.extend(tweets)
    unduplicated_tweets = list(dict.fromkeys(tweets_db))
    return unduplicated_tweets


def add_document(collection, fields_values):
    collection.insert_one(fields_values)


def update_collection(collection, document, fields_to_update):
    collection.update_one(document, {"$set": fields_to_update})


def update_db_twitter(db, account, name, description, tweets):
    document = {'account': account}
    db_element = db.find_one(document)

    same_name = db_element['name'] == name
    same_description = db_element['description'] == description

    fields_to_update = {}  # Las propiedades que se van a modificar
    if not same_name:
        fields_to_update['name'] = name
    elif not same_description:
        fields_to_update['description'] = description

    fields_to_update['tweets'] = join_tweets(db_element['tweets'], tweets)

    update_collection(db, document, fields_to_update)


def update_db_worries(db, account, worries):
    document = {'account': account}

    fields_to_update = {}  # Las propiedades que se van a modificar

    fields_to_update['worries'] = worries

    update_collection(db, document, fields_to_update)