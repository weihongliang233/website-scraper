import coloredlogs, logging
from typing import Union
# Create a logger object.
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import os
import urllib
#BASE_URL和BASE_DIR末尾一定是斜杠
BASE_URL = "https://www.haskell.org/"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\store\\"
html_history = set()
static_history = set()
url_and_tag = []
# Getting document from url
import requests

def add_slash(url):
    if url[-1] != '/':
        return url + '/'
    else:
        return url

def remove_slash(url):
    if url[-1] == '/':
        return url[:-1]
    else:
        return url

def get_doc_html(url):
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

def get_doc_static(url):
    print("Getting static from url: " + url)
    #url = remove_slash(url)
    try:
        doc = requests.get(url)
        if doc.status_code == 200:
            return doc.text
        else:
            return None
    except Exception as e:
        print(e)
        return None


def join_url_current_relative(current_url:str,relative_url:str):
    #print("Joining url: " + current_url + " and relative url: " + relative_url)
    #current_url = add_slash(current_url)
    #relative_url = add_slash(relative_url)

    #if relative_url starts with "../", then remove the last part of current_url
    '''
    if relative_url[:3] == '../':
        current_url_pieces = current_url.split('/')
        relative_url_pieces = relative_url.split('/')
        for i in range(3):
            current_url_pieces.pop()
        relative_url_pieces.pop(0)
        relative_url = '/'.join(relative_url_pieces)
        return '/'.join(current_url_pieces) + '/' + relative_url
    '''
    if "../" in relative_url:
        #但凡带有"../"的都认为已经process过
        return BASE_URL

    if relative_url.startswith("/"):
        return BASE_URL + relative_url[1:]
    else:
        return current_url + "/" + relative_url
join_url_current_relative = urllib.parse.urljoin
#join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","/sdfds")
#join_url_current_relative(BASE_URL+"intro/overview/","../_static/img/logo.png")
join_url_current_relative("https://docs.scrapy.org/en/latest/intro/overview.html","install.html")

#join file path
def join_file_path_html(absolute_url)->str:
    print("Joining html file path: " + absolute_url)
    relavitve_filename:str = absolute_url[len(BASE_URL):]
    if relavitve_filename:
        if relavitve_filename.endswith(tuple(['.html','.htm'])):
            pass
        else:
            relavitve_filename = add_slash(relavitve_filename) + 'index.html'
    
    #此时传入的absolute_url就是BASE_DIR
    else:
        relavitve_filename = "index.html"
    return os.path.join(BASE_DIR, relavitve_filename)



def join_file_path_static(absolute_url)->str:
    print("Joining html file path: " + absolute_url)
    relavitve_filename:str = absolute_url[len(BASE_URL):]
    if relavitve_filename:
        if relavitve_filename.endswith(tuple(['.js','.css','.png','.jpg','.jpeg','.gif','.svg'])):
            pass
        else:
            relavitve_filename = add_slash(relavitve_filename) + 'index.html'
    
    #此时传入的absolute_url就是BASE_DIR
    else:
        relavitve_filename = "index.html"
    return os.path.join(BASE_DIR, relavitve_filename)
#join_file_path_static("https://docs.scrapy.org/en/latest/")
#join_file_path_static("https://docs.scrapy.org/en/latest/topics/")
#join_file_path_static("https://docs.scrapy.org/en/latest/topics/min.js")

def write_file(doc, filename):
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
def filter_html_links(links: list[str]):
    #if link is not anchor, not start with http, not start with irc`, no "?"
    return [link for link in links if link and not "#" in link and  not link.startswith("http") and not link.startswith("irc") and not "?" in link]
            
    

def filter_static_links(links:list[str]):
    #if link is not start with http, not start with irc
    return [link for link in links if link and not "#" in link and  not link.startswith("http") and not link.startswith("irc") and not "?" in link and not link.endswith(".js")]

def process_link(url,html_doc):
    print("Processing link: {}"+url)
    #url = add_slash(url)

    html_history.add(url)
    if html_doc:
        write_file(html_doc, join_file_path_html(url))
    #extract static links, filter links
    static_links = extract_static_links(html_doc)
    static_links = filter_static_links(static_links)
    #if link in static_history, skip, else requset and write to file, finally add to static_history
    for link in static_links:
        #link to absolute url
        link = join_url_current_relative(url, link)
        if link in static_history:
            continue
        else:
            static_history.add(link)
            static_doc = get_doc_static(link)
            if static_doc:
                write_file(static_doc, join_file_path_static(link))
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
        html_doc = get_doc_html(url)
        if html_doc:
            process_link(url,html_doc)
            links = filter_html_links(extract_html_links(html_doc))
            for (index, link) in enumerate( links):
                if link not in html_history:
                    newlink = join_url_current_relative(url,link)
                    tempnum=num_tag_list[:]
                    tempnum.append(index)
                    #print(tempnum)
                    get_links_recursively(newlink,tempnum)
    print("DONE_Recursive: {}".format(num_tag_list))

get_links_recursively(BASE_URL, [0])