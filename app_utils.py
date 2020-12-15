def check_existence(db,property,value):
    if db.find_one({property:value}):
        return True
    else:
        return False


def join_tweets(tweets_db,tweets):
    tweets_db.extend(tweets)
    unduplicated_tweets=list(dict.fromkeys(tweets_db))
    return unduplicated_tweets

def update_db_twitter(db,account,name,description,tweets):

    db_element=db.find_one({'account':account})

    same_name= db_element['name']==name
    same_description= db_element['description']==description

    fields_to_update={}
    if not same_name :
        fields_to_update['name']=name
    elif not same_description:
        fields_to_update['description']=description
    
    fields_to_update['tweets']=join_tweets(db_element['tweets'],tweets)
  
    db.update_one({'account':account},{"$set":fields_to_update})

        