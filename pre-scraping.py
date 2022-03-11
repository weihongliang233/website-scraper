import coloredlogs, logging
from typing import Union
# Create a logger object.
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import os
import urllib
import json
import base64
#BASE_URL和BASE_DIR末尾一定是斜杠
BASE_URL = "https://git-scm.com/"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\storeScrapy_Documentation\\"
PRE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\pre\\"
html_history = set()
static_history = set()
url_and_tag = []
# Getting document from url
import requests

def get_content(url):
    print("Getting content from" + url)
    #url = add_slash(url)
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            #bytes can be decode to text or binary
            return response.content
        else:
            print("Failed")
            print(url)
            print(response.status_code)
            return None
    except Exception as e:
        print(e)
        return None

join_url_current_relative = urllib.parse.urljoin
#join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","/sdfds")
#join_url_current_relative(BASE_URL+"intro/overview/","../_static/img/logo.png")
#join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","install.html")
join_url_current_relative("https://docs.readthedocs.io/en/stable/index.html","../_static/pygments.css")

def hash_file_path(url:str)->str:
    return  os.path.join(PRE_DIR , str(hash(url)) + '.json')
def write_obj_to_json(obj, filename):
    if filename=="":
        return
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(obj, f)
        print("Writed to file: {}".format(filename))
def extract_html_links(doc):
    soup = BeautifulSoup(doc, "html.parser")
    links = []
    for link in soup.find_all("a"):
        links.append(link.get("href"))
    return links

def extract_css_links(doc):
    soup = BeautifulSoup(doc, "html.parser")
    links = []
    for link in soup.find_all("link"):
            links.append(link.get("href"))
    return links

def extract_js_links(doc):
    soup = BeautifulSoup(doc, "html.parser")
    links = []
    for link in soup.find_all("script"):
        links.append(link.get("src"))
    return links

def extract_image_links(doc):
    soup = BeautifulSoup(doc, "html.parser")
    links = []
    for link in soup.find_all("img"):
        links.append(link.get("src"))
    return links

def extract_static_links(doc):
    return  extract_image_links(doc) + extract_css_links(doc) 
def filter_links(links: list[str]):
    #if link is not anchor, not start with http, not start with irc`, no "?"
    return [link for link in links if link and not "#" in link and  not link.startswith("http") and not link.startswith("irc") and not "?" in link]


binary_file_extension = ['.png','.jpg','.jpeg','.gif','.svg','.ico','.ttf','.woff','.woff2','.eot']
def process_link(url,html_doc):
    print("Processing link: {}"+url)
    #url = add_slash(url)

    html_history.add(url)
    if html_doc:
        obj = {
            "url": url,
            "content": html_doc,
        }
        write_obj_to_json(obj, hash_file_path(url))
    #extract static links, filter links
    static_links = extract_static_links(html_doc)
    static_links = filter_links(static_links)
    #if link in static_history, skip, else requset and write to file, finally add to static_history
    for link in static_links:
        #link to absolute url
        link = join_url_current_relative(url, link)
        if link in static_history:
            continue
        else:
            static_history.add(link)
            static_content = get_content(link)
            if not link.endswith(tuple(binary_file_extension)):
                if static_content:
                    obj = {
                        "url": link,
                        "content": static_content.decode("utf-8"),
                    }
                    write_obj_to_json(obj, hash_file_path(link))
            else:
                obj = {
                    "url": link,
                    "content": base64.b64encode(static_content).decode("utf-8"),
                }
                write_obj_to_json(obj, hash_file_path(link))
    print("Processed link DONE: {}"+url)
def get_links_recursively(url,num_tag_list):
    print("Getting links recursively: {}".format(num_tag_list))
    #url = add_slash(url)
    if len(num_tag_list) > 3:
        return
    if url in html_history:
        return None
    else:
        html_history.add(url)
        html_doc = get_content(url).decode("utf-8")
        if html_doc:
            process_link(url,html_doc)
            links = filter_links(extract_html_links(html_doc))
            for (index, link) in enumerate( links):
                if link not in html_history:
                    newlink = join_url_current_relative(url,link)
                    tempnum=num_tag_list[:]
                    tempnum.append(index)
                    #print(tempnum)
                    get_links_recursively(newlink,tempnum)
    print("DONE_Recursive: {}".format(num_tag_list))

get_links_recursively(BASE_URL, [0])
