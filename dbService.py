import MySQLdb as mdb, sys
from models import Post
import formatter, datetime, ast, json

class dbService(object):

	def __init__(self):
		try:
			self.con = mdb.connect('localhost', 'root', 'qwerty01', 'ProjectX')
			cur = self.con.cursor()
			cur.execute("SELECT VERSION()")
			ver = cur.fetchone()
			print "MySQL version: %s" % ver
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit(1)

	def searchPostTable(self, searchVal):
		"""
		Query the database and return results with text matching 'searchVal' in the Title and/or the Body columns.
		@param - str
		@return - list<Post>
		"""
		try:
			cur = self.con.cursor()
			sql = """SELECT * FROM POST WHERE MATCH (TITLE, DESCRIPTION) \
			AGAINST (%s IN NATURAL LANGUAGE MODE)"""
			cur.execute(sql, (searchVal,))
			rows = cur.fetchall()

			posts = list()
			for row in rows:
				post = Post(row[1],row[2],row[3],row[4],row[5],row[6],row[7]).getDict()
				post['Photos'] = self.getPhotos(post['Guid'])
				posts.append(post)

			print "Found %s posts" % len(posts)
			return posts
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		finally:
			cur.close()

	def getPhotos(self, guid):
		"""
		Query the database and return results that match the guid.
		@param - str
		@return - list<string>
		"""
		try:
			cur = self.con.cursor()
			sql = """SELECT * FROM PHOTO_URL WHERE GUID = %s"""
			cur.execute(sql, (guid,))
			rows = cur.fetchall()

			photoUrls = list()
			for row in rows:
				photoUrls.append(row[2])

			print "Found %s photos" % len(photoUrls)
			return photoUrls
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		finally:
			cur.close()

	def insertPost(self, post):
		"""
		Insert a post object into the database.
		"""
		post = post.postDict
		date = datetime.date.today()
		try:
			cur = self.con.cursor()
			sql = """INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
			VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"""
			cur.execute(sql, (post['Guid'], post['Title'], post['Description'], post['Email'], post['Price'], 
				post['Location'], post['Phone'], date))
			self.con.commit()
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		finally:
			cur.close()
			return ""

	def insertPhotos(self, guid, photos):
		"""
		Insert photos as urls into the table

		guid - Unique ID matching to the post that the photos belong to
		photoUrls - Array of string urls
		"""
		try:
			cur = self.con.cursor()
			sql = """INSERT INTO PHOTO_URL (GUID, URL) VALUES(%s, %s)"""
			for photo in photos:
				url = photo.get('url')
				print len(url)
				cur.execute(sql, (guid, url))
			self.con.commit()
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		finally:
			cur.close()
			return ""
