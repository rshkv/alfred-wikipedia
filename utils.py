def url_to_mobile(url):
    return url.replace('wikipedia.org', 'm.wikipedia.org') + '#content'


def url_to_dbpedia(url):
    return 'http://dbpedia.org/page/' + url.split('wiki/')[1]


class ResultsException(Exception):

    def __init__(self, query):
        self.message = "'{0}' not found".format(query)


class RequestException(Exception):

    def __init__(self, request):
        self.message = ('Endpoint not answering ({0})'
                        .format(request.url.split('?')[0]))
