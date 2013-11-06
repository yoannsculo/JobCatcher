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


from optparse import OptionParser
from xml.dom import minidom
import utilities
import sqlite3 as lite

reload(sys)
sys.setdefaultencoding("utf-8")

from config import configs

# For testing
# rm jobs.db; python jobcatcher.py -a

class JobBoards(object):
    """A class for dowload a feed or a HTML page"""

    def __init__(self, configs=[]):
        self._configs = configs
        self._rootdir = configs['global']['rootdir']

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value


    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    def downloadFeeds(self, forcedownload=False):
        """Download all feeds or HTMLs pages"""
        for jobboardname in self._configs:
            if jobboardname not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[jobboardname]:
                    feeds = self._configs[jobboardname]['feeds']

                    # Donwload all feeds for jobboard
                    plugin = utilities.loadJobBoard(jobboardname, configs)
                    for url in feeds:
                        plugin.downloadFeed(url)

    def analyzesPages(self):
        """Analyze downloaded pages"""
        for jobboardname in self._configs:
            if jobboardname not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[jobboardname]:
                    destdir = "%s/%s/pages" % (self.rootdir, jobboardname)
                    plugin = utilities.loadJobBoard(jobboardname, configs)
                    for p in glob.glob("%s/*.page" % destdir):
                        # Load the HTML feed
                        content = utilities.openPage(p)
                        plugin.analyzePage(content.url, content.page)

    def moveToOffers(self):
        """Move jobboards datas to offer"""
        for jobboardname in self._configs:
            if jobboardname not in self._configs['global']['ignorejobboard']:
                if 'feeds' in self._configs[jobboardname]:
                    plugin = utilities.loadJobBoard(jobboardname, configs)
                    plugin.moveToOffers()

class JobBoard(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=[], interval=1200):
        self._rootdir = configs['global']['rootdir']
        self._configs = configs
        self._interval = interval
        self._datas = {}
        self._processingDir = "%s/%s" % (
            self.rootdir,
            self.name
        )

        #Check and create Jobboard table
        if not self.isTableCreated():
            self.createTable()

    @property
    def name(self):
        """Get JobBoard name"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def datas(self):
        """JobBoard datas"""
        return self._datas

    @datas.setter
    def datas(self, value):
        self._datas = value

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    @property
    def interval(self):
        """Get interval in minute"""
        return self._interval

    @interval.setter  
    def interval(self, value):
        """Set interval in minute"""
        self._interval = value

    def isTableCreated(self):
        """Check if the table for jobboard exist"""
        return utilities.db_istableexists("jb_%s" % self.name)

    def downloadFeed(self, url, interval=1200, forcedownload=False):
        """Download a feed or a HTML page"""

        feeddir = "%s/feeds" % self._processingDir
        urlid = utilities.md5(url)
        saveto = "%s/%s.feed" % (feeddir, urlid)
        utilities.downloadFile(url, saveto, interval)

    def downloadPages(self, jobboardname, urls):
        """Download all pages from urls list"""
        destdir = "%s/%s/pages" % (self.rootdir, jobboardname)

        for u in urls:
            md5 = utilities.md5(u)
            saveto = "%s/%s.page" % (destdir, md5)
            utilities.downloadFile(u, saveto, self._interval)

    def getAllJBDatas(self):
        """Get all jobboard datas"""
        conn = lite.connect("jobs.db")
        conn.row_factory = lite.Row
        cursor = conn.cursor()

        sql = "SELECT * FROM jb_%s" % self.name

        cursor.execute(sql)
        datas = cursor.fetchall()

        return datas

    def moveToOffers(self):
        datas = self.getAllJBDatas()
        for d in datas:
            o = self.createOffer(d)
            if o:
                utilities.db_add_offer(o)

    def createTable(self,):
        """Create Jobboard table"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def getUrls(self):
        """Get Urls offers from feed"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def analyzePage(self, url, html):
        """Analyze page and extract datas"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def insertToJBTable(self):
        """Insert to jobboard offer into table"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def createOffer(self, data):
        """Create Offer object with jobboard data"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def fetchAllOffersFromDB(self):
        conn = lite.connect("jobs.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM offers WHERE source='%s' ORDER BY date_pub DESC" %(self.name)
        cursor.execute(sql)
        data = cursor.fetchall()
        return data


class ReportGenerator(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=[]):
        self._wwwdir = configs['global']['wwwdir']
        self._configs = configs

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value


    def generate(self):
        self.generateReport(True)
        self.generateReport(False)
        self.generateStatistics()


    def generateStatistics(self):
        html_dir = self.wwwdir

        conn = lite.connect("jobs.db")
        cursor = conn.cursor()

        stat = open(os.path.join(html_dir, 'statistics.html'), 'w')
        stat.write("<html><head>")
        stat.write("<link href=\"./bootstrap.css\" rel=\"stylesheet\">")
        stat.write("<link href=\"./bootstrap-responsive.css\" rel=\"stylesheet\">")
        stat.write("<style>table{font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>")
        stat.write("<meta http-equiv=\"Content-type\" content=\"text/html\"; charset=\"utf-8\"></head>")
        stat.write("<body>")

        stat.write("<table class=\"table table-condensed\">")
        stat.write("<thead>")
        stat.write("<tr>")
        stat.write("<th>JobBoard</th>")
        stat.write("<th>Total Offers</th>")
        stat.write("<th>Offers not from blacklist</th>")
        stat.write("<th>Offers from blacklist</th>")
        stat.write("</tr>")
        stat.write("</thead>")

        jb = JobCatcher()
        jb.loadPlugins()
        for item in jb.jobBoardList:
            data = item.fetchAllOffersFromDB()
            stat.write("<tr>")
            stat.write("<td>%s</td>" %(item.name))
            stat.write("<td>%s</td>" %(len(data)))
            stat.write("<td></td>")
            stat.write("<td></td>")
            stat.write("</tr>")

        stat.write("</table>")
        stat.write("</html>")
        stat.close()

    def generateReport(self, filtered=True):

        html_dir = self.wwwdir

        conn = lite.connect("jobs.db")
        cursor = conn.cursor()

        sql_filtered = "SELECT * FROM offers WHERE company not IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"
        sql_full = "SELECT * FROM offers ORDER BY date_pub DESC"

        cursor.execute(sql_filtered)
        data_filtered = cursor.fetchall()
        count_filtered = len(data_filtered)

        cursor.execute(sql_full)
        data_full = cursor.fetchall()
        count_full = len(data_full)

        if (filtered):
            report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
            data = data_filtered
        else:
            report = open(os.path.join(html_dir, 'report_full.html'), 'w')
            data = data_full

        report.write("<html><head>")
        report.write("<link href=\"./bootstrap.css\" rel=\"stylesheet\">")
        report.write("<link href=\"./bootstrap-responsive.css\" rel=\"stylesheet\">")
        report.write("<style>table{font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>")
        report.write("<meta http-equiv=\"Content-type\" content=\"text/html\"; charset=\"utf-8\"></head>")
        report.write("<body>")

        report.write("<center><p><a href=\"report_filtered.html\">%s filtered offers (%.2f%%)</a>" %(count_filtered, 100*(float)(count_filtered)/count_full))
        report.write(" - %s blacklisted offers (%.2f%%)" %(count_full-count_filtered, 100*(float)(count_full-count_filtered)/count_full) )
        report.write(" - <a href=\"report_full.html\">All %s offers</a>" %(count_full) )
        report.write(" - <a href=\"statistics.html\">Statistics</a></p></center>" )

        report.write("<table class=\"table table-condensed\">")
        report.write("<thead>")
        report.write("<tr>")
        report.write("<th>Pubdate</th>")
        report.write("<th>Type</th>")
        report.write("<th>Title</th>")
        report.write("<th>Company</th>")
        report.write("<th>Location</th>")
        report.write("<th>Contract</th>")
        report.write("<th>Salary</th>")
        report.write("<th>Source</th>")
        report.write("</tr>")
        report.write("</thead>")

        s_date = ''

        for row in data:
            offer = Offer()
            offer.load(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12])

            if (s_date != offer.date_pub.strftime('%Y-%m-%d')):
                s_date = offer.date_pub.strftime('%Y-%m-%d')
                report.write('<tr class=\"error\">');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('<td></td>');
                report.write('</tr>');

            report.write("<tr>")
            report.write('<td>' + offer.date_pub.strftime('%Y-%m-%d') + '</a></td>')
            report.write('<td><span class="label label-success">noSSII</span></td>')
            report.write('<td><a href="'+offer.url+'">' + offer.title + '</a></td>')
            report.write('<td>' + offer.company + '</td>')
            report.write('<td>' + offer.location + '</td>')
            #report.write('<td><span class="label label-important">SSII</span></td>')

            if (offer.contract == ur'CDI' or offer.contract == ur'CDI (Cab/recrut)'):
                report.write('<td><span class="label label-success">'+ offer.contract +'</span></td>')
            elif (offer.contract[:3] == ur'CDD'):
                report.write('<td><span class="label label-warning">'+ offer.contract +'</span></td>')
            else:
                report.write('<td><span class="label">'+ offer.contract +'</span></td>')

            report.write('<td>' + offer.salary + '</td>')
            report.write('<td>' + offer.src + '</td>')
            report.write("</tr>")
        report.write("</table></body></html>")
        report.close()


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
    def __init__(self):
        self.ref = u""
        self.title = u""
        self.company = u""
        self.contract = u""
        self.location = u""
        self.salary = u""
        self.url = u""
        self.content = u""
        self.date_add = u""
        self.date_pub = u""
        self.lat = u""
        self.lon = u""

    def load(
            self, src, ref, date_pub, date_add, title, company,
            contract, location, lat, lon, salary, url, content
    ):

        self.src = src
        self.ref = ref

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title
        self.company = company
        self.contract = contract
        self.location = location
        self.salary = salary
        self.url = url
        self.content = content

    def loadFromHtml(self, filename):
        ""

    def cleanContract(self):
        self.contract = utilities.filter_contract_fr(self.contract)
        return

    def cleanLocation(self):
        self.location = utilities.filter_location_fr(self.location)
        return

    def cleanSalary(self):
        self.salary = utilities.filter_salary_fr(self.salary)
        return

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

    def loadPlugins(self):
        """ load all jobboards from jobboards directory
        """

        for file in glob.glob("./jobboards/*.py"):
            name = os.path.splitext(os.path.basename(file))[0]
            if name != "Eures":
                continue
            if (name == '__init__'):
                continue

            plugin = utilities.loadJobBoard(name, configs)
            self.jobBoardList.append(plugin)

    def run(self):
        for jobboard in self.jobBoardList:
            if jobboard.name not in configs['global']['ignorejobboard']:
                if jobboard.name != "Eures":
                    continue

                print ""
                print "=================================="
                print jobboard.name
                print "=================================="

                jb = utilities.loadJobBoard(jobboard.name, configs)
                urls = jb.getUrls()
                jb.downloadPages(jobboard.name, urls)


def generatereport():
    r = ReportGenerator(configs)
    r.generate()


def initblacklist():
    utilities.db_checkandcreate()
    utilities.blacklist_flush()
    utilities.blocklist_load()


def feeddownload():
    fd = JobBoards(configs)
    fd.downloadFeeds()


def pagesdownload():
    bot = JobCatcher()
    bot.loadPlugins()
    bot.run()


def pagesinsert():
    utilities.db_checkandcreate()
    fd = JobBoards(configs)
    fd.analyzesPages()


def pagesmove():
    utilities.db_checkandcreate()
    fd = JobBoards(configs)
    fd.moveToOffers()

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
    parser.add_option('-a', '--all',
                          action = 'store_true', dest = 'all',
                          help = 'Sync the blacklist, fetch the offers and generates reports.')
    parser.add_option('-c', '--create',
                          action = 'store_true', dest = 'create',
                          help = 'create the databse')
    parser.add_option('-s', '--start',
                          action = 'store_true', dest = 'start',
                          help = 'start the fetch')
    parser.add_option('-p', '--pages',
                          action = 'store_true', dest = 'pages',
                          help = 'Pages download')
    parser.add_option('-i', '--insert',
                          action = 'store_true', dest = 'insert',
                          help = 'Insert pages')
    parser.add_option('-m', '--move',
                          action = 'store_true', dest = 'move',
                          help = 'Move datas to offer')
    # parser.add_option('-b', '--blocklist',
    #                       action = 'store_true', dest = 'blocklist',
    #                       help = 'update blocklist')
    parser.add_option('-u', '--url',
                          action = 'store_true', dest = 'url',
                          help = 'analyse an url')
    parser.add_option('-f', '--flush',
                          action = 'store_true', dest = 'flush',
                          help = 'flush the blacklist and update it.')

    (options, args) = parser.parse_args(args)

    if options.version:
        print 'jobcatcher version %s - %s (%s)' % (__version__,
                                                __copyright__,
                                                __license__)
        sys.exit(0)

    if options.report:
        print "Report generation..."
        generatereport()
        print "Done."
        sys.exit(0)

    if options.all:
        initblacklist()
        feeddownload()
        pagesdownload()
        pagesinsert()
        pagesmove()
        generatereport()
        sys.exit(0)

    if options.url:
        if len(args) != 1:
            print "error"
        else:
            import importlib
            module = importlib.import_module('jobboards.Apec');
            moduleClass = getattr(module, 'Apec')
            instance = moduleClass()
            filename = instance.fetch_offer(args[0])
            instance.processOffer(filename)
        sys.exit(0)

    if options.start:
        print "Try to load a feed"
        feeddownload()
        print "Done."
        sys.exit(0)

    if options.pages:
        pagesdownload()
        sys.exit(0)

    if options.insert:
        pagesinsert()
        sys.exit(0)

    if options.move:
        pagesmove()
        sys.exit(0)

    if options.blocklist:
        utilities.blocklist_load();
        sys.exit(0)

    if options.flush:
        initblacklist()
        sys.exit(0)
