from flask_uploads import UploadSet, IMAGES, configure_uploads

from app import app, mongo
from flask import request, send_file
from app.Lib.Reply import Reply
from app.Models.User import User
from app.Models.Post import Post


# ok
@app.route('/login', methods=['POST'])
def login():
	user = User.login(request.json['username'], request.json['password'])
	if user is not None:
		return Reply(user).ok()
	else:
		return Reply("Invalid username or password!").error()


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
	user = User.create_from_db_obj(mongo.db.users.find_one({"username": username}))
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


