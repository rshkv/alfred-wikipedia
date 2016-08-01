#!/usr/bin/python
import json
import sys
import os

from lib import requests


def lookup_results(query, max_hits):
    """Find DBpedia entities whose label matches the query. Results are ordered
    by the number of inlinks pointing from other articles.
    """
    response = requests.get(
        url="http://lookup.dbpedia.org/api/search/PrefixSearch",
        params={
            "QueryClass": None,
            "MaxHits": max_hits,
            "QueryString": query
        },
        headers={
            "Accept": "application/json"
        }
    )
    return json.loads(response.content.decode('utf-8'))['results']


def uris(results):
    """Get Wikipedia and mobile urls from the DBpedia uris of the results.
    """

    def dbp_wiki(uri):
        return uri.replace('http://dbpedia.org/resource/',
                           'https://en.wikipedia.org/wiki/')

    def dbp_to_mobile(uri):
        return uri.replace('http://dbpedia.org/resource/',
                           'https://en.m.wikipedia.org/wiki/') + '#content'

    return [{
                'title': result['label'],
                'description': result['description'],
                'wikipedia_uri': dbp_wiki(result['uri']),
                'mobile_uri': dbp_to_mobile(result['uri']),
                'dbpedia_uri': result['uri']
            } for result in results]


def alfred_output(results):
    """Return Alfred output.
    """
    items = [{
                 'title': result['title'],
                 'subtitle': result['description'],

                 'arg': result['wikipedia_uri'],  # Passed on to action
                 'uid': result['wikipedia_uri'],  # Used to learn order
                 'autocomplete': result['title'],  # Added to search field

                 'quicklookurl': result['mobile_uri'],  # Opened on quick look
                 'text': {
                     'copy': result['wikipedia_uri'],  # Pasted to clipboard
                     'largetype': result['description']  # Shown in large type
                 },
                 'mods': {
                     # Hold cmd to open mobile Wikipedia (better for reading)
                     'cmd': {
                         'arg': result['mobile_uri'],
                         'subtitle': 'Open in mobile version'
                     },
                     # Hold ctrl to open DBpedia resource
                     'ctrl': {
                         'arg': result['dbpedia_uri'],
                         'subtitle': 'Open in DBpedia'
                     },
                 }
             } for result in results]
    # Return results as encoded JSON
    return json.dumps({'items': items}, ensure_ascii=False).encode('utf-8')


if __name__ == "__main__":
    # Get input
    query = sys.argv[1]
    max_hits = os.getenv('maxHits') or 9
    # Get matches for input
    hits = lookup_results(query, max_hits)
    hits = uris(hits)
    hits.insert(0, {'title': query})
    # Return Alfred output
    output = alfred_output(hits)
    print(output)
