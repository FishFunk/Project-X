import MySQLdb as mdb, sys
import sqlalchemy as alchemy
import formatter, datetime, ast, json
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Post

Base = declarative_base()
engine = create_engine("mysql+mysqldb://root:qwerty01@localhost/projectx", pool_recycle="3600")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Post(Base):
	__tablename__ = "Post"
	id = Column(Integer, Sequence("post_id_seq"), primary_key=True)
	guid = Column(String(40))
	title = Column(String(100))
	description = Column(String(500))
	email = Column(String(30))
	price = Column(Integer)
	zip_code = Column(Integer)
	phone = Column(String(20))
	date_added = Column(Date)
	flag_count = Column(Integer, default=0)

class dbService(object):

	def __init__(self):
		try:
			self.con = mdb.connect('localhost', 'root', 'qwerty01', 'ProjectX')
			cur = self.con.cursor()
			cur.execute("SELECT VERSION()")
			ver = cur.fetchone()
			print "MySQL version: %s" % ver
			print "SqlAlchemy version: %s" % alchemy.__version__
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
			sesh = Session()
			q = sesh.query(Post).filter(or_(Post.title.like('%'+searchVal+'%'), 
				Post.description.like('%'+searchVal+'%')))
			posts = self._multiRowToDict(q.all())
			print "Found %s posts" % len(posts)
			return posts
		except Exception, e:
			print "Error %s" % e
			raise e

	def getPostByGuid(self, guid):
		"""
		"""
		try:
			sesh = Session()
			q = sesh.query(Post).filter(Post.guid==guid)
			post = q.first()
			if post is None:
				raise Exception("POST GUID not found.")
			return self._singleRowToDict(post)
		except Exception, e:
			print "Error %s" % e

	def insertPost(self, post):
		"""
		Insert a post object into the database.
		"""
		date = datetime.date.today()
		try:
			p = Post(
				guid=post['guid'], 
				title=post['title'], 
				description=post['description'],
				email=post['email'],
				price=post['price'],
				zip_code=post['zip_code'],
				phone=post['phone'],
				date_added=date)
			sesh = Session()
			sesh.add(p)
			sesh.commit()
		except Exception, e:
			print "Error %s" % e
			raise e

	def updatePost(self, post):
		"""
		Update existing post in the database.
		"""
		try:
			sesh = Session()
			sesh.query(Post).filter_by(guid=post['guid']).update({
				"title":post['title'], 
				"description":post['description'],
				"email":post['email'],
				"price":post['price'],
				"zip_code":post['zip_code'],
				"phone":post['phone']})
			sesh.commit()
		except Exception, e:
			print "Error %s" % e
			raise e

	def flagPost(self, guid):
		"""
		Flag a post by GUID
		"""
		try:
			sesh = Session()
			post = sesh.query(Post).filter(Post.guid==guid).first()
			sesh.query(Post).update({"flag_count":post.flag_count + 1})
			sesh.commit()
		except Exception, e:
			print "Error %d: %s" % e
			raise e

	def deletePost(self, guid):
		try:
			sesh = Session()
			sesh.query(Post).filter(Post.guid==guid).delete()
			sesh.commit()
		except Exception, e:
			raise e

	def deleteExpiredPosts(self):
		"""
		"""
		try:
			now = datetime.date.today()
			sesh = Session()
			sesh.query(Post).filter(Post.date_added==now).delete()
			sesh.commit()
		except Exception, e:
			raise e

	def _singleRowToDict(self, row):
		d = row.__dict__
		d.pop('_sa_instance_state')
		d.pop('date_added')
		d.pop('flag_count')
		return d

	def _multiRowToDict(self, rows):
		"""
		Convert query results into dictionary objects
		"""
		dicts = list()
		for r in rows:
			d = r.__dict__
			d.pop('_sa_instance_state')
			d.pop('date_added')
			d.pop('flag_count')
			dicts.append(d)
		return dicts