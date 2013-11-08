#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

import os
import sys
import unittest
import utilities
from config import configstest as configs


class TestPackages(unittest.TestCase):

    def setUp(self):
        """Test & Create database"""
        # Remove exist database
        if os.path.isfile(configs['global']['database']):
            os.remove(configs['global']['database'])

        # Check if database not exist
        exists = utilities.db_istableexists(configs, 'offers')
        self.assertEqual(exists, False)

        # Create database & check
        utilities.db_create(configs)
        exists = utilities.db_istableexists(configs, 'offers')
        self.assertEqual(exists, True)

    def test_JBEures(self):
        """ Test Eures jobboard"""

        # Jobboardname
        jobboard = 'Eures'

        # Get feed content
        plugin = utilities.loadJobBoard(jobboard, configs)
        url = configs[jobboard]['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(filename, '/tmp/dl/Eures/feeds/0855c939d3b5b5cd1fffeb1665dcecfc.feed')

        # Dowload page
        jb = utilities.loadJobBoard(jobboard, configs)
        urls = jb.getUrls()
        self.assertEqual(len(urls), 5)
        jb.downloadPages(jobboard, urls)

    def test_JBApec(self):
        """ Test Apec jobboard"""

        # Jobboardname
        jobboard = 'Apec'

        # Get feed content
        plugin = utilities.loadJobBoard(jobboard, configs)
        url = configs[jobboard]['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(filename, '/tmp/dl/Apec/feeds/17a63531332158f5b8204dadc24efcb4.feed')

        # Dowload page
        jb = utilities.loadJobBoard(jobboard, configs)
        urls = jb.getUrls()
        self.assertEqual(len(urls), 30)
        jb.downloadPages(jobboard, urls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
