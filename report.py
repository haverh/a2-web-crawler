import re
from urllib.parse import urlparse
from collections import defaultdict
import sys
from os.path import exists
from urllib.request import urlopen
from sys import getsizeof
from bs4 import BeautifulSoup
'''
url = urlopen("https://www.ics.uci.edu/~rohit/Acknowledgments.htm")
soup = BeautifulSoup(url.read(), "html.parser")
print(soup.get_text())

sz	= getsizeof(url.read())
print("SIZE IS : " + str(sz))
'''


validLinks = open('validLinks.txt', 'r').readlines()
stopwords = open('stopwords.txt', 'r').readlines()

''' HELPER FUNCTIONS '''
def filterLine(ln):
	temp = ln.split()
	temp[1] = int(temp[1])
	return temp
			    
def getFirstElement(ln):
	return ln.split()[0]
						    
def printOut( freqDict, sortByVal=False ):
	# Time Complexity of sorting is O(nlogn)
	sortedTokens = sorted(freqDict.items())
		
	# Time Complexity of sorting in reverse is also O(nlogn)
	# Source: www.geeksforgeeks.org/ways-sort-list-dictionaries-values-python-using-lambda-function/
	if ( sortByVal is True ):
		sortedTokens = sorted(sortedTokens, key = lambda x: x[1], reverse=True)
		
	# Time Complexity is n
	# Iterates throuhg the sortedTokens and prints out
	for tup in sortedTokens:
		print( str(tup[0]) + " -> " + str(tup[1]))
	
def tokenize( textFile ):
	# Raise an error if the file/path doesn't exist
	if ( not exists( textFile ) ):
		raise FileExistsError(textFile + " does not exist")
	# Open and read file given in command line
	with open( textFile, "r" ) as file:
		tokenList = []
		# Initialize token to catch any broken/split words
		token = ""

		# Check if the file read is a pure text file ( utf-8 encoded )
		try:
			content = file.read(100)
			# This while loops checks the last token of the tokenList
			# and the first token to see if they are one word or
			# separate words
			while ( content ):
				# Split content up to tokens
				tempList = re.split("[^a-zA-Z0-9\']", content)

				#Check if words are broken up
				if ( token != "" and tempList[0] != "" ):
					joined = token + tempList[0]
					tokenList.append(joined.lower())
					tempList.pop(0)
				elif ( token != "" ):
					tokenList.append(token.lower())

				token = tempList[len(tempList)-1]
				tempList.pop(len(tempList)-1)

				for tok in tempList:
					if ( tok != "" ):
						tokenList.append(tok.lower())

				content = file.read(100)

			if ( token != "" ):
				tokenList.append(token.lower())

			return tokenList

		except UnicodeDecodeError:
			raise Exception("Unable to read the file. Please enter a pure text file")


''' Count Number of Unique Pages '''
def countPages(urlList):
	return len(urlList)


''' Get Longest Page '''
def longestPage(urlList):
	filteredLines = list(map(filterLine, urlList))
	return max(filteredLines, key=lambda x: x[1])


''' Get Subdomains '''
def trackSubdomain(urlList):
	filteredLines = list(map(getFirstElement, urlList))
	subdomainTracker = defaultdict(int)
	for item in filteredLines:
		if re.match(r"^.*[a-zA-Z0-9]+.ics.uci.edu", item):
			subdomainTracker[urlparse(item).netloc] += 1

	return subdomainTracker


''' Common Words '''
def commonWords(textFileName, stopwords):
	tokenList = tokenize(textFileName)
	wordCounter = defaultdict(int)
	for word in tokenList:
		if word+"\n" not in stopwords:
			wordCounter[word] += 1
	sortedWords = sorted(wordCounter.items())
	temp = sorted(sortedWords, key = lambda x: x[1], reverse=True)
	listOfCommonWords = map(lambda x:x[0], temp)
	return listOfCommonWords


print("# of Pages => " + str(countPages(validLinks)))
print("Longest Page => " + longestPage(validLinks)[0])
print("# of Subdomains => " + str(len(trackSubdomain(validLinks))))
printOut(trackSubdomain(validLinks))
print(list(commonWords('words.txt', stopwords))[0:50])

