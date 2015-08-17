#dumps Script that will traverse all forks of LarryMad/recipies,
#                  collect unique recipies,
#                  and save them in a directory in this repo

#TODO:  define unique-ness by file contents, vs filename (first implementation)

#TODO: pagination of forks data.... am i getting all forks?......

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

#access_token = <FILL IN>

data = api("/repos/LarryMad/recipes")
larry_forks_url = data["forks_url"]
larry_forks_data = api_url(larry_forks_url)

for fork_data in larry_forks_data:
    GET_sha = "/repos/" + fork_data["full_name"] + "/git/refs/"
    print "\n\n", GET_sha
    data = api(GET_sha)
    sha = data["sha"]

    GET_commit = "/repos/" + fork_data["full_name"] + "/git/commits/" + sha
    data = api(GET_commit)
    
    tree_sha = data["tree"]["sha"] #?????  but why?,,,, to ensure latest, "master" branch?

    GET_tree_contents = "/repos/" + fork_data["full_name"] + "/git/trees/" + tree_sha
    data = api(GET_tree_contents)

    paths = [] 

    for file_data in data["tree"]:
        path.append( file_data["path"] )
        # pick it up from here...............................TODO TODO TODO 
    
     
    # get recipes content
    # write recipes 



# useful links:
# http://stackoverflow.com/questions/25022016/get-all-file-names-from-a-github-repo-through-the-github-api







