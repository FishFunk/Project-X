""" 
app.py
"""

from flask import *
import os, json, uuid, urllib2, cookielib, utils
from dbService import dbService
from models import Post

app = Flask(__name__)
dbService = dbService()
imgPath = "/Users/Daniel/bin/AppData/ProjectX/Images"
app.config['UPLOAD_FOLDER'] = imgPath

@app.route("/")
def index():
	return render_template('index.html')

@app.route('/search', methods=['GET','POST'])
def search():
	searchVal = request.get_json().get('searchVal')
	resultPosts = dbService.searchPostTable(searchVal)

	for post in resultPosts:
		post['photos'] = utils.ReadFilesFromDirectory(os.path.join(imgPath, post['guid']))

	result = json.dumps(resultPosts)
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
		WritePhotos(guid, photos)

		print "Successfully created post!"
	except IOError, e:
		print "DB Service Failure. %s, %s" % (e.args[0], e.args[1])

	return ""

@app.route('/image_uploads', methods=['GET'])
def uploaded_file():
	return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 
		request.args.get('guid')), request.args.get('filename'))



def WritePhotos(guid, photos):
	count = 0
	for p in photos:
		path = os.path.join(imgPath, str(guid))
		filename = "%s.jpg" % count
		utils.WriteBase64FileToPath(path, filename, p['base64'])
		count+=1

if __name__ == "__main__":
	app.run(port=8080, debug=True)
	#app.run(host='0.0.0.0', debug=True) # public on network