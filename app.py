from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from customjson import JSONEncoder

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'tweets_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/' + app.config['MONGO_DBNAME']

mongo = PyMongo(app)


@app.route('/tweets', methods=['GET'])
def tweets():
    more_than = request.args.get('morethan') #if key doesn't exist, returns None
    tweets_db = mongo.db.tweets
    output = {}
    count = 1

    for tweet in tweets_db.find():
        if more_than != None:
            if len(tweet['entities']['hashtags']) < int(more_than):
                continue

        output['tweet_' + str(count)] = tweet
        count += 1

    if output == {}:
        return jsonify({"ok": False, "message": "No tweets found"}), 404

    return JSONEncoder().encode(output)

@app.route('/tweets/hashtag/<hashtag>', methods=['GET'])
def get_hashtagged_tweets(hashtag):
    tweets_db = mongo.db.tweets
    output = {}
    count = 1

    for tweet in tweets_db.find():
        if 'entities' not in tweet:
            continue

        for candidate in tweet['entities']['hashtags']:
            if hashtag == candidate['text']:
                output['tweet_' + str(count)] = tweet
                count += 1

    if output == {}:
        return jsonify({"ok": False, "message": "No tweets found"}), 404

    return JSONEncoder().encode(output)

@app.route('/post', methods=['POST'])
def post():
    tweet = request.json

    if tweet == None:
        return jsonify({"ok": False, "message": "Possibly wrong Content-Type"}), 400

    if tweet.get('user', None) is None or tweet.get('message', None) is None or tweet.get('age', None) is None:
        return jsonify({"ok": False, "message": "Bad parameters"}), 400

    mongo.db.tweets.insert_one({
        'user' : tweet['user'],
        'message' : tweet['message'],
        'age': tweet['age']
    })

    return JSONEncoder().encode(tweet), 201

@app.route('/tweets/hashtag/<hashtag>', methods=['DELETE'])
def delete_hashtagged_tweets(hashtag):
    tweets_db = mongo.db.tweets
    to_be_removed = []

    for tweet in tweets_db.find():
        if 'entities' not in tweet:
            continue

        for candidate in tweet['entities']['hashtags']:
            if hashtag == candidate['text']:
                to_be_removed.append(tweet['_id'])

    tweets_db.delete_many({
        '_id': {
            '$in': to_be_removed
        }
    })

    return jsonify({'removedCount': len(to_be_removed)})

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'ok': False, 'message': 'Wrong endpoint'}), 400

if __name__ == '__main__':
    app.run(debug=True)
