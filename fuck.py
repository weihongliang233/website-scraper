import coloredlogs, logging
from typing import Union
# Create a logger object.
logger = logging.getLogger(__name__)
from bs4 import BeautifulSoup
import os
#BASE_URL和BASE_DIR末尾一定是斜杠
BASE_URL = "https://docs.scrapy.org/en/latest/"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\storeScrapy_Documentation\\"
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
    url = add_slash(url)
    
    try:
        doc = requests.get(url)
        if doc.status_code == 200:
            return doc.text
        else:
            return None
    except Exception as e:
        print(e)
        return None

def get_doc_static(url):
    url = remove_slash(url)
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
    current_url = add_slash(current_url)
    relative_url = add_slash(relative_url)

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
        return BASE_URL

    temp = (current_url+relative_url).replace('//','/')
    temp = temp.replace('http:/', 'http://')
    temp = temp.replace('https:/', 'https://')

    return temp

join_url_current_relative(BASE_URL,"/sdfds")
#join_url_current_relative(BASE_URL+"intro/overview/","../_static/img/logo.png")
#join file path
def join_file_path_html(absolute_url)->str:
    absolute_url = add_slash(absolute_url)

    relavitve_filename = absolute_url[len(BASE_URL):]
    if relavitve_filename:
        if relavitve_filename.endswith('.html'):
            pass
        else:
            relavitve_filename += "index.html"
    
    #此时传入的absolute_url就是BASE_DIR
    else:
        relavitve_filename = "index.html"
    return os.path.join(BASE_DIR, relavitve_filename)

join_file_path_html("https://docs.scrapy.org/en/latest/")
#join_file_path_html("https://docs.scrapy.org/en/latest/topics/")



def join_file_path_static(url)->str:
    url = add_slash(url)

    relavitve_filename = url[len(BASE_URL):]
    if relavitve_filename:
        #if url has filename extension
        lastname = relavitve_filename.split("/")[-2]
        if "." in lastname:
            pass
        else:
            raise Exception("No file extension")
    #此时传入的absolute_url就是BASE_DIR
    else:
        raise Exception("static file path should not be empty")
    final =  os.path.join(BASE_DIR, relavitve_filename)
    return final[:-1]

#join_file_path_static("https://docs.scrapy.org/en/latest/")
#join_file_path_static("https://docs.scrapy.org/en/latest/topics/")
join_file_path_static("https://docs.scrapy.org/en/latest/topics/min.js")
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
    return extract_css_links(doc) + extract_image_links(doc)
def filter_html_links(links: list[str]):
    #if link is not anchor, not start with http, not start with irc`
    return [link for link in links if link and not "#" in link and  not link.startswith("http") and not link.startswith("irc")]
            
    

def filter_static_links(links:list[str]):
    #if link is not start with http, not start with irc
    return [link for link in links if link and not "#" in link and  not link.startswith("http") and not link.startswith("irc")]

def process_link(url):
    url = add_slash(url)

    html_history.add(url)
    doc = get_doc_static(url)
    if doc:
        write_file(doc, join_file_path_html(url))
    #extract static links, filter links
    static_links = extract_static_links(doc)
    static_links = filter_static_links(static_links)
    #if link in static_history, skip, else requset and write to file, finally add to static_history
    for link in static_links:
        #link to absolute url
        link = join_url_current_relative(url, link)
        if link in static_history:
            continue
        else:
            static_history.add(link)
            doc = get_doc_static(link)
            if doc:
                write_file(doc, join_file_path_static(link))
    else:
        return None
def get_links_recursively(url,num_tag_list):
    url = add_slash(url)

    if url in html_history:
        return None
    else:
        html_history.add(url)
        doc = get_doc_html(url)
        if doc:
            process_link(url)
            links = filter_html_links(extract_html_links(doc))
            for (index, link) in enumerate( links):
                newlink = join_url_current_relative(url,link)
                if link not in html_history:
                    tempnum=num_tag_list[:]
                    tempnum.append(index)
                    get_links_recursively(newlink,num_tag_list)

get_links_recursively(BASE_URL, [0])