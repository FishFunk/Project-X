""" 
utils.py
"""
import os

def WriteBase64FileToPath(fileDir, fileName, base64):
	try:
		data = base64.decode("base64");
		filePath = os.path.join(fileDir, fileName)

		if not os.path.exists(fileDir):
			os.makedirs(fileDir)
		with open(filePath, "wb") as FILE:
			FILE.write(data)
			FILE.close()
			print "Wrote file %s!" % filePath
	except IOError, e:
		print "Failed to create file. %s" % e.args[1]

def ReadFilesFromDirectory(directory):
	try:
		return os.listdir(directory)
	except OSError, e:
		print "Failed to read files from %s. %s." % (directory, e.args[1])
		return []