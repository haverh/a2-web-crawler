import re
from collections import defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
#from nltk.tokenize import word_tokenize
import pickle
def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
	Domain = [".ics.uci.edu", ".cs.uci.edu", ".informatics.uci.edu", ".stat.uci.edu"];
	setOfURL = set();
	# Traps:
	# Calendar, going in a circle
	if resp.status == 200:
		soup = BeautifulSoup(resp.raw_response.content, "html.parser");
		for link in soup.find_all('a'):
			linkURL = link.get('href');
#			parsed = urlparse(url);
#			token = word_tokenize(parsed.path);
#			print(token, "	this is token");


#			print(linkURL, 		"this is url");
			if linkURL is not None:
				if re.match(r"/[a-zA-Z0-9]+", linkURL):
#					print(resp.url, "		This is the url of the page");
					setOfURL.add(resp.url + linkURL);
				else:
					for domain in Domain:
						if domain in linkURL:
#							print(linkURL, "    is in domain");
							setOfURL.add(linkURL);
	if resp.status != 200:
		print("Error Status: ", resp.error);

	pickle.dump(setOfURL, open("visited.p", "ab+"));	
	return list(setOfURL);
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    #return list()

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
	try:
		parsed = urlparse(url)
		counterDict = defaultdict(int);
		if parsed.scheme not in set(["http", "https"]):
			return False

		token = parsed.query.split('/');
		#### list of string after domain
		#print(parsed.path, "		this is the parsed");
		#print(token, "		this is the tokenn");
		if len(token) > 1:
			return False;
		token = parsed.path.split('/');	
		for word in token:
			counterDict[word] += 1;
			if (counterDict[word] > 1):
				return False;
		setOfURL = pickle.load(open("visited.p", "rb"));
		print(setOfURL);
		if url in setOfURL:
			return False;
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
