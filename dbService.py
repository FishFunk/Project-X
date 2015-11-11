import MySQLdb as mdb, sys
import sqlalchemy as alchemy
import formatter, datetime, ast, json
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("mysql+mysqldb://root:qwerty01@localhost/projectx", pool_recycle="3600")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class post(Base):
	__tablename__ = "post"
	id = Column(Integer, Sequence("post_id_seq"), primary_key=True)
	guid = Column(String(40))
	title = Column(String(100))
	desc = Column(String(500))
	email = Column(String(30))
	price = Column(Integer)
	zip = Column(Integer)
	phone = Column(String(20))
	date = Column(Date)
	flags = Column(Integer, default=0)

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
		@return - list<post>
		"""
		try:
			sesh = Session()
			q = sesh.query(post).filter(or_(post.title.like('%'+searchVal+'%'), 
				post.desc.like('%'+searchVal+'%')))
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
			q = sesh.query(post).filter(post.guid==guid)
			post = q.first()
			if post is None:
				raise Exception("POST GUID not found.")
			return self._singleRowToDict(post)
		except Exception, e:
			print "Error %s" % e

	def insertPost(self, newPost):
		"""
		Insert a post object into the database.
		"""
		date = datetime.date.today()
		try:
			p = post(
				guid=newPost['guid'], 
				title=newPost['title'], 
				desc=newPost['desc'],
				email=newPost['email'],
				price=newPost['price'],
				zip=newPost['zip'],
				phone=newPost['phone'],
				date=date)
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
			sesh.query(post).filter_by(guid=post['guid']).update({
				"title":post['title'], 
				"desc":post['desc'],
				"email":post['email'],
				"price":post['price'],
				"zip":post['zip'],
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
			sesh.query(post).filter(post.guid==guid).update({"flags":post.flags + 1})
			sesh.commit()
		except Exception, e:
			print "Error %s" % e
			raise e

	def deletePost(self, guid):
		try:
			sesh = Session()
			sesh.query(post).filter(post.guid==guid).delete()
			sesh.commit()
		except Exception, e:
			raise e

	def deleteExpiredPosts(self):
		"""
		"""
		try:
			now = datetime.date.today()
			sesh = Session()
			sesh.query(post).filter(post.date==now).delete()
			sesh.commit()
		except Exception, e:
			raise e

	def _singleRowToDict(self, row):
		d = row.__dict__
		d.pop('_sa_instance_state')
		d.pop('date')
		d.pop('flags')
		return d

	def _multiRowToDict(self, rows):
		"""
		Convert query results into dictionary objects
		"""
		dicts = list()
		for r in rows:
			d = r.__dict__
			d.pop('_sa_instance_state')
			d.pop('date')
			d.pop('flags')
			dicts.append(d)
		return dicts