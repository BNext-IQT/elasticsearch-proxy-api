"""
Moudle that sets up the Appreggio parser
"""
from arpeggio import ParserPython, Optional, PTNodeVisitor, OneOrMore, ZeroOrMore, EOF
from arpeggio import RegExMatch as _

from app.free_text_parsing.grammar import common
from app.free_text_parsing.grammar import smiles
from app.free_text_parsing.grammar import inchi
from app.free_text_parsing.grammar import fasta


def single_term():
    return common.correctly_parenthesised_non_space_char_sequence, common.term_end_lookahead


def exact_match_term():
    return (
        [
            (
                Optional(['+', '-']),
                [
                    ('"', _(r'((\\")|[^"])+'), '"'),
                    ("'", _(r"((\\')|[^'])+"), "'")
                ]
            ),
            (
                ['+', '-'], common.correctly_parenthesised_non_space_char_sequence
            )
        ],
        common.term_end_lookahead
    )


def json_property_path_segment():
    return OneOrMore(_(r'[a-z0-9_\-]'))


def property_term():
    return (
        Optional(['+', '-']),
        json_property_path_segment, ZeroOrMore('.', json_property_path_segment), ':',
        [
            ('"', _('[^"]+'), '"'),
            ("'", _("[^']+"), "'"),
            ("(", _("[^\(\)]+"), ")"),
            common.correctly_parenthesised_non_space_char_sequence
        ],
        common.term_end_lookahead
    )


def parenthesised_expression():
    return '(', expression, ')', common.term_end_lookahead


def expression_term():
    return [parenthesised_expression,
            smiles.smiles,
            inchi.inchi_key, inchi.inchi,
            fasta.fasta,
            property_term,
            exact_match_term,
            single_term]


def expression():
    """
    :return:
    """

    return \
        (
            Optional(common.space_sequence),
            expression_term,
            ZeroOrMore(
                # Optional(
                #     (common.space_sequence, _(r'and|or', ignore_case=True))
                # ),
                common.space_sequence,
                expression_term,
                common.term_end_lookahead
            ),
            Optional(common.space_sequence)
        )


PARSER = ParserPython(expression, skipws=False)
