from typing import List
from app.es_data import es_data

class ElasticSearchMultiSearchQuery:

    def __init__(self, index, body):
        self.index = index
        self.body = body


DATA_CONNECTION = 'data'

def do_multi_search(queries: List[ElasticSearchMultiSearchQuery]):
    try:

        multi_search_body = []
        for query_i in queries:
            multi_search_body.append({'index': query_i.index})
            if query_i.body is None:
                query_i.body = {}
            query_i.body['track_total_hits'] = True
            multi_search_body.append(query_i.body)

        result = es_data.do_multisearch(body=multi_search_body)

        return result
    except Exception as e:
        raise Exception('ERROR: can\'t retrieve elastic search data!')