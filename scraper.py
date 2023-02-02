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

	domains = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"]
	crawledLinks = []
	# print("NETLOC : " + urlparse(url).netloc)

	if  (resp.status == 200):

		sz = getsizeof(resp.raw_response.content)

		if (sz >= 10000 and sz < 1000000):
			#print("STATUS : " + str(resp.status))
			soup = BeautifulSoup( resp.raw_response.content, "html.parser")


			# Get all urls that are in the a valid domain
			for link in soup.find_all('a'):
				linkUrl = link.get('href')

				if ( linkUrl ):
					parsed = urlparse(linkUrl)
					
					if ( len(parsed.fragment) > 1 ):
						#print("OLD: " + linkUrl)
						#print("FRAGMENT === " + "#" + parsed.fragment)
						linkUrl = linkUrl.replace('#'+parsed.fragment, '')
						#print("NEW: " + linkUrl)

					# Create url with a page path
					isPath = re.match("^\/\w+", linkUrl)
					if ( isPath ):
						newUrl = urlparse(url).netloc + linkUrl
						# print("ADDED -> " + str(newUrl))
						crawledLinks.append(newUrl)
		
					else:
						# Check if domain name is valid
						for domain in domains:
							if ( domain in urlparse(linkUrl).netloc ):
								# print("ADDED -> " + str(linkUrl))
								crawledLinks.append(linkUrl)
		
			if ( not exists('validLinks.bin') ):
				vLinks = open( 'validLinks.bin', 'wb' )
				validLinks = {resp.url}

				pickle.dump(validLinks, vLinks)
				vLinks.close()
			else:
				vLinks = open('validLinks.bin', 'rb')
				validLinks = pickle.load(vLinks)
				validLinks.add(resp.url)
				vLinks.close()

				vLinks = open('validLinks.bin', 'wb')
				pickle.dump(validLinks, vLinks)
				vLinks.close
	
			return crawledLinks
		return list()



	else:
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
		
		if parsed.scheme not in set(["http", "https"]):
			return False

		if ( re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())):
			return False;


		pToken = parsed.path.split('/')
		
		for word in pToken:
			if ( len(word) > 0 ):
				pathCount[word] += 1
				if ( pathCount[word] > 1 ):
					return False;

		for link in pToken:
			if ".php" in link and pToken[-1] != link:
				return False;	
		
		# Check Visited
		vLinks = open( 'validLinks.bin', 'rb' )
		validLinks = pickle.load(vLinks)
		#print( validLinks )
		if ( url not in validLinks ):
			# print("\nCRAWL COMMENCING -> " + str(url) + "\n")
			validLinks.add(url)
			vLinks.close()
			vLinks = open( 'validLinks.bin', 'wb' )
			pickle.dump(validLinks, vLinks)
			vLinks.close()
			return True
		else:
			# print("+_+_+_+_+_+_+ ALREADY CRAWLED -> " + str(url) )
			return False
		
		return not re.match(
			r".*\.(css|js|bmp|gif|jpe?g|ico"
			+ r"|png|tiff?|mid|mp2|mp3|mp4"
			+ r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
			+ r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
			+ r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
			+ r"|epub|dll|cnf|tgz|sha1"
			+ r"|thmx|mso|arff|rtf|jar|csv"
			+ r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())


	except TypeError:
		print ("TypeError for ", parsed)
		raise
