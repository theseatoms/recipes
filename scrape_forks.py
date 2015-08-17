from __future__ import print_function

# script that will traverse all forks of LarryMad/recipies,
#                  collect unique recipies,
#                  and save them in a directory in this repo

#TODO:  define unique-ness by file contents, vs filename (first implementation)
#TODO: pagination of forks data... am i getting all forks?

import os
import json
import urllib2

def api(REST_call):
    api_root = "https://api.github.com"
    query_url = api_root + REST_call 

    req = urllib2.Request(query_url)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def api_url(query_url):
    req = urllib2.Request(query_url)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

# -------------------------------------------------------------

#TODO implement authentication
#access_token = <FILL IN>

data = api("/repos/LarryMad/recipes")
larry_forks_url = data["forks_url"]
larry_forks_data = api_url(larry_forks_url)

output_filename = "recipe_paths"

for fork_data in larry_forks_data:
    GET_sha = "/repos/" + fork_data["full_name"] + "/git/refs/"
    data = api(GET_sha)
    
    sha = -1
    for dat in data:
        if dat["ref"] == "refs/heads/master":
            sha = dat["object"]["sha"]
            break
    if sha == -1:
        print("no 'refs/heads/master' found for " + str(fork_data) + "\n" + str(dat))
        continue

    GET_commit = "/repos/" + fork_data["full_name"] + "/git/commits/" + sha
    data = api(GET_commit)
    
    tree_sha = data["tree"]["sha"] # why? to ensure latest, "master" branch

    GET_tree = "/repos/" + fork_data["full_name"] + "/git/trees/" + tree_sha
    data = api(GET_tree)


    paths = [] 

    for file_data in data["tree"]:
        print(file_data) 
        print(file_data["url"])
        
        GET_contents = "/repos/" + fork_data["full_name"] + "/contents/" + file_data["path"]
        contents = api(GET_file_contents)

        owner = fork_data["full_name"].split("/")[0] # TODO check this
        print("owner: "+ owner )
        
        new_file_dir = os.getcwd() + "/" + fork_data["full_name"] + "/"
        new_file_path = os.getcwd() + "/" + fork_data["full_name"] + "/" + file_data["path"] 
        print(new_file_path)
        
        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir) 

        f = open(new_file_path, 'ab+')
        f.write(contents) 
        f.close()
         
        paths.append( file_data["path"] )
        
     
    # get recipes content
    # write recipes 


# known issues: appending on each run of the script

# useful links:
# http://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api


#alternate file_write
#print(file_data["path"], file=f)




