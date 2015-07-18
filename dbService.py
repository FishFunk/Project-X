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
				posts.append(post)

			print "Found %s posts" % len(posts)
			return posts
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
			cur.execute(sql, (post['guid'], post['title'], post['description'], post['email'], post['price'], 
				post['location'], post['phone'], date))
			self.con.commit()
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0], e.args[1])
		finally:
			cur.close()
			return ""
