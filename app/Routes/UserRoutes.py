import bcrypt
from flask_uploads import UploadSet, IMAGES, configure_uploads

from app import app, mongo
from flask import request, send_file, json
from app.Lib.Reply import Reply
from app.Models.User import User
from app.Models.Post import Post

import requests

import re

# ok
@app.route('/login', methods=['POST'])
def login():
	salt = bcrypt.gensalt()

	print(bcrypt.hashpw(request.json['password'].encode(), salt))

	user = User.login(request.json['username'], request.json['password'])
	if user is not None:
		return Reply(user).ok()
	else:
		return Reply("Invalid username or password!").error()


@app.route('/test', methods=['POST', 'GET'])
def t():
	url = 'https://fcm.googleapis.com/fcm/send'
	body = {
		"data": {
			"title": "title",
			"body": "body",
			"url": "localhost"
		},
		"notification": {
			"title": "My web app name",
			"body": "message",
			"content_available": "true"
		},
		"to": "dOAtRjJSbkA:APA91bEdS5CvahhZgaqtFcG4PRzf6u2gjAhSjUei0V687eq-IAgm9LX3ZDEFLd6yI7Jf4Im30wA-9jZhjkNpd62bKeCXYyjiBff_9l2MabMHzn2xue3vp7KUgVmGLM1ROOUYhYjef_lz"
	}
	headers = {"Content-Type": "application/json", "Authorization": "key=AAAAxe-zm-c:APA91bFo5NK_jcUydvxbwbp1wWD3KCND2ul9xRLvZvi14aNjbAeQi6eJkbdU9wiFwawo7b6Af3rPuqoUH8q0vOfGYA40nRpIC436_SxBx2wbC1pl_CXTkA2Q_ev_yb-RUXQF66hS1YZq"}
	r= requests.post(url, data=json.dumps(body), headers=headers)
	return Reply(str(r.reason)).ok()

# maybe
@app.route('/search', methods=['POST', 'GET'])
@User.validate_user
def search(requester):
	query = mongo.db.users.find({"username": {"$regex": request.json["search"], "$options": "i"}})
	users = User.create_from_db_obj(query)
	overviews = [user.get_overview(requester) for user in users]

	return Reply(overviews).ok()


@app.route('/setNotificationKey', methods=['POST'])
@User.validate_user
def set_n_key(user):
	mongo.db.users.update({"username": user.username}, {"$set": {"notificationKey": request.json["key"]}}, upsert=True)
	mongo.db.posts.remove({})
	return Reply().ok()


@app.errorhandler(500)
def custom500(error):
	return Reply("Internal Server error!").error()


# ok
@app.route('/castVotes', methods=['POST'])
@User.validate_user
def cast_votes(user):
	return user.cast_votes(request.json["votes"])


# ok
@app.route('/getMutuals', methods=['POST'])
@User.validate_user
def get_mutuals(user):
	return Reply(user.get_mutuals()).ok()


# ok
@app.route('/follow', methods=['POST'])
@User.validate_user
def follow(user):
	return user.follow(request.json["user"], request.json["following"])


# ok
@app.route('/sendPost', methods=['POST'])
@User.validate_user
def send_post(user):
	return Post.create_post(
		user,
		request.json["to"],
		request.json["content"],
		request.json["title"],
		request.json["type"]
	).send(user)


# ok
@app.route('/getQueue', methods=['POST'])
@User.validate_user
def get_queue(user):
	return user.get_queue()


# prob ok
@app.route('/getPost', methods=['POST'])
@User.validate_user
def get_post(user):
	return user.get_post(request.json["id"])


# ok
@app.route('/getArchive', methods=['POST'])
@User.validate_user
def get_archive(user):
	return Reply(user.get_archive(request.json["page"], request.json["count"])).ok()


# ok
@app.route('/getPatch/<username>', methods=["GET", 'POST'])
def get_patch(username):
	user = User.get_from_username(username)
	print(user)
	path = user.get_patch_path()
	return send_file(path, mimetype='image/png')


# prob ok
@app.route('/setPatch', methods=['POST'])
def set_patch():
	user = User.create_from_db_obj.User(mongo.db.users.find_one({"sessionKey": request.form["apiKey"]}))
	photos = UploadSet('photos', IMAGES)
	if request.method == 'POST' and 'pic' in request.files:
		configure_uploads(app, photos)
		filename = photos.save(request.files['pic'])
		user.set_patch(filename)
		return Reply().ok()
	else:
		return Reply("could not save image!").error()


