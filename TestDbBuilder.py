""" 
TestDbBuilder.py
"""

import MySQLdb as mdb, sys
import uuid

class BuildTestDb(object):

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
		con = mdb.connect(self.host, self.user, self.passwd, self.dbName)
		cur = con.cursor()
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', 'lawn chair', 'so comfortable!', 'daniel@email.com', 40, 22203, \N, '2015-03-12')" % guid
		cur.execute(sql)
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', 'Macbook Pro', 'This thing is a beast. 250 gigs.', 'grant@email.com', 200, 22003, \N, '2015-03-12')" % guid
		cur.execute(sql)
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', 'Need a roommate', 'Renovated 1 bed and private bath.', 'rent@email.com', 1500, 22903, '7031129302', '2015-03-12')" % guid
		cur.execute(sql)
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', 'Desk', 'Made in the 80s. Oak wood. Has a scratch on the side.', 'chris@email.com', 150, 91003, '5713548233', '2015-03-12')" % guid
		cur.execute(sql)
		guid = uuid.uuid4()
		sql = "INSERT INTO POST (GUID, TITLE, DESCRIPTION, EMAIL, PRICE, LOCATION, PHONE, DATE_ADDED)\
		VALUES('%s', 'Drum kit', 'Basic set for beginners. Throne included.', 'drums@email.com', 500, 23205, \N, '2015-03-12')" % guid
		cur.execute(sql)
		con.commit()
		con.close()

if __name__ == "__main__":
	builder = BuildTestDb("localhost", "root", "qwerty01", "ProjectX")
	builder.createTable()
	builder.addData()
