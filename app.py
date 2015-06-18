""" 
Sample.py
"""

from flask import Flask, jsonify, render_template, request
import json, uuid
from dbService import dbService
from models import Post

app = Flask(__name__)
dbService = dbService()

@app.route("/")
def index():
	return render_template('index.html')

@app.route('/search', methods=['GET','POST'])
def search():
	searchVal = request.get_json().get('searchVal')
	resultPosts = dbService.searchPostTable(searchVal)
	result = json.dumps(resultPosts)
	print result
	return result

@app.route('/upload', methods=['GET','POST'])
def upload():
	reqJson = request.get_json()
	title = reqJson.get('title')
	desc = reqJson.get('description')
	email = reqJson.get('email')
	price = reqJson.get('price')
	loc = reqJson.get('location')
	phone = reqJson.get('phone')

	# Create Unique Identifier
	guid = uuid.uuid4()

	# Handle photos separately
	photos = reqJson.get('photos')

	post = Post(guid, title, desc, email, price, loc, phone)

	try:
		dbService.insertPost(post)
		dbService.insertPhotos(guid, photos)
		print "Successfully created post!"
	except:
		print "DB Service Failure"

	return ""

if __name__ == "__main__":
	app.run(port=8080, debug=True)
	#app.run(host='0.0.0.0') # public on network