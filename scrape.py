#get all filename of a directory
import os
def get_file_list(dir_path):
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list
import base64
PRE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\pre"
BASE_DIR = "E:\Temp\practice_scrapy\\tutorial\src\storeScrapy_Documentation\\"
BASE_URL = "https://git-scm.com/"
#keep the domian part of the url
DOMAIN = "https://git-scm.com/"

get_file_list(PRE_DIR)
#join objects to a dictionary
def join_dict(dict_list):
    result = {}
    for d in dict_list:
        result.update(d)
    return result
# read json file to dict
def read_json(file_path):
    import json
    with open(file_path, 'r') as f:
        return json.load(f)
list_of_objs = [ read_json(get_file_list(PRE_DIR)[i]) for i in range(len(get_file_list(PRE_DIR))) ]
static_filename_extension = ['.html','.htm','.js','.css','.png','.jpg','.jpeg','.gif','.svg','.ico','.ttf','.woff','.woff2','.eot']
def join_file_path(absolute_url)->str:
    print("Joining file path: " + absolute_url)
    relavitve_filename:str = absolute_url[len(DOMAIN):]
    if relavitve_filename:
        if relavitve_filename.endswith(tuple(static_filename_extension)):
            pass
        elif relavitve_filename.endswith('/'):
            relavitve_filename += 'index.html'
        else:
            return ""
    
    #此时传入的absolute_url就是BASE_DIR
    else:
        relavitve_filename = "index.html"
    return os.path.join(BASE_DIR, relavitve_filename)
#binary file extension
binary_file_extension = ['.png','.jpg','.jpeg','.gif','.svg','.ico','.ttf','.woff','.woff2','.eot']
def write_file(content_binary_or_text:str, filename):
    if filename=="":
        return
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    else:
        print("Exist: {}".format(filename))
    
    if filename.endswith(tuple(binary_file_extension)):
        with open(filename, 'wb' ) as f:
            f.write(base64.b64decode(content_binary_or_text.encode('utf-8')))
    else:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content_binary_or_text)
        #再加一点错误处理
#traverse list_of_objs, write file
for obj in list_of_objs:
    write_file(obj['content'], join_file_path(obj['url']))