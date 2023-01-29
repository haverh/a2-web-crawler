import re
from collections import defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from os.path import exists
import pickle
# Modify this function
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
	# ===========================================================================================
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
	# resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
	# ===========================================================================================
	# Domains to access
	Domain = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"];
	# File containing all visited webpages!
	file = "visited.p";
	
	# List of all hyperlinks found on the current webpage and to return
	URLs = list();
	if resp.status == 200:
		soup = BeautifulSoup(resp.raw_response.content, "html.parser");
		for link in soup.find_all('a'):
			hyperlink = link.get('href');
			
			# Check the webpage contain a hyperlink or in other words
			# Check if the above hyperlink does not return a nonetype
			# to prevent errors
			
			if hyperlink:
				
				# Add the domain iff the hyperlink starts with a slash
				# e.g. /about --> https://www.ics.uci.edu/about
				if re.match(r"/[a-zA-Z0-9]+", hyperlink):
					for domain in Domain:
						if  domain in hyperlink:
							URLs.append(domain + hyperlink);
							break;
				else:
					# Check if the link is within the domain
					# Possible move to is_valid method
					for domain in Domain:
						if domain in hyperlink:
							URLs.append(hyperlink);

		# Save the current URL  to the pickle file
		# to prevent crawlling the same URL multiple times
		# Append mode
		pickle.dump(resp.raw_response.url, open(file, "ab"));
		# Return the list of hyperlinks found on the current webpage
		return URLs;
	else:
		print("Error Status: ", resp.error);
	return URLs;
	

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
	try:
		parsed = urlparse(url)
		counterDict = defaultdict(int);
		# Pickle File
		file = "visited.p"
		if parsed.scheme not in set(["http", "https"]):
			return False

		token = parsed.query.split('/');
		#### list of string after domain
		#print(parsed.path, "		this is the parsed");
		#print(token, "		this is the tokenn");
		#if len(token) > 1:
	#		return False;



		# Check if the url is repeating the same path
		# e.g. /about/about/about/ ...
		
		token = parsed.path.split('/');	
		
		for word in token:
			# Ignores white spaces
			if len(word) > 0:
				counterDict[word] += 1;
				if (counterDict[word] > 1):
					print(token , " REMOVED ", word, " ", url);
					return False;
		
		# Do not know what this is doing
		for link in token:
			if ".php" in link and token[-1] != link:
				return False;
		
		# Check if the url exist to prevent crawlling it multiple times
		URLs = pickle.load(open("visited.p", "rb"));
		#print(setOfURL);
		
		visited = set();
		for visitedURL in URLs:
			# Whenever the url is a webpage we traveled already
			# Return False;
			if visitedURL != url and url in visited:
				return False;
			else:
				visited.add(visitedURL);
		
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
