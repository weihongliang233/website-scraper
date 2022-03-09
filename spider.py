import coloredlogs, logging
from typing import Union
# Create a logger object.
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import os
import urllib
#BASE_URL和BASE_DIR末尾一定是斜杠
BASE_URL = "https://www.haskell.org/"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\storeScrapy_Documentation\\"
html_history = set()
static_history = set()
url_and_tag = []
# Getting document from url
import requests

def get_doc(url):
    print("Getting html from url: " + url)
    #url = add_slash(url)
    
    try:
        doc = requests.get(url)
        if doc.status_code == 200:
            return doc.text
        else:
            print("Failed")
            print(url)
            print(doc.status_code)
            return None
    except Exception as e:
        print(e)
        return None

join_url_current_relative = urllib.parse.urljoin
#join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","/sdfds")
#join_url_current_relative(BASE_URL+"intro/overview/","../_static/img/logo.png")
#join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","install.html")

#join file path
static_filename_extension = ['.html','.htm','.js','.css','.png','.jpg','.jpeg','.gif','.svg','.ico','.ttf','.woff','.woff2','.eot']
def join_file_path(absolute_url)->str:
    print("Joining file path: " + absolute_url)
    relavitve_filename:str = absolute_url[len(BASE_URL):]
    if relavitve_filename:
        if relavitve_filename.endswith(tuple(static_filename_extension)):
            pass
        elif relavitve_filename.endswith('/'):
            relavitve_filename += 'index.html'
        elif not '.' in relavitve_filename:
            relavitve_filename = os.path.join(relavitve_filename, 'index.html')
        else:
            return ""
    
    #此时传入的absolute_url就是BASE_DIR
    else:
        relavitve_filename = "index.html"
    return os.path.join(BASE_DIR, relavitve_filename)
#join_file_path_html("https://docs.scrapy.org/en/latest/")
#join_file_path_html("https://docs.scrapy.org/en/latest/topics/")
#join_file_path_html("https://docs.scrapy.org/en/latest/topics.html")
join_file_path("https://www.gitbook.com/explore-categories/api-docs/")


def write_file(doc, filename):
    if filename=="":
        return
    if not os.path.exists(os.path.dirname(filename)):   
        os.makedirs(os.path.dirname(filename))
    else:
        print("Exist: {}".format(filename))
    
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(doc)
        print("Writed to file: {}".format(filename))
        #再加一点错误处理
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


def process_link(url,html_doc):
    print("Processing link: {}"+url)
    #url = add_slash(url)

    html_history.add(url)
    write_file(html_doc, join_file_path(url))
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
            static_doc = get_doc(link)
            if static_doc:
                write_file(static_doc, join_file_path(link))
                pass
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
        html_doc = get_doc(url)
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