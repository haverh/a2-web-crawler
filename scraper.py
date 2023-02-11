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

# Helper function
# To get url from crawledLinks.txt
def splitLine(ln):
	return ln.split()[0]

# Helper function
# Determines if url has good information
def is_good_info( wordAmount ):
	textLength = len(wordAmount)
	return (textLength >= 100 and textLength < 2500)

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
	domains = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]
	extractedLinks = []

	# Extract links if the status is 200
	if  (resp.status == 200):

		# Initializing 'crawled.txt'
		if not exists('crawledLinks.txt'):
			crawledLinks = open('crawledLinks.txt', 'w')
			crawledLinks.close()
		
		# Store Content in a variable
		content = resp.raw_response.content

		# Check if content is NoneType( Empty )
		# 	If NoneType => BeautifulSoup Throws an Exception
		try :

			soup = BeautifulSoup( content, "html.parser")
			text = soup.get_text()
			wordAmount = text.split()

			# Check if website has good info
			if is_good_info(wordAmount):
			
				words = open("words.txt", "a")
				words.write(text)
			
				# Get all URLs that are in the a valid domain
				for link in soup.find_all('a'):
					linkUrl = link.get('href')
					if ( linkUrl ):
						parsed = urlparse(linkUrl)
						# Defragment the URLs if they exists
						if ( len(parsed.fragment) > 1 ):
							linkUrl = linkUrl.replace('#'+parsed.fragment, '')
						
						# Handle any unexpected errors that might be thrown
						# due to opening the file
						try:
							crawledLinks = open('crawledLinks.txt', 'r').readlines()
							
							# Check if linkUrl is a relative path
							isPath = re.match("(^[a-zA-Z0-9/]+).([a-zA-Z0-9/]+)$", linkUrl)
							if (isPath):
								if ( linkUrl[0] == "/" ):
									newUrl = parsed.scheme + "://" + parsed.netloc + linkUrl
								else:
									newUrl = parsed.scheme + "://" + parsed.netloc + "/" + linkUrl

								# Check if the newUrl is not in crawledLinks.txt
								# To prevent re-crawling a link twice.
								if ( newUrl not in list(map(splitLine, crawledLinks)) ):
									extractedLinks.append(newUrl)
							# Absolute Path
							else:
								for domain in domains:
									if domain in urlparse(linkUrl).netloc:
										# Check if the linkUrl is not in the crawledLinks.txt
										# To prevent re-crawling a link twice.
										if ( linkUrl not in list(map(splitLine, crawledLinks)) ):
											extractedLinks.append(linkUrl)

							crawledLinks.close()

						except:
							# REMOVE LATER 
							exceptionLinks = open('exception.txt', 'a+');
							exceptionLinks.seek(0);
							exceptionLinks.write(resp.url + "\n");
							pass

				# Insert current URL to file if all
				# links are extracted from current URL
				crawledLinks = open('crawledLinks.txt', 'a+')
				crawledLinks.seek(0)
				crawledLinks.write(resp.url + " " + str(len(wordAmount)) + "\n")
				crawledLinks.close()

				# Return all extracted links
				return extractedLinks

			# Doesn't have good information
			else:
				errLinks = open('errLinks.txt', 'a+')
				errLinks.seek(0)
				if resp.url + "\n" not in errLinks.readlines():
					errLinks.write(resp.url + "\n")
				errLinks.close()
				
				# Return empty list( No links found )
				# Because URL isn't crawled
				#	Low Information || Too Large
				return list()
		
		# Empty Content
		except:
			errLinks = open('errLinks.txt', 'a+')
			errLinks.seek(0)
			if resp.url + "\n" not in errLinks.readlines():
				errLinks.write(resp.url + "\n")
			errLinks.close()

			return list()
	
	# Return an empty list if status is not valid
	else:
		errLinks = open('errLinks.txt', 'a+')
		errLinks.seek(0)
		if resp.url+"\n"  not in errLinks.readlines():
			errLinks.write(resp.url+"\n")
		errLinks.close()
		return list()


def checkExtension(path):
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
		pathCount = defaultdict(int)

		parsed = urlparse(url)
	
		# Not valid (Returns False) if the url is not
		# the correct scheme
		if parsed.scheme not in set(["http", "https"]):
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

		# Check if extensions are valid to crawl
		if (checkExtension(parsed.path.lower()) or checkExtension(parsed.query.lower())):
			return False

		# Check if its a pdf file
		if "pdf" in url:
			return False
		
		# Check if the url has been crawled
		# 	Add to txt file if not
		#	Not a valid url (Returns False) if yes
		crawledLinks = open('crawledLinks.txt', 'r')
		if url in list(map(splitLine, crawledLinks.readlines())):
			crawledLinks.close()
			return False
		
		# Blacklisting all trap websites
		# 	Calendar Trap
		if ("event" in url or re.match("\w*date\w*=", url)):
			return False

		# Write all valid links to txt file
		allLinks = open('allLinks.txt','a+')
		allLinks.seek(0)
		urlList = allLinks.readlines()
		if ( url.strip("/")+"\n" not in urlList ):
			allLinks.write(url.strip("/") + "\n")
		allLinks.close()

		# Return true when its a valid link
		return True

	except TypeError:
		print ("TypeError for ", parsed)
		raise
