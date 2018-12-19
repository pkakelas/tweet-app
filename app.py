from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'tweets_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/' + app.config['MONGO_DBNAME']

mongo = PyMongo(app)

@app.route('/tweets', methods=['GET'])
def tweets():
    tweets_db = mongo.db.tweets
    output = []

    for tweet in tweets_db.find():
        output.append({
            'user' : tweet['user'],
            'message' : tweet['message'],
            'age': tweet['age']
        })

    return jsonify(output)

@app.route('/tweets/hashtag', methods=['GET'])
def get_hashtagged_tweets(hashtag):
    tweets_db = mongo.db.tweets
    regex = ".*" + hashtag + ".*"

    tweets = tweets_db.find({'message': {
        "$regex": regex
    }})

    if tweets:
        output = tweets
    else:
        output = "No such tweet"
    return jsonify({'result' : output})

@app.route('/post', methods=['POST'])
def post():
    tweet = request.get_json()

    if tweet.get('user', None) is None or tweet.get('message', None) is None or tweet.get('age', None) is None:
        return jsonify({"ok": False, "message": "Bad parameters"}), 400

    print(tweet)
    mongo.db.tweets.insert_one({
        'user' : tweet['user'],
        'message' : tweet['message'],
        'age': tweet['age']
    })

    return jsonify(tweet)

if __name__ == '__main__':
    app.run(debug=True)
