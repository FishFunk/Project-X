"""
Models a user post object in the database. Accessible as a dictionary.
"""
class Post:
	def __init__(self, guid, title, desc, email, price, loc, phone):
		self.postDict = dict()
		self.postDict['guid'] = guid
		self.postDict['title'] = title
		self.postDict['description'] = desc
		self.postDict['email'] = email
		self.postDict['price'] = price
		self.postDict['location'] = loc
		self.postDict['phone'] = phone

	def getDict(self):
		return self.postDict