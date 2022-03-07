import os
BASE_URL = "https://quotes.toscrape.com/"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\storefuck"

# Getting document from url
from collections import deque
import requests
def get_doc(url):
    try:
        doc = requests.get(url)
        if doc.status_code == 200:
            return doc.text
        else:
            return None
    except Exception as e:
        print(e)
        return None

#join file path
def join_file_path(path, url):
    relavitve_filename = url[len(BASE_URL):]
    if relavitve_filename:
        #relavitve_filename = relavitve_filename[:-1]
        relavitve_filename += "index.html"
    else:
        relavitve_filename = "index.html"
    return os.path.join(path, relavitve_filename)


#Get all links from response text
from bs4 import BeautifulSoup
def get_links(url):
    if url[-1] != "/":
        url += "/"
    doc = get_doc(url)
    filename = join_file_path(BASE_DIR, url)
    #create file and directory if not exist
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    else:
        print("Exist: {}".format(filename))
    #create file
    if doc:
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(doc)
            print("Writed to file: {}".format(filename))


    if doc:
        soup = BeautifulSoup(doc, "html.parser")
        links = []
        for link in soup.find_all("a"):
            links.append(link.get("href"))
        return links
    else:
        return None
    


#relatively url to absolute url
def get_absolute_url(url, relative_url):
    if relative_url.startswith("http"):
        return 
    if relative_url.startswith("/"):
        return url.split("/")[0]+"//"+url.split("/")[2]+relative_url
    if relative_url.startswith(".."):
        return url.split("/")[0]+"//"+url.split("/")[2]+"/"+relative_url.replace("..", "")
    return url+"/"+relative_url


#recursively request all links
from queue import Queue
from threading import Thread
#store history url in a set
history = set()
url_and_tag = {}
def get_all_links(url,num_tag_list):
    if len(num_tag_list) >3:
        return
    history.add(url)
    print("History Stored ", url)
    print("Tag ", num_tag_list)
    url_and_tag[url] = num_tag_list
    links = get_links(url)
    if links:
        for link_index in range(len(links)):
            link = links[link_index]
            new_link = get_absolute_url(url, link)
            temp_num = num_tag_list[:]
            temp_num.append(link_index)
            if new_link and new_link not in history:
                get_all_links(new_link,temp_num)
#get all values from history set
all_values = list(history)

get_all_links(BASE_URL,[0])