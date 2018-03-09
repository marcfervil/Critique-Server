from flask import render_template
from flask import request
from flask import make_response,redirect
from app import app
from app import mongo
from flask import jsonify
from app import UserManager
from flask import send_from_directory
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)



@app.route('/')
def index():
	return render_template("index.html")


@app.route('/static/<path:path>')
def send_js(path):
	return send_from_directory('static', path)


@app.route('/login', methods=['POST'])
def login():
	#print(request.data);
	loginVal=UserManager.login(request.json['username'],request.json['password'])
	if loginVal != None:
		#response = make_response(redirect('/home'))
		#response.set_cookie('sessionKey', str(loginVal))
		return jsonify({"status":"ok", "apiKey":str(loginVal)})
	else:
		return jsonify({"status":"error", "message":"invalid username or password!"})



@app.route('/getPosts', methods=['POST'])
@UserManager.validateUser
def getPosts(user):
	#print(list(user.getPosts()))
	#return "ye"
	return JSONEncoder().encode(user.getPosts())
	#return jsonify(list(user.getPosts()))

	



@app.route('/invalid')
def invalid():
	return "bad username or password"



@app.route('/home')
@UserManager.validateUser
def home(user):
	return "Hello, "+user.getUsername()



@app.route('/test')
def about():
	#mongo.db.users.remove({})
	mongo.db.posts.remove({})
	#mongo.db.users.insert({"username":"marc","password":"nohash","sessionKey":"823gfc32gf8723gf83g27"})
	
	mongo.db.posts.insert({"username":"marc","seen":[],"to":["marc","john"],"text":"test"})
	mongo.db.posts.insert({"username":"john","seen":[],"to":["john"],"text":"test"})
	mongo.db.posts.insert({"username":"john","seen":[],"to":["marc"],"text":"join the critique team"})
	mongo.db.posts.insert({"username":"ueee","seen":[],"to":["fast","marc"],"text":"test"})
	
	

	return "just doing stuff"