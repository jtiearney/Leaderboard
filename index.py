from flask import Flask
import redis
import random
import uuid
from oboeware import OboeMiddleware
import oboe
oboe.config['tracing_mode'] = 'always'

r = redis.StrictRedis(host='172.17.0.2', port=6379, db=0)
app = Flask(__name__)
app.wsgi_app = OboeMiddleware(app.wsgi_app)
@app.route("/genUserId/<username>")
def genUserId(username):
	if getUserId(username) is not None:
		return str(0)
	else:
		newId = uuid.uuid4().hex
		r.hset(newId, 'username', username)
		r.hset('users', username, newId)
		return str(1)
	
def getUserId(username):
	return r.hget('users', username)

def getUsername(userId):
	return r.hget(userId, 'username')

@app.route("/getLeaderboard")
def getLeaderboard():
	numScores = 0
	leaders = r.zrevrange('dsd', 0, -1, 'withscores')
	for items in leaders:
		if numScores == 0:
			response = str(getUsername(items[0])) + ',' + str(items[1])
		else:
			response = response + ':' + str(getUsername(items[0])) + ',' + str(items[1])
		numScores = 1
	return str(response)
	
@app.route("/setLeaderboard/<userId>")
def setLeaderboard(userId):
	score = random.randint(1,10000)
	text = str(r.zadd('dsd', score, userId))
	return text

if __name__ == "__main__":
	app.run()
