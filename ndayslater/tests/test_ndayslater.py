import unittest
from ndayslater.ndayslater import get_config_parser, run, NDaysLaterIMAPClient


class TestCase(unittest.TestCase):

    def test_ndayslater(self):
        config_parser=get_config_parser()
        args=config_parser.parse_args(['-o', 'localhost', '-u', 'imaptest', '-p', 'imaptest', '--no-ssl', '-v'])
        run(args)

    def test_pycharm_completition(self):
        client=NDaysLaterIMAPClient()
        run=client
