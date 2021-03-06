"""
Module that tests the grammar
"""
import unittest

from arpeggio import ParserPython

from app.free_text_parsing.grammar.test import utils
from app.free_text_parsing.grammar import smiles
from app.free_text_parsing.grammar import inchi
from app.free_text_parsing.grammar import fasta


class GrammarTester(unittest.TestCase):

    def setUp(self):
        print('Running Test: {0}'.format(self._testMethodName))

    def tearDown(self):
        print('Test {0}'.format('Passed!' if self._outcome.success else 'Failed!'))

    def try_parse_failure(self, parser: ParserPython, text_to_parse: str):
        # noinspection PyBroadException
        try:
            parser.parse(text_to_parse)
            self.fail("Should not parse {0} using the {1} parser!".format(text_to_parse, parser.__class__))
        except:
            pass

    def try_parsing(self, parser: ParserPython, text_to_parse: str):
        # noinspection PyBroadException
        try:
            parser.parse(text_to_parse)
        except:
            self.fail("Could not parse {0} using the {1} parser!".format(text_to_parse, parser.__class__))

    # ------------------------------------------------------------------------------------------------------------------
    # Simple Grammars Tests
    # ------------------------------------------------------------------------------------------------------------------

    def test_smiles_parsing(self):
        # noinspection PyBroadException
        try:
            parser = ParserPython(smiles.smiles, skipws=False)
        except:
            self.fail("Could not instantiate the SMILES parser!")
        if parser:
            for smiles_i in utils.SMILES_EXAMPLES:
                self.try_parsing(parser, smiles_i)
            for non_smiles_i in utils.NON_SMILES_EXAMPLES:
                self.try_parse_failure(parser, non_smiles_i)

    def test_inchi_parsing(self):
        # noinspection PyBroadException
        try:
            parser = ParserPython(inchi.inchi, skipws=False)
        except:
            self.fail("Could not instantiate the InChI parser!")
        if parser:
            for inchi_i in utils.INCHI_EXAMPLES:
                self.try_parsing(parser, inchi_i)

    def test_inchi_key_parsing(self):
        # noinspection PyBroadException
        try:
            parser = ParserPython(inchi.inchi_key, skipws=False)
        except:
            self.fail("Could not instantiate the InChI KEY parser!")
        if parser:
            for inchi_key_i in utils.INCHI_KEY_EXAMPLES:
                self.try_parsing(parser, inchi_key_i)

    def test_fasta_parsing(self):
        # noinspection PyBroadException
        try:
            parser = ParserPython(fasta.fasta, skipws=False)
        except:
            self.fail("Could not instantiate the FASTA parser!")
        if parser:
            for fasta_sequence_i in utils.FASTA_SAMPLES:
                self.try_parsing(parser, fasta_sequence_i)

    # ------------------------------------------------------------------------------------------------------------------
    # Simple Grammars Tests
    # ------------------------------------------------------------------------------------------------------------------

    def test_parenthesization(self):
        pass
