""" 
app.py
"""

from flask import *
import os, json, uuid, urllib2, cookielib, utils, smtplib, shutil
from email.mime.text import MIMEText
from dbService import dbService
from models import Post

app = application = Flask(__name__)
dbService = dbService()
imgPath = "/Users/Daniel/bin/AppData/ProjectX/Images"
app.config['UPLOAD_FOLDER'] = imgPath

@app.route("/")
def index():
	return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
	searchVal = request.get_json().get('searchVal')
	resultPosts = dbService.searchPostTable(searchVal)

	for post in resultPosts:
		post['photos'] = utils.ReadFilesFromDirectory(os.path.join(imgPath, post['guid']))

	result = json.dumps(resultPosts)
	return result

@app.route('/upload', methods=['GET','POST'])
def upload():
	newPost = dict()
	
	reqJson = request.get_json()
	newPost['title'] = reqJson.get('title')
	newPost['desc'] = reqJson.get('desc')
	newPost['email'] = reqJson.get('email')
	newPost['price'] = reqJson.get('price')
	newPost['zip'] = reqJson.get('zip')
	newPost['phone'] = reqJson.get('phone')
	newPost['guid'] = uuid.uuid4()

	# Handle photos separately
	photos = reqJson.get('photos')

	try:
		dbService.insertPost(newPost)
		WritePhotos(newPost['guid'], photos)
		#SendConfirmEmail("FishFry62@gmail.com","FishFry62@gmail.com", newPost['guid'])
		print "Successfully created post"
	except Exception, e:
		print "Failure creating post. %s" % e
	return ""

@app.route('/update', methods=['GET', 'POST'])
def update():
	
	post = dict()
	
	reqJson = request.get_json()
	post['title'] = reqJson.get('title')
	post['desc'] = reqJson.get('desc')
	post['email'] = reqJson.get('email')
	post['price'] = reqJson.get('price')
	post['zip'] = reqJson.get('zip')
	post['phone'] = reqJson.get('phone')
	post['guid'] = reqJson.get('guid')
	post['photos'] = reqJson.get('photos')

	try:
		dbService.updatePost(post)
		WritePhotos(post['guid'], post['photos'])
		print "Successfully updated post"
	except Exception, e:
		print "Failed to update post - %s" % e
	return ""

@app.route('/image_uploads', methods=['GET'])
def uploaded_file():
	return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 
		request.args.get('guid')), request.args.get('filename'))

@app.route('/flag_post', methods=['POST'])
def flag_post():
	reqJson = request.get_json()
	guid = reqJson.get('guid')
	try:
		dbService.flagPost(guid)
	except Exception, e:
		print "DB Service Failure - failed to flag post. %s" % e
	return "OK"

@app.route('/delete_post', methods=['POST'])
def delete_post():
	reqJson = request.get_json()
	guid = reqJson.get('guid')
	try:
		print "Deleting... #" + guid
		dbService.deletePost(guid)
		shutil.rmtree(os.path.join(imgPath, guid))
	except Exception, e:
		print "Failed to delete post. %s" % e
	return "OK"

@app.route('/edit/<post_guid>', methods=['GET', 'POST'])
def edit_post(post_guid):
	result = ""
	post = dbService.getPostByGuid(post_guid)
	photos = utils.ReadFilesFromDirectory(os.path.join(imgPath, post_guid))
	photoPaths = list()
	for fileName in photos:
		photoPaths.append("/image_uploads?guid=%s&filename=%s" % (post_guid, fileName))
	post['photos'] = photoPaths
	result = json.dumps(post)
	return result

def SendConfirmEmail(sender, receiver, guid):
	msg = '''High five! Your post is now live on ProjectX.
	Made a mistake? Have no fear! Below is your unique link that you can use to make edits
	to your post if need be. This link is crafted just for you so be careful not to share
	this link with anybody or else they can mess up your beautiful post!
	\n\nhttp://localhost:8080/#/edit/%s''' % guid

	mimeTxt = MIMEText(msg)
	mimeTxt['Subject'] = "ProjectX Post Created Successfully!"
	mimeTxt['From'] = sender
	mimeTxt['To'] = receiver

	s = smtplib.SMTP("email-smtp.us-west-2.amazonaws.com", 587)
	usr = "AKIAI7H3KEOG2XZNY45Q"
	pwd = "AkPQA6cVpVd6c6gAOeFhLAtHIAiMfuGzrqp89z8C3Ncl"
	s.starttls()
	s.ehlo()
	s.login(usr,pwd)
	s.sendmail(sender, receiver, mimeTxt.as_string())
	s.quit()

def WritePhotos(guid, photos):
	try:
		if photos is None or len(photos) < 1:
			raise ValueError("Invalid parameter value for 'photos'.")
		fileNameLen = 12
		path = os.path.join(imgPath, str(guid))
		diskImgs = utils.ReadFilesFromDirectory(path)
		webImgs = list()
		newImgsBase64 = list()

		for p in photos:
			if "/image_uploads" not in p['url'] and photos.index(p) != 0:
				newImgsBase64.append(p['base64'])
			elif "/image_uploads" in p['url']:
				idx = p['url'].index("filename=") + 9
				imgName = p['url'][idx:]
				webImgs.append(imgName)

		## Delete expired images ##
		imgsToDelete = set(diskImgs) - set(webImgs)
		for img in imgsToDelete:
			os.remove(os.path.join(path, img))

		## Handle the primary image separately ##
		primaryImg = photos[0]
		if "/image_uploads" in primaryImg['url']:
			idx = p['url'].index("filename=") + 9
			imgName = p['url'][idx:]
		else:
			if(os.path.isfile(os.path.join(path, "0.jpg"))):
				os.rename(os.path.join(path, mainFileName), \
					os.path.join(path, utils.RandomWord(fileNameLen) + ".jpg"))
			else:
				utils.WriteBase64FileToPath(path, "0.jpg", primaryImg['base64'])

		## Write the remaining new images ##
		for newImg in newImgsBase64:
			utils.WriteBase64FileToPath(path, utils.RandomWord(fileNameLen) + ".jpg", newImg)
	except IOError, e:
		print "IO Error - failed to create image files. %s" % e

if __name__ == "__main__":
	app.run(port=8080, debug=True)
	#app.run(host='0.0.0.0', debug=True) # public on network

