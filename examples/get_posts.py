#!/usr/bin/env python

"""
A simple example script to get all posts on a user's timeline.
Originally created by Mitchell Stewart.
<https://gist.github.com/mylsb/10294040>

By <anupdhml@gmail.com> Sep 20 2014

Based on the example from python facebook sdk, to use api v1.0
api 2.1 does not allow accesssing a user's feed when the user has not
signed up for the app(even if they are your friend)
Also dumps the posts into a json file which can be read later

Install this first
https://github.com/pythonforfacebook/facebook-sdk
"""

import facebook
import requests

import sys
import simplejson

# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/
# Select v1.0 for the api version, when generating access token
# Create a file access_token and paste it there. or just directly assign it here
access_token = open('access_token').read()

#dumps data to a json file
def put(data, filename):
	try:
		jsondata = simplejson.dumps(data, indent=4, skipkeys=True, sort_keys=True)
		fd = open(filename, 'w')
		fd.write(jsondata)
		fd.close()
	except:
		print 'ERROR writing', filename
		pass

# get data from a json file
def get(filename):
    returndata = {}
    try:
        fd = open(filename, 'r')
        text = fd.read()
        fd.close()
        returndata = simplejson.loads(text)
    except:
        print 'COULD NOT LOAD:', filename
    return returndata

def post_action(post, indent_marker=''):
    """ Here you might want to do something with each post. E.g. grab the
    post's message (post['message']) or the post's picture (post['picture']).
    In this implementation we just print the post's created time.
    """
    post_type    = post['type'] if post.get('type') else '(null)'
    post_time    = post['created_time'] if post.get('created_time') else '(null)'
    post_from    = post['from']['id'] + ' - ' + post['from']['name'].encode('utf-8') if post.get('from') else '(null)'
    post_content = simplejson.dumps(post['message']) if post.get('message') else '(null) {}'.format(post_type)
    #post_content = post['message'].encode('utf-8') if post.get('message') else '(null) {}'.format(post['type'])

    # includes status updates and message in links shared. Does not include
    # photo captions (will need to make another request with the photo id if that's needed)
    #post_details = '{} ^ {} ^ {}'.format(post_time, post_from, post_content)
    post_details = '{} | {} | {}'.format(post_time, post_from, post_content)
    print indent_marker + post_details

    if post.get('comments'):
        [post_action(comment, '>--') for comment in post['comments']['data']]

if __name__ == '__main__':
    if len(sys.argv)!=4:
        print 'usage: python get_posts.py\n\
            --from-api  <file_to_save_posts> <fb_username>\n\
            --from-file <file_to_read_posts> <fb_username>'
        sys.exit(1)

    (command, filename, user) = sys.argv[1:]

    if command == '--from-api':
        # api version seems to be determined from the access_token
        #graph = facebook.GraphAPI(access_token, version='1.0')
        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object(user)
        page = graph.get_connections(profile['id'], 'feed')
        #page = graph.get_connections(profile['id'], 'posts')
        #page = graph.get_connections(profile['id'], 'posts', **{'until':'1373083499'})
        #page = graph.get_connections(profile['id'], 'posts', **{'since':'1184544000'})
        # Wrap this block in a while loop so we can keep paginating requests until finished.
        all_pages = []
        while True:
            try:
                all_pages.append(page)
                # Perform some action on each post in the collection we receive from
                # Facebook.
                [post_action(post=post) for post in page['data']]
                # Attempt to make a request to the next page of data, if it exists.
                page = requests.get(page['paging']['next']).json()
            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break
        put(all_pages, filename)
    elif command == '--from-file':
        all_pages = get(filename)
        for page in all_pages:
            [post_action(post=post) for post in page['data']]
    else:
        print 'Invalid first argument'
        sys.exit(1)
