#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo <yoann.sculo@gmail.com>'
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import sys
import datetime
import codecs
import html2text
import requests

from optparse import OptionParser
from xml.dom import minidom
import utilities

reload(sys)
sys.setdefaultencoding("utf-8")

class Jobboard():

    dlDir = "./dl"

    def load(self, file):
        ""

    def fetch(self):
        ""

    def processOffers(self):
        ""

class Location():

    lon = "0"
    lat = "0"

    def loadFromAddress(self, address):
        r = requests.get("http://nominatim.openstreetmap.org/search",
                params={'q': address,
                        'format':'xml',
                        'polygon': 0,
                        'addressdetails': 1})
        if (r.status_code != 200):
            return

        xmldoc = minidom.parseString(r.content)
        if (xmldoc.getElementsByTagName('place').length <= 0):
            return

        res = xmldoc.getElementsByTagName('place')[0]
        self.lat = res.getAttribute('lat')
        self.lon = res.getAttribute('lon')

class Offer():
    def load(self, src, ref, date_pub, date_add, title, company, contract, location, lat, lon, salary, url, content):
        self.src = src
        self.ref = ref

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title.encode("utf-8")
        self.company = company.encode("utf-8")
        self.contract = contract.encode("utf-8")
        self.location = location.encode("utf-8")
        self.salary = salary.encode("utf-8")
        self.url = url.encode("utf-8")
        self.content = content.encode("utf-8")

    def loadFromHtml(self, filename):
        ""

    def add_db(self):
        return utilities.db_add_offer(self)

    def printElt(self):
        #print "Title :" + self.title
        print "Company : " + self.company

    #def set_from_row(row):
    #    self.src = row[0]
    #    self.ref = row[1]
    #    self.date_pub = datetime.datetime.fromtimestamp(int(row[2]))
    #    self.date_add = datetime.datetime.fromtimestamp(int(row[3]))
    #    self.title = row[4].encode("utf-8")
    #    self.company = row[5].encode("utf-8")
    #    self.contract = row[6].encode("utf-8")
    #    self.location = row[7].encode("utf-8")
    #    self.salary = row[8].encode("utf-8")
    #    self.url = row[9].encode("utf-8")
    #    self.content = row[10].encode("utf-8")


class JobCatcher():

    jobBoardList = []

    def load_jobBoards(self):
        """ load all jobboards from jobboards directory
        """
        import glob
        import importlib

        for file in glob.glob("./jobboards/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if (name == '__init__'):
                continue

            module = importlib.import_module('jobboards.'+name);
            moduleClass = getattr(module, name)
            instance = moduleClass()
            self.jobBoardList.append(instance)

    def run(self):
        for item in self.jobBoardList:
            item.fetch()

if __name__ == '__main__':
    parser = OptionParser(usage = 'syntax: %prog [options] <from> [to]')
    args = sys.argv[1:]

    parser.set_defaults(version = False)
    parser.add_option('-v', '--version',
                          action = 'store_true', dest = 'version',
                          help = 'Output version information and exit')
    parser.add_option('-r', '--report',
                          action = 'store_true', dest = 'report',
                          help = 'Generate a full report')
    parser.add_option('-a', '--add',
                          action = 'store_true', dest = 'add',
                          help = 'add an offer')
    parser.add_option('-c', '--create',
                          action = 'store_true', dest = 'create',
                          help = 'create the databse')
    parser.add_option('-s', '--start',
                          action = 'store_true', dest = 'start',
                          help = 'start the fetch')
    parser.add_option('-b', '--blocklist',
                          action = 'store_true', dest = 'blocklist',
                          help = 'update blocklist')

    (options, args) = parser.parse_args(args)

    if options.version:
        print 'jobcatcher version %s - %s (%s)' % (__version__,
                                                __copyright__,
                                                __license__)
        sys.exit(0)

    if options.report:
        print "Report generation..."
        utilities.report_generate(True)
        utilities.report_generate(False)
        print "Done."
        sys.exit(0)

    if options.add:
        if len(args) == 11:
            print "%s" % args[10]
            offer = Offer()
            offer.load(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7], args[8], args[9], args[10])
            db_add_offer(offer)

        sys.exit(0)

    if options.create:
        db_create()
        sys.exit(0)

    # TODO : change to "run"
    if options.start:
        bot = JobCatcher()
        bot.load_jobBoards()
        bot.run()
        sys.exit(0)

    if options.blocklist:
        utilities.blocklist_load();
        sys.exit(0)

