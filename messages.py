import json
import re
import requests
import sys

_BASE_URL = 'https://api.groupme.com/v3/' 
_GROUP_NAME = 'Nerdery'

def get_token():
    with open('./access_token.txt', 'r') as token_file:
        access_token = token_file.read().strip()
        return access_token

def get_group_id(access_token):
    groups_url = _BASE_URL + 'groups?omit=memberships&token=' + access_token
    response_json = requests.get(groups_url).json()
    list_of_groups = response_json['response']

    group_id = None
    for group in list_of_groups:
        if group['name'] == _GROUP_NAME:
            group_id = group['group_id']
            break
    return group_id

def read_messages(group_id, access_token):
    initial_messages_url = _BASE_URL +  'groups/{}/messages?limit=100&token=' + access_token
    next_messages_url = _BASE_URL +  'groups/{}/messages?before_id={}&limit=100&token=' + access_token

    messages_json = requests.get(initial_messages_url.format(group_id)).json()
    messages = messages_json['response']['messages']

    all_messages = [x['text'] for x in messages]
    last_id = messages[-1]['id']

    while True:
        response = requests.get(next_messages_url.format(group_id, last_id))
        if response.status_code == 304:
            # This means no more messages to read.
            break

        next_messages = response.json()['response']['messages']
        all_messages.extend(x['text'] for x in next_messages)
        last_id = next_messages[-1]['id']
    return all_messages


quote_regex = re.compile(r'.*[\"\'\u0022\u0027\u2018\u201c].*[\"\'\u0022\u0027\u2019\u201d].*\s-\s.*',  re.DOTALL)
def generate_messages(messages):
    for m in messages:
        if quote_regex.match(str(m)):
            yield m

def main():
    access_token = get_token()
    group_id = get_group_id(access_token)
    messages = read_messages(group_id, access_token)

    for msg in generate_messages(messages):
        print(msg)
        print('\n')

if __name__ ==  "__main__":
    sys.exit(main())
