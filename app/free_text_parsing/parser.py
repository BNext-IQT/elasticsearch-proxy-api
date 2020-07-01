"""
Moudle that sets up the Appreggio parser
"""
from arpeggio import ParserPython, Optional, PTNodeVisitor, OneOrMore, ZeroOrMore, EOF

# import glados.grammar.common as common
#
# def expression():
#     """
#     :return:
#     """
#
#     return \
#         (
#             Optional(common.space_sequence),
#             expression_term,
#             ZeroOrMore(
#                 # Optional(
#                 #     (common.space_sequence, _(r'and|or', ignore_case=True))
#                 # ),
#                 common.space_sequence,
#                 expression_term,
#                 common.term_end_lookahead
#             ),
#             Optional(common.space_sequence)
#         )
#
#
# PARSER = ParserPython(expression, skipws=False)
