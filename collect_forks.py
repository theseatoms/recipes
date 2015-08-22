from __future__ import print_function

# this script that traverses all forks of LarryMad/recipies,
#                  collects the unique recipies (by filename),
#                  and saves them in a 'recipes' directory in this repo

#TODO:  define unique-ness by file contents, vs filename (first implementation)

import time
import os
import json
import urllib2
import re
import glob
#from requests_oauthlib import OAuth2Session # TODO someday
import config
import requests
from requests.auth import HTTPBasicAuth

# authenticate user
try:
    requests.get('https://api.github.com/user', auth=HTTPBasicAuth(config.USERNAME, config.PASSWORD))
except requests.exceptions.ConnectionError as e:
    print(e.args)
    print(e.args[0])

# -----

def api(REST_call, include_header=False):
    time.sleep(2)
    api_root = "https://api.github.com"
    query_url = api_root + REST_call 
    response = requests.get(query_url, auth=(config.USERNAME, config.PASSWORD))

    if include_header:
        return (json.loads(json.dumps(dict(response.headers))), json.loads(response.text))
    else:
        return json.loads(response.text)

def api_url(query_url, include_header=False):
    time.sleep(2)
    response = requests.get(query_url, auth=(config.USERNAME, config.PASSWORD))

    if include_header:
        return (json.loads(json.dumps(dict(response.headers))), json.loads(response.text))
    else:
        return json.loads(response.text)


def build_direction_dict(header):
    directions_dict = {}
    pages_links = header["link"]
    pages_data = pages_links.split(',')

    for link in pages_data:
        value_key = link.split(';')    
        key = re.search('"([^"]*)"' , value_key[1]).group(0)[1:-1] # word betweeen double quotes
        value = value_key[0][1:-1]
         
        directions_dict[key] = value

    return directions_dict


def download_aggregate_and_rename_unique(forks_data, larrys_recipes):
    GET_sha = "/repos/" + forks_data["full_name"] + "/git/refs/"
    data = api(GET_sha)
    
    sha = -1
    for dat in data:
        if dat["ref"] == "refs/heads/master":
            sha = dat["object"]["sha"]
            break
    if sha == -1:
        print("no 'refs/heads/master' found for " + str(forks_data) + "\n" + str(dat))
        return

    GET_commit = "/repos/" + forks_data["full_name"] + "/git/commits/" + sha
    data = api(GET_commit)
    tree_sha = data["tree"]["sha"] # why? to ensure latest, "master" branch

    GET_tree = "/repos/" + forks_data["full_name"] + "/git/trees/" + tree_sha
    data = api(GET_tree)

    for file_data in data["tree"]:
        if file_data["path"] in larrys_recipes or file_data["path"].find("README") != -1:
            continue

        GET_contents = "/repos/" + forks_data["full_name"] + "/contents/" + file_data["path"]
        contents = api(GET_contents)
                
        owner = forks_data["full_name"].split("/")[0]
        # owner = forks_data["owner"]["login"]
        
        new_file_dir = os.getcwd() + "/recipes/" 
        new_file_path = os.getcwd() + "/recipes/" + owner + "--" + file_data["path"] 
        print("new file :", new_file_path)
        
        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir) 

        f = open(new_file_path, 'ab+')
        f.write(urllib2.urlopen(contents["download_url"]).read())
        f.close()

def download_content(forks_data):
    GET_sha = "/repos/" + forks_data["full_name"] + "/git/refs/"
    data = api(GET_sha)
    
    sha = -1
    for dat in data:
        if dat["ref"] == "refs/heads/master":
            sha = dat["object"]["sha"]
            break
    if sha == -1:
        print("no 'refs/heads/master' found for " + str(forks_data) + "\n" + str(dat))
        return

    GET_commit = "/repos/" + forks_data["full_name"] + "/git/commits/" + sha
    data = api(GET_commit)
    tree_sha = data["tree"]["sha"] # why? to ensure latest, "master" branch

    GET_tree = "/repos/" + forks_data["full_name"] + "/git/trees/" + tree_sha
    data = api(GET_tree)

    paths = [] 

    for file_data in data["tree"]:
        GET_contents = "/repos/" + forks_data["full_name"] + "/contents/" + file_data["path"]
        contents = api(GET_contents)
                
        owner = forks_data["full_name"].split("/")[0]
        # owner = forks_data["owner"]["login"]
        
        new_file_dir = os.getcwd() + "/knives/" + owner + "/"
        new_file_path = os.getcwd() + "/knives/" + owner + "/" + file_data["path"] 
        print("new file :", new_file_path)
        
        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir) 

        f = open(new_file_path, 'ab+')
        f.write(urllib2.urlopen(contents["download_url"]).read())
        f.close()
         
        paths.append( file_data["path"] )

# -------------------------------------------------------------

# initial api call, top level repo
data = api("/repos/LarryMad/recipes")
larry_forks_url = data["forks_url"]

# get all forks, paginated links live in the header response
header, larry_forks_data = api_url(larry_forks_url, include_header=True)

# parse links and build dict of "first", "next", "last", "prev" dict
directions_dict = build_direction_dict(header)

remaining_pages = int(directions_dict["last"][directions_dict["last"].index('=')+1:]) - 1

larrys_recipes = glob.glob('*.txt')
#print(larrys_recipes)

# loop through paginated results
while remaining_pages > 0:

    for fork_data in larry_forks_data:
        #download_content(fork_data)
        download_aggregate_and_rename_unique(fork_data, larrys_recipes)

    print(json.dumps(header, indent=4))

    header, larry_forks_data = api_url(directions_dict["next"], include_header=True)
    directions_dict = build_direction_dict(header)
    
    print("next: ", directions_dict["next"])

    next_page = int(directions_dict["next"][directions_dict["next"].index('=')+1:])
    last_page = int(directions_dict["last"][directions_dict["last"].index('=')+1:])
    remaining_pages = last_page - next_page + 1
    print(next_page, last_page, remaining_pages)

# useful links:
# http://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api

