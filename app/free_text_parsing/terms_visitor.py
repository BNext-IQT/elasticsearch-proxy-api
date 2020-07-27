"""
Terms Visitor
"""
import urllib
import traceback
import re

from arpeggio import PTNodeVisitor
import arpeggio
import requests
from urllib.parse import urlparse

from app.free_text_parsing.grammar import inchi
from app.config import RUN_CONFIG

WS_URL = 'https://www.ebi.ac.uk/chembl/api/data'
WS_PARSED_URL = urlparse(WS_URL)
WS_DOMAIN = WS_PARSED_URL.scheme + '://' + WS_PARSED_URL.netloc

ELASTICSEARCH_EXTERNAL_URL = 'https://www.ebi.ac.uk/chembl/glados-es'
CHEMBL_ES_INDEX_PREFIX = 'chembl_'

__CHEMBL_REGEX_STR = r'^chembl[^\d\s]{0,2}([\d]+)[^\d\s]{0,2}$'
CHEMBL_REGEX = re.compile(__CHEMBL_REGEX_STR, flags=re.IGNORECASE)

__DOI_REGEX_STR = r'^(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>|])\S)+)$'
DOI_REGEX = re.compile(__DOI_REGEX_STR)

INTEGER_REGEX = re.compile(r'^\d+$')

CHEMBL_ENTITIES = {
    'target': 'targets',
    'compound': 'compounds',
    'molecule': 'compounds',
    'document': 'documents',
    'assay': 'assays',
    'cell': 'cells',
    'tissue': 'tissues'
}


def check_chembl_entities(term_dict: dict):
    term = term_dict['term'].lower()
    if len(term) > 0 and term[-1] == 's':
        term = term[0:-1]
    if term in CHEMBL_ENTITIES:
        term_dict['chembl_entity'] = CHEMBL_ENTITIES[term]


def check_doi(term_dict: dict):
    re_match = DOI_REGEX.match(term_dict['term'])
    if re_match is not None:
        try:
            chembl_ids = []
            response = requests.get(
                '{es_url}/{index_prefix}document/_search'.format(
                    es_url=ELASTICSEARCH_EXTERNAL_URL,
                    index_prefix=CHEMBL_ES_INDEX_PREFIX
                ),
                json=
                {
                    'size': 10,
                    '_source': 'document_chembl_id',
                    'query': {
                        'term': {
                            'doi': {
                                'value': term_dict['term']
                            }
                        }
                    }
                },
                timeout=5
            )
            json_response = response.json()
            for hit_i in json_response['hits']['hits']:
                chembl_ids.append(hit_i['_source']['document_chembl_id'])
            if chembl_ids:
                term_dict['references'].append(
                    {
                        'type': 'doi',
                        'label': 'DOI (Digital Object Identifier)',
                        'chembl_ids': get_chembl_id_list_dict(chembl_ids),
                        'include_in_query': True,
                        'chembl_entity': 'document'
                    }
                )
        except:
            traceback.print_exc()


def check_integer(term_dict: dict):
    re_match = INTEGER_REGEX.match(term_dict['term'])
    if re_match is not None:
        term_dict['references'].append(
            {
                'type': 'integer_chembl_id',
                'label': 'Integer as ChEMBL ID',
                'chembl_ids': [
                    get_chembl_id_dict('CHEMBL{0}'.format(term_dict['term']))
                ],
                'include_in_query': True
            }
        )


def check_chembl(term_dict: dict):
    re_match = CHEMBL_REGEX.match(term_dict['term'])
    if re_match is not None:
        chembl_id_num = re_match.group(1)
        term_dict['references'].append(
            {
                'type': 'chembl_id',
                'label': 'ChEMBL ID',
                'chembl_ids': [
                    get_chembl_id_dict('CHEMBL{0}'.format(chembl_id_num))
                ],
                'include_in_query': True
            }
        )


def adjust_exact_term(exact_term: str) -> str:
    if exact_term[-1] == '"':
        return exact_term
    elif exact_term[-1] == "'":
        first_char = 1
        prefix = ""
        if exact_term[0] == '+' or exact_term[0] == '-':
            first_char = 2
            prefix = exact_term[0]
        return prefix+'"'+exact_term[first_char:-1].replace(r"\'", r'\"')+'"'
    else:
        return exact_term[0]+'"'+exact_term[1:]+'"'


def check_inchi(term_dict: dict, term_is_inchi_key=False):
    try:
        chembl_ids = []
        response = requests.get(
            '{es_url}/{index_prefix}molecule/_search'.format(
                es_url=ELASTICSEARCH_EXTERNAL_URL,
                index_prefix=CHEMBL_ES_INDEX_PREFIX
            ),
            json=
            {
                'size': 10,
                '_source': 'molecule_chembl_id',
                'query': {
                    'term': {
                        'molecule_structures.standard_inchi'+('_key' if term_is_inchi_key else ''): {
                            'value': term_dict['term']
                        }
                    }
                }
            },
            timeout=5
        )
        json_response = response.json()
        for hit_i in json_response['hits']['hits']:
            chembl_ids.append(hit_i['_source']['molecule_chembl_id'])
        if chembl_ids:
            term_dict['references'].append(
                {
                    'type': 'inchi'+('_key' if term_is_inchi_key else ''),
                    'label': 'InChI'+(' Key' if term_is_inchi_key else ''),
                    'chembl_ids': get_chembl_id_list_dict(chembl_ids),
                    'include_in_query': True,
                    'chembl_entity': 'compound'
                }
            )
    except:
        traceback.print_exc()


def check_unichem(term_dict: dict):
    pass

def get_chembl_id_dict(chembl_id, cross_references=[], include_in_query=True, score=None):
    return {
        'chembl_id': chembl_id,
        'cross_references': cross_references,
        'include_in_query': include_in_query,
        'score': score
    }

def get_chembl_id_list_dict(chembl_ids, cross_references=[], include_in_query=True):
    return [
        get_chembl_id_dict(
            chembl_id_i,
            cross_references[i] if i < len(cross_references) else [],
            include_in_query
        )
        for i, chembl_id_i in enumerate(chembl_ids)
    ]

def check_smiles(term_dict: dict):

    ws_base_path = RUN_CONFIG.get('chembl_api').get('ws_url')
    try:
        chembl_ids = []
        next_url_path = '{ws_path}/molecule.json?molecule_structures__canonical_smiles__flexmatch={smiles}'\
                        .format(ws_path=ws_base_path, smiles=urllib.parse.quote(term_dict['term']))
        while next_url_path:
            response = requests.get(
                WS_DOMAIN + next_url_path,
                headers={'Accept': 'application/json'},
                timeout=5
            )
            json_response = response.json()
            if 'error_message' in json_response:
                return None
            for molecule_i in json_response['molecules']:
                chembl_ids.append(molecule_i['molecule_chembl_id'])
            next_url_path = json_response['page_meta']['next']
        if chembl_ids:
            term_dict['references'].append(
                {
                    'type': 'smiles',
                    'label': 'SMILES',
                    'chembl_ids': get_chembl_id_list_dict(chembl_ids),
                    'include_in_query': True,
                    'chembl_entity': 'compound'
                }
            )
    except:
        traceback.print_exc()


class TermsVisitor(PTNodeVisitor):

    def __init__(self):
        super().__init__()

    def visit__default__(self, node, children):
        """
        Called if no visit method is defined for the node.

        Args:
            node(ParseTreeNode):
            children(processed children ParseTreeNode-s):
        """
        if isinstance(node, arpeggio.Terminal):
            return arpeggio.text(node)
        else:
            # term = ''.join([str(child_i) for child_i in children])
            # check_unichem(term)
            return ''.join([str(child_i) for child_i in children])

    def visit_expression_term(self, node, children):
        return children[0]

    def visit_parenthesised_expression(self, node, children):
        return children[1]

    def visit_expression(self, node, children):
        exp = {'or': []}
        previous_single_term_lc = None
        for child_i in children:
            str_child_i_lc = str(child_i).strip().lower()
            term_dict = None
            if len(str_child_i_lc) > 0:

                if str_child_i_lc == 'and' or str_child_i_lc == 'or':
                    term_dict = self.get_term_dict(str(child_i).strip(), include_in_query=False)
                    check_unichem(term_dict)
                last_term_is_and_group = len(exp['or']) > 0 and type(exp['or'][-1]) == dict and 'and' in exp['or'][-1]
                if str_child_i_lc == 'and' and not last_term_is_and_group:
                    if len(exp['or']) > 0:
                        exp['or'][-1] = {'and': [exp['or'][-1], term_dict]}
                    else:
                        exp['or'].append({'and': [term_dict]})
                elif last_term_is_and_group and (str_child_i_lc == 'and' or previous_single_term_lc == 'and'):
                    if term_dict:
                        exp['or'][-1]['and'].append(term_dict)
                    else:
                        exp['or'][-1]['and'].append(child_i)
                else:
                    if term_dict:
                        exp['or'].append(term_dict)
                    else:
                        exp['or'].append(child_i)
                previous_single_term_lc = str_child_i_lc
        if len(exp['or']) == 1:
            return exp['or'][0]
        return exp

    @staticmethod
    def get_term_dict(term: str, include_in_query=True) -> dict:
        return {
            'term': term,
            'include_in_query': include_in_query,
            'references': [],
            'exact_match_term': False,
            'filter_term': False,
            'chembl_entity': None
        }

    def visit_smiles(self, node, children):
        term = ''.join(children)
        include_in_query = len(term) <= 4
        term_dict = self.get_term_dict(term, include_in_query=include_in_query)
        check_smiles(term_dict)
        if include_in_query:
            check_unichem(term_dict)
        if inchi.is_inchi_key(term):
            check_inchi(term_dict)
        return term_dict

    def visit_inchi(self, node, children):
        term = ''.join(children)
        term_dict = self.get_term_dict(term, include_in_query=False)
        check_inchi(term_dict)
        return term_dict

    def visit_inchi_key(self, node, children):
        term = ''.join(children)
        term_dict = self.get_term_dict(term, include_in_query=False)
        check_inchi(term_dict, term_is_inchi_key=True)
        return term_dict

    def visit_fasta(self, node, children):
        term = ''.join(children)
        term_dict = self.get_term_dict(term, include_in_query=False)
        # check_fasta(term_dict)
        return term_dict

    def visit_property_term(self, node, children):
        term = ''.join(children)
        term_dict = self.get_term_dict(term)
        term_dict['filter_term'] = True
        return term_dict

    def visit_exact_match_term(self, node, children):
        term = ''.join(children)
        term = adjust_exact_term(term)
        term_dict = self.get_term_dict(term)
        term_dict['exact_match_term'] = True
        return term_dict

    def visit_single_term(self, node, children):
        term = ''.join(children)
        term_lc = term.lower()
        if term_lc == 'or' or term_lc == 'and':
            return term
        term_dict = self.get_term_dict(term)
        check_unichem(term_dict)
        check_chembl(term_dict)
        check_integer(term_dict)
        check_doi(term_dict)
        check_chembl_entities(term_dict)
        return term_dict

TERMS_VISITOR = TermsVisitor()