import sys
import re
import urllib.request
from bs4 import BeautifulSoup
import time
import gc
   
# Variables
seed_url = ""
keyphrase = "" 
isSet = False
check_key = False
links_crawled = []
main_page_pattern = "/wiki/Main_Page"
discovered_urls = []
focussed_urls = []
more_urls = []
final_urls = []

# Check for keyphrase in Soup Object
def check_keyphrase(soup_obj, keyphrase):
	for item in soup_obj.find_all(text=re.compile('(?i)'+keyphrase)):
		return True
	return False

def isColonPresent(link):
	if(":" not in link):
		return True
	else: 
		return False

def wikiPattern(url): 
	wiki_pattern = "/wiki/"
	enwiki_pattern = "//en.wikipedia.org"
	new_pattern = enwiki_pattern + wiki_pattern
	if(url and wiki_pattern in url[0:6] or new_pattern in url[0:50]):
		return True
	else:
		return False

# Main Crawler Function to extract info and add URL if reqd.
def crawler_main(url, keyphrase, isSet):
	req_obj = urllib.request.Request(url)
	req_obj.add_unredirected_header('User-Agent','Mozilla/5.0')
	# Extract data if response code is success
	if(urllib.request.urlopen(req_obj).getcode() == 200):
		data = urllib.request.urlopen(req_obj)
	else:
		print("Error opening URL")
	discovered_urls.append(url)
	# Read the data and put it in a BeautifulSoup object
	content = data.read()
	soup_obj = BeautifulSoup(content)
	
	# Check for the keyphrase
	check_key = check_keyphrase(soup_obj, keyphrase)
	if((not isSet) or check_key):
		print(url)
		focussed_urls.append(url)
		for link in soup_obj.findAll('a'):
			link_href = link.get('href')
			link_to_string = str(link_href)
			if(link_to_string and link_to_string not in discovered_urls and main_page_pattern not in repr(link_to_string) and link_to_string[0:] != '#' and isColonPresent(link_to_string) and wikiPattern(link_to_string)):
				links_crawled.append(link_to_string)
		
	return list(set(links_crawled))	

def parse_url(str):
	parsed_url = str
	if(str.find("//www",0,7) >= 0):
		parsed_url = "http:"+str
	elif(str.find("/wiki",0,5) >= 0):
		parsed_url = "http://en.wikipedia.org"+str
	elif(str.find("http",0,5) == -1):
		parsed_url = "http:"+str
	return parsed_url	

# URL and Keyphrase as inputs
if (len(sys.argv)-1) == 2: 
	print("Seed Document URL: ", sys.argv[1])
	seed_url = sys.argv[1]
	print("Keyphrase: ", sys.argv[2])
	keyphrase = sys.argv[2]
	isSet = True

# URL as input
elif (len(sys.argv)-1) == 1: 
	print("Seed Document URL: ", sys.argv[1])
	seed_url = sys.argv[1]

#Initial Crawl
urls = crawler_main(seed_url, keyphrase, isSet)
crawled_links = 0
length = len(urls)
depth =2 
childs_at_certain_depth = length
temp=0
flag = 0
link = ""

while urls!=None and depth<=5 and len(focussed_urls)<1000:
	if flag == 0:
		flag=1
	if childs_at_certain_depth == 0:
		depth = depth + 1
		flag = 0
		childs_at_certain_depth = temp
		temp = 0
	link = urls[0]
	link = urls.pop(0)
	parsed_link = parse_url(link)
	if parsed_link not in discovered_urls and parsed_link not in focussed_urls:
		gc.disable()
		more_urls = crawler_main(parsed_link, keyphrase, isSet)
		gc.enable()
		urls = urls + more_urls
		temp += len(more_urls)
	childs_at_certain_depth = childs_at_certain_depth - 1