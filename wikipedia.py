#!/usr/bin/python
import unicodedata
import json
import sys
import os

from lib import requests


def search(query, lang, max_hits):
    """Use Wikipedia's search API to find matches
    """
    # Convert Alfred's decomposed utf-8 to composed as expected by the endpoint
    q = unicodedata.normalize('NFC', query.decode('utf-8')).encode('utf-8')
    response = requests.get(
        url='https://{lang}.wikipedia.org/w/api.php'.format(lang=lang),
        params={'action': 'query',
                'format': 'json',
                'utf8': '',
                # Build generator
                'generator': 'search',
                'gsrsearch': q,
                'gsrlimit': max_hits,
                # Get properties
                'prop': 'extracts|info',
                'explaintext': '',
                'exintro': '',
                'exlimit': 'max',
                'exsentences': '1',
                'inprop': 'url'})

    # Raise error on 4xx and 5xx status codes
    response.raise_for_status()

    response = json.loads(response.content.decode('utf-8'))
    results = response['query']['pages'].values()
    return results


def url_to_mobile(url):
    return url.replace('wikipedia.org', 'm.wikipedia.org') + '#content'


def url_to_dbpedia(url):
    return 'http://dbpedia.org/page/' + url.split('wiki/')[1]


def alfred_item(result):
    """Return result dictionary in Alfred format
    """
    title = result['title']
    subtitle = result['extract']
    url = result['fullurl']
    mobile_url = url_to_mobile(url)
    dbpedia_url = url_to_dbpedia(url)

    return {
        'title': title,
        'subtitle': subtitle,
        'arg': url,  # Passed on to action
        'uid': title,  # Used to learn order
        'autocomplete': title,  # Added to search field
        'quicklookurl': mobile_url,  # Opened on quick look
        'text': {'copy': url,  # Pasted to clipboard
                 'largetype': title},  # Shown in large
        'mods': {
            # Hold cmd to open mobile Wikipedia (better for reading)
            'cmd': {'arg': mobile_url,
                    'subtitle': 'Open in mobile version'},
            # Hold ctrl to open DBpedia page
            'ctrl': {'arg': dbpedia_url,
                     'subtitle': 'Open in DBpedia'}}}


def language(query):
    lang, query = query.split('.')
    return lang.strip(), query.strip()


def alfred_output(results):
    """Return Alfred output
    """
    items = [alfred_item(result) for result in results]
    return json.dumps({'items': items}, ensure_ascii=False).encode('utf-8')


def error_message(exception):
    msg = {'items': [{'title': 'Endpoint currently not answering',
                      'subtitle': exception.request.url.split('?')[0]}]}
    return json.dumps(msg)


if __name__ == "__main__":
    # Get settings
    max_hits = os.getenv('maxHits') or 9
    lang = os.getenv('defaultLang') or 'en'
    # Get query
    query = sys.argv[1]
    if '.' in query:
        lang, query = language(query)
    # Try connection
    try:
        # Get matches for input
        hits = search(query, lang, max_hits)
        # Return Alfred output
        output = alfred_output(hits)
        print(output)
    except requests.exceptions.RequestException as e:
        # Return error
        print(error_message(e))
