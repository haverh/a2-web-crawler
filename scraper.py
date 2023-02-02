import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pickle
from collections import defaultdict
from os.path import exists
from sys import getsizeof

def scraper(url, resp):
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
	crawledLinks = []

	# Extract links if the status is 200
	if  (resp.status == 200):

		# Limits the size of content for extraction
		sz = getsizeof(resp.raw_response.content)
		if (sz >= 10000 and sz < 1000000):
			soup = BeautifulSoup( resp.raw_response.content, "html.parser")

			# Get all URLs that are in the a valid domain
			for link in soup.find_all('a'):
				linkUrl = link.get('href')

				if ( linkUrl ):

					# Defragment the URLs if they exists
					parsed = urlparse(linkUrl)
					if ( len(parsed.fragment) > 1 ):
						linkUrl = linkUrl.replace('#'+parsed.fragment, '')

					# Create and extract the absolute URL
					# given its relative URL
					isPath = re.match("^\/\w+", linkUrl)
					if ( isPath ):
						newUrl = urlparse(url).netloc + linkUrl
						crawledLinks.append(newUrl)
		
					else:
						# Check if URL has a valid domain name
						for domain in domains:
							if ( domain in urlparse(linkUrl).netloc ):
								crawledLinks.append(linkUrl)
		
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
				vLinks.close
			
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

	
def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
	try:

		pathCount = defaultdict(int)

		parsed = urlparse(url)
	
		# Not valid (Returns False) if the url is not
		# the correct scheme
		if parsed.scheme not in set(["http", "https"]):
			return False

		# Not valid (Returns False) if the url is of the
		# following types of files
		if ( re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())):
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
		
		# Check if the url has been crawled
		# 	Add to pickled file if not
		#	Not a valid url (Returns False) if yes
		vLinks = open( 'validLinks.bin', 'rb' )
		validLinks = pickle.load(vLinks)

		if ( url not in validLinks ):
			validLinks.add(url)
			vLinks.close()
			vLinks = open( 'validLinks.bin', 'wb' )
			pickle.dump(validLinks, vLinks)
			vLinks.close()
			return True
		else:
			return False
		

	except TypeError:
		print ("TypeError for ", parsed)
		raise
