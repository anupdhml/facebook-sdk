#!/usr/bin/env python

"""
A simple example script to get all the chats with a user, from all threads
Also dumps the messages into a json file which can be read later

By <anupdhml@gmail.com> Sep 21 2014

Install this first
https://github.com/pythonforfacebook/facebook-sdk
"""

import facebook
import requests

import sys
import simplejson
import dateutil.parser as dateparser
import time

# You'll need an access token here to do anything.  You can get a temporary one
# here: https://developers.facebook.com/tools/explorer/
# Select v1.0 for the api version, when generating access token
# Create a file access_token and paste it there. or just directly assign it here
access_token = open('access_token').read()

def get_all_thread_messages(graph, thread_id):
    """Here, we grab all the messages in the thread and apply message_action to each
    Also dumps all the messages in a file
    """
    # Get the thread info for filename
    thread = graph.get_object(thread_id)
    thread_recipients = [ recipient['name'] for recipient in thread['to']['data'] ]
    thread_details = "{} - {} - {}".format(thread_id, thread['updated_time'], ', '.join(thread_recipients))
    print '\nGathering messages for ', thread_details

    all_messages = {}
    all_pages = []
    page = graph.get_connections(thread_id, 'comments')

    # Wrap this block in a while loop so we can keep paginating requests until
    # finished.
    while True:
        try:
            all_pages.append(page)
            # Perform some action on each message in the collection we receive from
            # Facebook.
            [message_action(message=message) for message in page['data']]
            # fb does not return messages chronologically (even with the documented options)
            # so maintain a list of messages to print them chronologically 
            for message in page['data']:
                timestamp = dateparser.parse(message['created_time'])
                unix_time = time.mktime(timestamp.timetuple())
                all_messages[unix_time] = message

            # Attempt to make a request to the next page of data, if it exists.
            page = requests.get(page['paging']['next']).json()
        except KeyError:
            print 'error'
            print page
            # When there are no more pages (['paging']['next']), break from the
            # loop and end the script.
            break

    print '\n\nNow listing these chronologically'
    keylist = all_messages.keys()
    keylist.sort()
    for key in keylist:
        message_action(all_messages[key])

    put(all_pages, thread_details+'.json')

def message_action(message):
    """ Here you might want to do something with each thread.
    Here, we just print the message details
    """
    msg_time    = message['created_time'] if message.get('created_time') else '(null)'
    msg_from    = message['from']['name'].encode('utf-8') if message.get('from') else '(null)'
    msg_content = message['message'].encode('utf-8') if message.get('message') else '(null)'

    message_details = '{} | {} | {}'.format(msg_time, msg_from, msg_content)
    print message_details

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

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'usage: python get_messages.py\n\
            --from-api  <chat_fb_username>\n\
            --from-file <filename_with _chats>'
        sys.exit(1)

    command  = sys.argv[1]

    if command == '--from-api':
        username = sys.argv[2]
        graph = facebook.GraphAPI(access_token)
        profile = graph.get_object(username)
        profile_id = profile['id']
        my_profile = graph.get_object('me')
        page = graph.get_connections(my_profile['id'], 'inbox')

        # USING FQL
        # Get all the messages to you by a single user from all threads
        # works in the graph api explorer with v1.0, but for some reason, always returs
        # None from here
        #message_query = "SELECT thread_id, created_time, message_id, body FROM message\
                         #WHERE author_id = {}\
                         #AND thread_id IN (SELECT thread_id\
                                           #FROM thread\
                                           #WHERE (folder_id = 1 OR folder_id = 0)\
                                           #AND {} IN (recipients))\
                         #ORDER BY created_time DESC\
                         #LIMIT 25".format(user_id, user_id)
        #messages = graph.fql(message_query)

        # Determine threads where conversation happened against user with profile_id
        # Wrap this block in a while loop so we can keep paginating requests until
        # finished.
        print 'Determining valid chat threads...'
        valid_threads = []
        while True:
            try:
                # Perform some action on each post in the collection we receive from
                # Facebook.
                for thread in page['data']:
                    thread_recipients = [ recipient['id'] for recipient in thread['to']['data'] ]
                    if profile_id in thread_recipients:
                        print thread['id'], ': valid'
                        valid_threads.append(thread['id'])
                    else:
                        print thread['id'], ': invalid'
                # Attempt to make a request to the next page of data, if it exists.
                page = requests.get(page['paging']['next']).json()
            except KeyError:
                # When there are no more pages (['paging']['next']), break from the
                # loop and end the script.
                break

        print 'Thread ids for chats with the given user: ', valid_threads
        [get_all_thread_messages(graph, thread_id) for thread_id in valid_threads]
    elif command == '--from-file':
        filename = sys.argv[2]
        all_pages = get(filename)
        for page in all_pages:
            [message_action(message=message) for message in page['data']]
    else:
        print 'Invalid first argument' 
        sys.exit(1)
