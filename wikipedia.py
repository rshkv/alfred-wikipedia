#!/usr/bin/python
import json
import sys
import os

from lib import requests

MAX_HITS = os.getenv('maxHits') or 9


def dbp2wiki(uri):
    return uri.replace('http://dbpedia.org/resource/',
                       'https://en.wikipedia.org/wiki/')


def dbp2mwiki(uri):
    return uri.replace('http://dbpedia.org/resource/',
                       'https://en.m.wikipedia.org/wiki/') + '#content'


response = requests.get(
    url="http://lookup.dbpedia.org/api/search/PrefixSearch",
    params={
        "QueryClass": None,
        "MaxHits": MAX_HITS,
        "QueryString": sys.argv[1]
    },
    headers={
        "Accept": "application/json",
    },
)

results = json.loads(response.content.decode('utf-8'))['results']
items = [{
             'title': result['label'],
             'arg': dbp2wiki(result['uri']),
             'subtitle': result['description'],

             'uid': result['uri'],
             'autocomplete': result['label'],
             'quicklookurl': dbp2mwiki(result['uri']),
             'text': {
                 'copy': dbp2wiki(result['uri']),
                 'largetype': result['description']
             },
             'mods': {
                 'cmd': {
                     'arg': dbp2mwiki(result['uri']),
                     'subtitle': 'Open in mobile version'
                 },
                 'ctrl': {
                     'arg': result['uri'],
                     'subtitle': 'Open in DBpedia'
                 },
             }
         } for result in results]

print(json.dumps({'items': items}, ensure_ascii=False).encode('utf-8'))
