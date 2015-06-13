"""
Models a user post object in the database. Accessible as a dictionary.
"""
class Post:
	def __init__(self, guid, title, desc, email, price, loc, phone):
		self.postDict = dict()
		self.postDict['Guid'] = guid
		self.postDict['Title'] = title
		self.postDict['Description'] = desc
		self.postDict['Email'] = email
		self.postDict['Price'] = price
		self.postDict['Location'] = loc
		self.postDict['Phone'] = phone

	def getDict(self):
		return self.postDict