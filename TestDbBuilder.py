""" 
TestDbBuilder.py
"""

import MySQLdb as mdb, sys
import uuid, os, shutil

class BuildTestDb(object):

	imgPath = "/Users/Daniel/bin/AppData/ProjectX/Images"
	placeholderImg = "/Users/Daniel/Desktop/Project X/static/resources/img/placeholder.jpeg"

	def __init__(self, host, user, passwd, dbName):
		self.host = host
		self.user = user
		self.passwd = passwd
		self.dbName = dbName
		try:
			con = mdb.connect(host, user, passwd)
			cur = con.cursor()
			sql = "CREATE DATABASE %s;" % dbName
			cur.execute(sql)
			con.close()
		except mdb.Error, ex:
			print "Error %d: %s" % (ex.args[0], ex.args[1])

	def createTable(self):
		try:
			con = mdb.connect(self.host, self.user, self.passwd, self.dbName)
			cur = con.cursor()

			cur.execute("""CREATE TABLE POST \
				(POST_ID int(11) unsigned NOT NULL AUTO_INCREMENT,\
					GUID varchar(100) NOT NULL, \
					TITLE varchar(100) NOT NULL DEFAULT '',\
					DESCRIPTION varchar(1000) NOT NULL DEFAULT '',\
					EMAIL varchar(100) NOT NULL DEFAULT '',\
					PRICE int(11) NOT NULL,\
					LOCATION int(11) NOT NULL,\
					DATE_ADDED date NOT NULL,\
					PHONE int(11) DEFAULT NULL,\
					PRIMARY KEY (POST_ID),\
					FULLTEXT KEY TITLE (TITLE, DESCRIPTION))\
					ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;""")

			cur.execute("""CREATE TABLE PHOTO_URL\
				ID int(11) unsigned NOT NULL AUTO_INCREMENT,\
				GUID varchar(100) NOT NULL,\
				URL mediumblob
				PRIMARY KEY (ID),\
				ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;""")
			
			con.close()
		except mdb.Error, ex:
			print "Error %d: %s" % (ex.args[0], ex.args[1])

	def addData(self):
		self.createPost('lawn chair', 'so comfortable!', 'daniel@email.com', 40, 22203, '\N', '2015-03-12')
		self.createPost('Macbook Pro', 'This thing is a beast. 250 gigs.', 'grant@email.com', 200, 22003, '\N', '2015-03-12')
		self.createPost('Sofa', 'Confortable! Like new!', 'abc@email.com', 1000, 22003, '\N', '2015-05-12')
		self.createPost('50" TV', 'Samsung. Crystal clear image.', 'bs@email.com', 1200, 22003, '\N', '2015-04-12')
		self.createPost('20" HD TV', 'Nice little tv.', 'aa@email.com', 100, 22203, '\N', '2015-03-12')
		self.createPost('43 inch HDTV', 'Moving, will take best offer.', 'bb@email.com', 500, 22314, '\N', '2015-03-19')
		self.createPost('Dining Table', 'This thing is an antique. Great condition', 'thatguy@email.com', 600, 23143, '\N', '2015-03-22')
		self.createPost('Lamp', 'Cheap IKEA lamp.', 'ikea@email.com', 10, 22314, '\N', '2015-03-12')
		self.createPost('Macbook Pro 2009', 'Old but still works! 150 gigs.', 'mac@email.com', 300, 22003, '\N', '2015-03-12')
		self.createPost('Macbook Pro 2011', '15" screen. Scratch on the casing but work perfect.', 'hikerdude@email.com', 500, 22314, '\N', '2015-03-12')
		

	def createPost(self, title, desc, email, price, loc, phone, date):
		con = mdb.connect(self.host, self.user, self.passwd, self.dbName)
		cur = con.cursor()
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', '%s', '%s', '%s', %s, %s, %s, '%s')" % (guid, title, desc, email, price, loc, phone, date)
		cur.execute(sql)
		fileDir = os.path.join(self.imgPath, str(guid))
		if not os.path.exists(fileDir):
			os.makedirs(fileDir)
		shutil.copyfile(self.placeholderImg, os.path.join(fileDir, 'testPhoto.jpg'))
		con.commit()
		cur.close()

if __name__ == "__main__":
	builder = BuildTestDb("localhost", "root", "qwerty01", "ProjectX")
	builder.createTable()
	builder.addData()
