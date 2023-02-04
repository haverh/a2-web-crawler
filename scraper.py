import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pickle
from collections import defaultdict
from os.path import exists
from sys import getsizeof
import http.client
#from utils.download import download
#from utils.config import Config


def scraper(url, resp):
	# print("				--		Scraper		--");	
	links = extract_next_links(url, resp)
	return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content

	# List consisting of valid domains to crawl
	domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
	blacklist = ["wics.ics.uci.edu/events/"]
	crawledLinks = []

	# Extract links if the status is 200
	if  (resp.status == 200):

		# Limits the size of content for extraction
		sz = getsizeof(resp.raw_response.content)
		print("					SIZE OF " + url + " is " + str(sz))

		if (sz >= 10000 and sz < 1000000):
			soup = BeautifulSoup( resp.raw_response.content, "html.parser")

			'''
			if ( re.match("\w*date\w*=", url )):
				return list()
			'''
			
			# Get all URLs that are in the a valid domain
			for link in soup.find_all('a'):
				linkUrl = link.get('href')
				if ( linkUrl ):
					#print("OG LINK ==> " + linkUrl)
					# Defragment the URLs if they exists
					parsed = urlparse(linkUrl)
					if ( len(parsed.fragment) > 1 ):
						linkUrl = linkUrl.replace('#'+parsed.fragment, '')
					#print(" 	DEFRAGGED LINK ==> " + linkUrl)
					# Create and extract the absolute URL
					# given its relative URL
					#print("		LEN = " + str(len(linkUrl)) + " || LinkURL = " + linkUrl + " || Path = " + parsed.path)
					'''
					if ( len(linkUrl) > 0 and linkUrl == parsed.path ):
						#print("			linkUrl ==> " +  linkUrl)
						#print("			linkPATH ==> " + parsed.path ) 
						newUrl = ""
						if ( linkUrl[0] == "/" ):
							newUrl = url + linkUrl
						else:
							newUrl = url + "/" + linkUrl
						#print("		CAUGHT => " + newUrl)
						crawledLinks.append(newUrl)
					else:
						# Check if URL has a valid domain name
						for domain in domains:
							if ( domain in urlparse(linkUrl).netloc ):
								#print("EXTRACTING => " + linkUrl)
								crawledLinks.append(linkUrl)
					'''
					try:
						validLinks = pickle.load(open('validLinks.bin', 'rb'))
						isPath = re.match("(^[a-z0-9/]+).([a-z0-9/]+)$", linkUrl)
						if (isPath):
							if ( linkUrl[0] == "/" ):
								newUrl = urlparse(url).netloc + linkUrl
							else:
								newUrl = urlparse(url).netloc + "/" + linkUrl
							if ( newUrl not in validLinks ):
								crawledLinks.append(newUrl)
						else:
							for domain in domains:
								if domain in urlparse(linkUrl).netloc:
									if ( linkUrl not in validLinks ):
										crawledLinks.append(linkUrl)
					except:
						pass

			
			# Create a pickle file with the seed URL
			# if the file doesn't exists
			if ( not exists('validLinks.bin') ):
				vLinks = open( 'validLinks.bin', 'wb' )
				validLinks = {resp.url}
				pickle.dump(validLinks, vLinks)
				vLinks.close()
			else:
				# Add the current URL to the pickle file
				# if file exists
				vLinks = open('validLinks.bin', 'rb')
				validLinks = pickle.load(vLinks)
				validLinks.add(resp.url)
				vLinks.close()

				vLinks = open('validLinks.bin', 'wb')
				pickle.dump(validLinks, vLinks)
				vLinks.close()
			

			#print(crawledLinks)	
			# Return the list of URLs
			return crawledLinks

		# Return an empty list if size is out of bounds
		return list()
	else:
		# Return an empty list if status is not valid
		print("ERROR STATUS: " + str(resp.status))
		print("RESP -> " + str(resp.raw_response))
		print("			" + str(resp.error))
		return list()


def checkExtension(path):
	'''
	print("			--> " + path);
	if ("pdf" in path):
		print("		__ " + path);
	if (not re.match(r"pdf", path.lower())):
		print("			FOUND  " + path.lower());
	'''
	return re.match(r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", path.lower())


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
	try:
		#print("	URL ==> " + url + " <==")
		#print("				CHECKING FOR VALIDITY\n URL = " + url)
		pathCount = defaultdict(int)

		parsed = urlparse(url)
	
		# Not valid (Returns False) if the url is not
		# the correct scheme
		if parsed.scheme not in set(["http", "https"]):
			return False

		# Not valid (Returns False) if the url is of the
		# following types of files
		"""
		print("		PATH ====> " +parsed.path + "	" +  str(re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())));
		"""
		"""
		if ( re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())):
			#print("				" + url  + "		" + parsed.path);
			#print("						============caught=================");
			#print("						" + 
			return False
		
		if ( re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.query.lower())):
			return False
		"""
	#	if (url == "https://computableplant.ics.uci.edu/papers/2004/graphNotationsTR.pdf"):
	#		print("			" + parsed.path + "			" +parsed.query);

		# Not valid (Returns False) if the url is a share link
		if ( re.match(r"share=", parsed.query.lower())):
			return False

		# Parses the url to a list of paths
		pToken = parsed.path.split('/')
		
		# Not valid (Returns False) if the url has
		# infinitely repeating paths
		for word in pToken:
			if ( len(word) > 0 ):
				pathCount[word] += 1
				if ( pathCount[word] > 1 ):
					return False

		# 
		for link in pToken:
			if ".php" in link and pToken[-1] != link:
				return False
		'''
		# CONTENT SIMILARITY
		content = open( 'content.bin', 'rb' )
		contentSet = pickle.load(content)

		if ( c not in validLinks ):
			validLinks.add(url)
			vLinks.close()
			vLinks = open( 'validLinks.bin', 'wb' )
			pickle.dump(validLinks, vLinks)
			vLinks.close()
			return True
		else:
			return False
		'''

		if (checkExtension(parsed.path.lower()) or checkExtension(parsed.query.lower())):
			return False

		if "pdf" in url:
			return False

		try:
			# Check if the url has been crawled
			# 	Add to pickled file if not
			#	Not a valid url (Returns False) if yes
		
			vLinks = open( 'validLinks.bin', 'rb' )
			validLinks = pickle.load(vLinks)
			#print("url is : " + url)

			httpconnection = http.client.HTTPConnection(parsed.hostname, parsed.port)
			httpconnection.request("GET", parsed.path)
			response = httpconnection.getresponse()
		
			#response = download(url, Config)
			#if ( url in validLinks ):
			#	return False
		
			if ( url not in validLinks):
				#	print("			THIS IS THE URL ID------> " + url + "		" + parsed.path + "		" + parsed.query);
				#print("			url id		" + parsed.path + " - " +parsed.query + " -");
				validLinks.add(url)
				vLinks.close()
				vLinks = open( 'validLinks.bin', 'wb' )
				pickle.dump(validLinks, vLinks)
				vLinks.close()
				print("VALID COUNTER ==> " + str(len(validLinks)))
			else:
				#print("ALREADY CRAWLED: " + url)
				return False
		except:
			return False
		
		
		calendar = open('calendar.txt', 'a+')
		if ("wics.ics.uci.edu/events/" in url):
			return False
			calendar.write(url + "\n")

		
		dateQuery = open("date.txt", "a+")
		if (re.match("\w*date\w*=", url)):
			dateQuery.write(url + "\n")

	#	print("CRAWLING: " + url)
		#return True
		"""
		return not re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())
		"""
		'''
		if (checkExtension(parsed.path) and checkExtension(parsed.query)):
			if "pdf" in url:
				r
				print("			---> 		" + url);
				print("			--->		" + parsed.path);
				print("			--->		" + parsed.query + "	" + str(len(parsed.query)));
		return checkExtension(parsed.path) and checkExtension(parsed.query);
		'''

		return True

	except TypeError:
		print ("TypeError for ", parsed)
		raise
