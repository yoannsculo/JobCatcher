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
import glob
import datetime
import codecs
import html2text
import requests
import unittest

from optparse import OptionParser
from xml.dom import minidom
import utilities
import sqlite3 as lite

reload(sys)
sys.setdefaultencoding("utf-8")

from config import configstest as configs
import jobcatcher

class TestPackages(unittest.TestCase):

    def setUp(self):
        """Before unittest"""
        pass

    def test_JBEures(self):
        """ Test Eures jobboard"""

        # Get feed content
        plugin = utilities.loadJobBoard('Eures', configs)
        url = configs['Eures']['feeds'][0]
        filename = plugin.downloadFeed(url)
        self.assertEqual(filename, '/tmp/dl/Eures/feeds/0855c939d3b5b5cd1fffeb1665dcecfc.feed')

        # Check if URL is parsed
        urls = plugin.getUrls()
        self.assertEqual(len(urls), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
