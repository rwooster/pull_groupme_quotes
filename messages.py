import json
import re
import requests


with open('./access_token.txt', 'r') as token_file:
    access_token = token_file.read().strip()

_BASE_URL = 'https://api.groupme.com/v3/' 

groups_url = _BASE_URL + 'groups?omit=memberships&token=' + access_token
messages_url = _BASE_URL +  'groups/{}/messages?limit=100&token=' + access_token

response_json = requests.get(groups_url).json()
list_of_groups = response_json['response']

nerdery_id = None
for group in list_of_groups:
    if group['name'] == 'Nerdery':
        nerdery_id = group['group_id']
        break

messages_json = requests.get(messages_url.format(nerdery_id)).json()
messages = messages_json['response']['messages']

all_messages = [x['text'] for x in messages]

last_id = messages[-1]['id']

while True:
    next_msg_format = _BASE_URL +  'groups/{}/messages?before_id={}&limit=100&token=' + access_token
    next_page_of_messages_url  = next_msg_format.format(nerdery_id, last_id)

    response = requests.get(next_page_of_messages_url.format(nerdery_id))
    if response.status_code == 304:
        # This means no more messages to read.
        break

    next_messages = response.json()['response']['messages']
    all_messages.extend(x['text'] for x in next_messages)
    last_id = next_messages[-1]['id']


left_quotes = r'[", \', \u0022, \u0027, \u2018, \u201c]'
right_quotes = r'[", \', \u0022, \u0027, \u2019, \u201d]'
quote_format = '.*' + left_quotes + '.*' + right_quotes + '.*'



quote_regex = re.compile(r'.*[\"\'\u0022\u0027\u2018\u201c].*[\"\'\u0022\u0027\u2019\u201d].*\s-\s.*',  re.DOTALL)

# import pdb; pdb.set_trace()
for m in all_messages:
    if quote_regex.match(str(m)):
        print(m)
