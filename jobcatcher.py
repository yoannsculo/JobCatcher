#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Yoann Sculo <yoann.sculo@gmail.com>',
    'Bruno Adelé <bruno@adele.im>',
    'Yankel Scialom <yankel.scialom@mail.com>'
]
__copyright__ = 'Copyright (C) 2013 Yoann Sculo'
__license__ = 'GPLv2'
__version__ = '1.0'

import os
import re
import sys
import glob
import codecs
import datetime
import requests
import importlib
import pprint

from optparse import OptionParser
from xml.dom import minidom
import utilities
import sqlite3 as lite

reload(sys)
sys.setdefaultencoding("utf-8")


class JobBoard(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=None, interval=3600):
        self._rootdir = configs.globals['rootdir']
        self._configs = configs
        self._interval = interval
        self._datas = {}
        self._processingDir = "%s/%s" % (
            self.rootdir,
            self.name
        )
        self._encoding = {'feed': 'utf-8', 'page': 'utf-8'}

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
    def encoding(self):
        return self._encoding

    @encoding.setter  
    def encoding(self, value):
        self._encoding = value

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
        return utilities.db_istableexists(self.configs.globals, "jb_%s" % self.name)

    def downloadFeed(self, feed, interval=3600, forcedownload=False):
        """Download feed from jobboard"""
        datas = None
        if 'datas' in feed:
            datas = feed['datas']

        saveto = utilities.getFeedDestination(
            self.rootdir, self.name, feed['url'], datas
        )
        utilities.downloadFile(feed['url'], datas, saveto, True, interval)

        return saveto

    def downloadFeeds(self, feeds, interval=3600, forcedownload=False):
        """Download a feeds from jobboard"""
        for feed in feeds:
            self.downloadFeed(feed, interval, forcedownload)

    def downloadPage(self, feedid, url):
        """Download pages from url"""
        saveto = utilities.getPageDestination(
            self.rootdir, self.name, feedid, url, None
        )
        try:
            utilities.downloadFile(url, None, saveto, True, self._interval)
        except UnicodeDecodeError:
            pass

        return saveto

    def downloadPages(self, urls):
        """Download all pages from urls list"""
        for feedid, url in urls:
            self.downloadPage(feedid, url)

    def getAllJBDatas(self):
        """Get all jobboard datas"""
        conn = lite.connect(self.configs.globals['database'])
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
                o.cleanFields()
                utilities.db_add_offer(self.configs.globals, o)

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
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()
        sql = "SELECT * FROM offers WHERE source='%s' ORDER BY date_pub DESC" %(self.name)
        cursor.execute(sql)
        data = cursor.fetchall()
        return data


class Page(object):
    """A page class"""
    def __init__(self, configs=[], jobboardname="", feedid="", pagename=""):
        self._wwwdir = configs.globals['wwwdir']
        self._p2pdir = configs.globals['p2pdir']
        self._rootdir = configs.globals['rootdir']
        self._configs = configs
        # Page information
        self._downloaded = False
        self._jobboardname = jobboardname
        self._feedid = feedid
        self._pagename = pagename
        self._pageid = ""
        self._url = ""
        self._content = ""

    def _extractFeedidFromFilename(self, filename):
        feedid = None
        m = re.match(r'.*/pages/([a-z0-9]+)/(.*\.page)', filename)
        if m:
            feedid = m.group(1)

        return feedid

    def load(self):
        filename = "%s/%s/pages/%s/%s" % (
            self.rootdir,
            self.jobboardname,
            self.feedid,
            self.pagename
        )
        webpage = utilities.openPage(filename)
        self._feedid = self._extractFeedidFromFilename(filename)
        self._pageid = webpage.pageid
        self._url = webpage.url
        self._content = webpage.content
        self._downloaded = True

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value


    @property
    def p2pdir(self):
        return self._p2pdir

    @p2pdir.setter  
    def p2pdir(self, value):
        self._p2pdir = value

    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    @property
    def jobboardname(self):
        return self._jobboardname

    @property
    def feedid(self):
        return self._feedid

    @property
    def pagename(self):
        return self._pagename

    @property
    def pageid(self):
        return self._pageid

    @property
    def url(self):
        return self._url

    @property
    def content(self):
        return self._content

    @property
    def downloaded(self):
        return self._downloaded

class Pages(object):
    """Download jobboard via static P2P"""
    def __init__(self, configs=[]):
        self._wwwdir = configs.globals['wwwdir']
        self._p2pdir = configs.globals['p2pdir']
        self._rootdir = configs.globals['rootdir']
        self._configs = configs
        self._pages = list()

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value


    @property
    def p2pdir(self):
        return self._p2pdir

    @p2pdir.setter  
    def p2pdir(self, value):
        self._p2pdir = value


    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    @property
    def pages(self):
        return self._pages

    def searchPagesForJobboard(self, jobboardname):
        srcdir = "%s/%s" % (self.configs.globals['rootdir'], jobboardname)
        files = utilities.findFiles(srcdir, '*.page')
        for f in files:
            m = re.match(r'.*/pages/([a-z0-9]+)/(.*\.page)', f)
            if m:
                feedid = m.group(1)
                pagename  = m.group(2)
                page = Page(self.configs, jobboardname, feedid, pagename)
                self._pages.append(page)


    def downloadPage(self, jobboardname):
        """Download a jobboard pages"""
        plugin = utilities.loadJobBoard(jobboardname, configs)
        urls = plugin.getUrls()
        plugin.downloadPages(urls)

    def downloadPages(self):
        """Download all jobboard pages"""
        jobboardlist = self.configs.getJobboardList()
        for jobboardname in jobboardlist:
            self.downloadPage(jobboardname)


class P2PDownloader(object):
    """Download jobboard via static P2P"""
    def __init__(self, configs=[]):
        self._wwwdir = configs.globals['wwwdir']
        self._p2pdir = configs.globals['p2pdir']
        self._rootdir = configs.globals['rootdir']
        self._configs = configs
        self._pages = dict()

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

    @property
    def rootdir(self):
        return self._rootdir

    @rootdir.setter  
    def rootdir(self, value):
        self._rootdir = value


    @property
    def p2pdir(self):
        return self._p2pdir

    @p2pdir.setter  
    def p2pdir(self, value):
        self._p2pdir = value


    @property
    def configs(self):
        return self._configs

    @configs.setter
    def configs(self, value):
        self._configs = value

    # def listServers(self):
    #     names = list()
    #     for name, url in self.configs.globals['p2pservers']:
    #         if 'name' in s:
    #             names.append(s['name'])

        return names

    def initcache(self):
        #p2plist = self.listServers()
        plugins = getjobboardlist(self.configs)

        for name, url in self.configs.globals['p2pservers'].iteritems():
            # Download feed ifnormations
            print 'Search for %s' % name
            destdir = "%s/%s" % (self.p2pdir, name)
            saveto = "%s/feeds.txt" % destdir
            utilities.downloadFile('%s/feeds.txt' % url, None, saveto, False)

            # Search pages for jobboards
            for jobboardname in plugins:
                saveto = "%s/%s.txt" % (destdir, jobboardname)
                page = utilities.downloadFile('%s/%s.txt' % (url, jobboardname), None, saveto, False)
                if page and page.statuscode == 200:
                    if name not in self._pages:
                        self._pages[name] = dict()
                    self._pages[name][jobboardname] = page.content.strip().split('\n')

    def sync(self):
        feeds = utilities.findFiles(self.rootdir, '*.feed')
        for i in range(len(feeds)):
            feeds[i] = re.sub(r'.*?/feeds/([a-z0-9]+)\.feed', r'\1', feeds[i])

        for p2psite, value in self._pages.iteritems():
            for jobboardname, value in self._pages[p2psite].iteritems():
                for u in self._pages[p2psite][jobboardname]:
                    feeddir = u.split('/')[0]
                    # Check if the url is in local feed
                    if feeddir in feeds:
                        local = "%s/%s/pages/%s" % (self.rootdir, jobboardname, u)
                        remote = "%s/dl/%s/pages/%s" % (
                            self.configs.globals['p2pservers'][p2psite],
                            jobboardname, u
                        )

                        if not os.path.exists(local):
                            utilities.downloadFile(remote, None, local, False)


class Config(object):
    """A class config"""
    def __init__(self):
        self._globals = None
        self._users = {}

    @property
    def globals(self):
        return self._globals

    @globals.setter
    def globals(self, value):
        self._globals = value

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, value):
        self._users = value

    def getUsers(self):
        """Get users list"""
        pos = -1

        # Search user config
        users = utilities.findFiles('./users', '*.py')
        for i in range(len(users)):
            if '__init__.py' in users[i]:
                pos = i
            users[i] = re.sub(r'.*/(.*?)\.py', r'\1', users[i])

        # Delete __init__.py
        if pos >= 0:
            del users[pos]

        return users

    def getFeedsInfo(self, users=None):
        """Get feeds list info"""
        feedslist = {}

        # Users
        if not users:
            users = self.getUsers()

        for u in users:
            for jobboardname in configs.users[u]:
                if 'feeds' in configs.users[u][jobboardname]:
                    for f in configs.users[u][jobboardname]['feeds']:
                        if 'datas' not in f:
                            f['datas'] = None
                        feedid = utilities.getEncodedURL(f['url'], f['datas'])
                        if jobboardname not in feedslist:
                            feedslist[jobboardname] = {}
                        if feedid not in feedslist[jobboardname]:
                            feedslist[jobboardname][feedid] = f

        return feedslist

    def getJobboardList(self, selecteduser=None):
        jobboardlist = []
        feedlist = self.getFeedsInfo(selecteduser)
        for jobboardname, feedinfo in feedlist.iteritems():
            if jobboardname not in jobboardlist:
                jobboardlist.append(jobboardname)

        return jobboardlist

    def addGlobalconfig(self, config):
        self.globals = config

    def addForUser(self, username, modulename):
        module = importlib.import_module(modulename)
        self._users[username] = module.configs

    def loadUsersConfig(self):
        users = self.getUsers()
        for u in users:
            self.addForUser(u, 'users.%s' % u)


class ReportGenerator(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=None):
        self._rootdir = configs.globals['rootdir']
        self._wwwdir = configs.globals['wwwdir']
        self._configs = configs

    @property
    def wwwdir(self):
        return self._wwwdir

    @wwwdir.setter  
    def wwwdir(self, value):
        self._wwwdir = value

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

    def generate(self):
        self.generateReport(True)
        self.generateReport(False)
        self.generateStatistics()
        self.generateDownloadedFile()

    def box(self, style, text):
        css = ""
        if style != "":
            css = " label-%s" % style

        return '<span class="label%s">%s</span>' % (css, text)

    def header(self, fhandle):
        fhandle.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        fhandle.write('<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">\n')
        fhandle.write('<head>\n')
        fhandle.write('\t<meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n')
        fhandle.write('\t<link rel="stylesheet" href="css/bootstrap.css" />\n')
        fhandle.write('\t<link rel="stylesheet" href="css/bootstrap-responsive.css" />\n')
        if self.configs.globals['report']['dynamic']:
            fhandle.write('\t<link rel="stylesheet" href="css/jquery-ui-1.10.3.custom.min.css" />\n')
            fhandle.write('\t<link rel="stylesheet" href="css/simplePagination.css" />\n')
            fhandle.write('\t<link rel="stylesheet" href="css/dynamic.css" />\n')
            fhandle.write('\t<script type="text/javascript" src="js/jquery-2.0.3.min.js"></script>\n')
            fhandle.write('\t<script type="text/javascript" src="js/jquery-ui-1.10.3.custom.min.js"></script>\n')
            fhandle.write('\t<script type="text/javascript" src="js/jquery.tablesorter.js"></script>\n')
            fhandle.write('\t<script type="text/javascript" src="js/jquery.simplePagination.js"></script>\n')
            fhandle.write('\t<script type="text/javascript" src="js/persist-min.js"></script>\n')
            fhandle.write('\t<script type="text/javascript" src="js/class.js"></script>\n')
            fhandle.write('\t<script type="text/javascript">var offers_per_page = %s;</script>\n' %self.configs.globals['report']['offer_per_page'])
            fhandle.write('\t<script type="text/javascript" src="js/dynamic.js"></script>\n')
        else:
            fhandle.write('\t<link rel="stylesheet" href="css/static.css" />\n')
        fhandle.write('</head>\n')

    def generateDownloadedFile(self):
        # Search feeds
        feeds = utilities.findFiles(self.rootdir, '*.feed')
        fl = open(os.path.join(self.wwwdir, 'feeds.txt'), 'w')
        for f in feeds:
            fl.write(os.path.basename("%s\n" % f))
        fl.close()

        # Search pages
        dirs = os.listdir(self.rootdir)
        for d in dirs:
            pagedir = '%s/%s' % (self.rootdir, d)
            pages = utilities.findFiles(pagedir, '*.page')
            saveto = os.path.join('%s/%s.txt' % (self.wwwdir, d))
            pl = open(saveto, 'w')
            for p in pages:
                filename = re.sub(r'.*?/pages/', '', p)
                pl.write("%s\n" % filename)
            pl.close()


    def generateStatistics(self):
        html_dir = self.wwwdir

        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()

        stat = open(os.path.join(html_dir, 'statistics.html'), 'w')

        stat.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
        stat.write('<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">\n')
        stat.write("<head>\n")
        stat.write("<link href=\"./css/bootstrap.css\" rel=\"stylesheet\" />\n")
        stat.write("<link href=\"./css/bootstrap-responsive.css\" rel=\"stylesheet\" />\n")
        stat.write("<style>table{font: 10pt verdana, geneva, lucida, 'lucida grande', arial, helvetica, sans-serif;}</style>\n")
        stat.write("<meta http-equiv=\"Content-type\" content=\"text/html; charset=utf-8\"></head>\n")
        stat.write("<body>\n")
        stat.write('\t<ul class="nav nav-pills nav-justified">\n')
        stat.write('\t\t<li><a href="report_full.html">All offers</a></li>\n')
        stat.write('\t\t<li><a href="report_filtered.html">Filtered offers</a></li>\n')
        stat.write('\t\t<li class="active"><a href="statistics.html">Statistics</a></li>\n')
        stat.write('\t</ul>\n')
        stat.write("<table class=\"table table-condensed\">")
        stat.write("<thead>")
        stat.write("<tr>")
        stat.write("<th>JobBoard</th>")
        stat.write("<th>Total Offers</th>")
        stat.write("<th>Offers not from blacklist</th>")
        stat.write("<th>Offers from blacklist</th>")
        stat.write("</tr>")
        stat.write("</thead>")

        jobboardlist = self.configs.getJobboardList()
        for jobboardname in jobboardlist:
            plugin = utilities.loadJobBoard(jobboardname, self.configs)
            data = plugin.fetchAllOffersFromDB()
            stat.write("<tr>")
            stat.write("<td>%s</td>" % plugin.name)
            stat.write("<td>%s</td>" % len(data))
            stat.write("<td></td>")
            stat.write("<td></td>")
            stat.write("</tr>")

        stat.write("</table>")
        stat.write("</html>")
        stat.close()

    def generateReport(self, filtered=True):

        # Directory
        html_dir = self.wwwdir
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)

        # Query
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()
        data = None

        sql_filtered = "SELECT * FROM offers WHERE company not IN (SELECT company FROM blacklist) ORDER BY date_pub DESC"
        sql_full = "SELECT * FROM offers ORDER BY date_pub DESC"
        cursor.execute(sql_filtered)
        data_filtered = cursor.fetchall()
        cursor.execute(sql_full)
        data_full = cursor.fetchall()
        count_filtered = len(data_filtered)
        count_full = len(data_full)
        if (filtered):
            report = open(os.path.join(html_dir, 'report_filtered.html'), 'w')
            data = data_filtered
        else:
            report = open(os.path.join(html_dir, 'report_full.html'), 'w')
            data = data_full

        self.header(report)

        report.write('<body>\n')
        # page header
        if count_full:
            report.write('\t<ul class="nav nav-pills nav-justified">\n')
            report.write('\t\t<li class="%s"><a href="report_full.html">All %s offers</a></li>\n' %("" if filtered else "active", count_full))
            report.write('\t\t<li class="%s"><a href="report_filtered.html">%s filtered offers (%.2f%%)</a></li>\n' %("active" if filtered else "", count_filtered, 100*(float)(count_filtered)/count_full))
            report.write('\t\t<li><a href="statistics.html">Statistics</a></li>\n')
            report.write('\t\t<li class="disabled"><a href="#">%s blacklisted offers (%.2f%%)</a></li>\n' %(count_full-count_filtered, 100*(float)(count_full-count_filtered)/count_full))
            report.write('\t</ul>\n')

        # page body
        report.write('\t<table id="offers" class="table table-condensed">\n')
        # table header
        report.write('\t\t<thead>\n')
        report.write('\t\t\t<tr id="lineHeaders">\n')
        report.write('\t\t\t\t<th class="pubdate">Pubdate</th>\n')
        report.write('\t\t\t\t<th class="type">Type</th>\n')
        report.write('\t\t\t\t<th class="title">Title</th>\n')
        report.write('\t\t\t\t<th class="company">Company</th>\n')
        report.write('\t\t\t\t<th class="location">Location</th>\n')
        report.write('\t\t\t\t<th class="contract">Contract</th>\n')
        report.write('\t\t\t\t<th class="salary">Salary</th>\n')
        report.write('\t\t\t\t<th class="source">Source</th>\n')
        report.write('\t\t\t</tr>\n')
        if self.configs.globals['report']['dynamic']:
            report.write('\t\t\t<tr id="lineFilters">\n')
            report.write('\t\t\t\t<td class="pubdate"></td>\n')
            report.write('\t\t\t\t<td class="type"></td>\n')
            report.write('\t\t\t\t<td class="title"></td>\n')
            report.write('\t\t\t\t<td class="company"></td>\n')
            report.write('\t\t\t\t<td class="location"></td>\n')
            report.write('\t\t\t\t<td class="contract"></td>\n')
            report.write('\t\t\t\t<td class="salary"></td>\n')
            report.write('\t\t\t\t<td class="source"></td>\n')
            report.write('\t\t\t</tr>\n')
        report.write('\t\t</thead>\n')
        # table body
        report.write('\t\t<tbody>\n')

        s_date = ''
        for row in data:
            offer = Offer()
            offer.load(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                row[7], row[8], row[9], row[10], row[11], row[12],
                row[13], row[14]
            )

            if (not self.configs.globals['report']['dynamic'] and s_date != offer.date_pub.strftime('%Y-%m-%d')):
                s_date = offer.date_pub.strftime('%Y-%m-%d')
                report.write('\t\t\t<tr class="error">\n');
                report.write('\t\t\t\t<td colspan="8" />\n')
                report.write('\t\t\t</tr>\n')

            report.write('\t\t\t<tr>\n')
            report.write('\t\t\t\t<td class="pubdate">' + offer.date_pub.strftime('%Y-%m-%d') + '</td>\n')
            report.write('\t\t\t\t<td class="type"><span class="label label-success">noSSII</span></td>\n')
            report.write('\t\t\t\t<td class="title"><a href="'+re.sub('&', '&amp;', offer.url)+'">' + offer.title + '</a></td>\n')
            report.write('\t\t\t\t<td class="company">' + offer.company + '</td>\n')
            # Location
            report.write('\t\t\t\t<td class="location">')
            if offer.department:
                report.write("%s&nbsp;" % self.box('primary', offer.department))
            report.write(offer.location)
            report.write('</td>\n')

            # contract
            duration = ""
            report.write('\t\t\t\t<td class="contract">')
            if offer.duration:
                duration = "&nbsp;%s mois" % self.box('info', offer.duration)
            if ('CDI' in offer.contract):
                report.write(self.box('success', offer.contract))
                report.write(duration)
            elif ('CDD' in offer.contract):
                report.write(self.box('warning', offer.contract))
                report.write(duration)
            else:
                report.write(self.box('', offer.contract))
                report.write(duration)
            report.write('</td>\n')
            report.write('\t\t\t\t<td class="salary">' + offer.salary + '</td>\n')
            report.write('\t\t\t\t<td class="source">' + offer.src + '</td>\n')
            report.write('\t\t\t</tr>\n')

        # closure
        report.write('\t</table>\n')
        report.write('</body>\n')
        report.write('</html>\n')
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
        self.feddid = u""
        self.title = u""
        self.company = u""

        # Contract
        self.contract = u""
        self.duration = u""

        # Location
        self.location = u""
        self.department = u""

        self.salary = u""
        self.url = u""
        self.content = u""
        self.date_add = u""
        self.date_pub = u""
        self.lat = u""
        self.lon = u""

    def load(
            self, src, ref, feedid, date_pub, date_add, title, company,
            contract, duration, location, department, lat, lon,
            salary, url, content
    ):

        self.src = src
        self.ref = ref
        self.feedid = feedid

        self.date_pub = datetime.datetime.fromtimestamp(int(date_pub))
        self.date_add = datetime.datetime.fromtimestamp(int(date_add))
        self.title = title
        self.company = company
        self.contract = contract
        self.duration = duration
        self.location = location
        self.department = department
        self.salary = salary
        self.url = url
        self.content = content

    def loadFromHtml(self, filename):
        ""

    def cleanFields(self):
        self.cleanContract()
        self.cleanLocation()
        self.cleanSalary()

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


def executeall(conf, selecteduser):
    initblacklist(conf)
    downloadfeeds(conf, selecteduser)
    downloadpages(conf)
    insertpages(conf, selecteduser)
    movepages(conf, selecteduser)
    generatereport(conf, selecteduser)


def generatereport(conf, selecteduser):
    r = ReportGenerator(conf)
    r.generate()


def initblacklist(conf):
    utilities.db_checkandcreate(conf.globals)
    utilities.blacklist_flush(conf.globals)
    utilities.blocklist_load(conf.globals)


# def downloadfeed(conf, jobboardname, feedinfo):
#     """Download a jobboard feeds"""
#     plugin = utilities.loadJobBoard(jobboardname, conf)
#     plugin.downloadFeed(feedinfo)


def downloadfeeds(conf, selecteduser):
    """Download all jobboard feeds"""

    # Get all users feeds
    feedsinfo = conf.getFeedsInfo(selecteduser)

    for jobboardname, jobboardfeeds in feedsinfo.iteritems():
        for feedid, feedinfo in jobboardfeeds.iteritems():
            plugin = utilities.loadJobBoard(jobboardname, conf)
            plugin.downloadFeed(feedinfo)



# def downloadpage(conf, jobboardname):
#     """Download a jobboard pages"""
#     plugin = utilities.loadJobBoard(jobboardname, conf)
#     urls = plugin.getUrls()
#     plugin.downloadPages(urls)


def downloadpages(conf):
    pages = Pages(conf)
    pages.downloadPages()
    # """Download all jobboard pages"""
    # jobboardlist = conf.getJobboardList()
    # for jobboardname in jobboardlist:
    #     downloadpage(conf, jobboardname)


def insertpage(conf, jobboardname):
    # Search page for jobboard
    pages = Pages(conf)
    pages.searchPagesForJobboard(jobboardname)
    plugin = utilities.loadJobBoard(jobboardname, conf)

    for page in pages.pages:
        # Load page content if needed
        if not page.downloaded:
            page.load()

        # Analyse page
        plugin.analyzePage(page)


def insertpages(conf, selecteduser):
    """Insert all pages from all jobboard"""
    jobboardlist = conf.getJobboardList()

    for jobboardname in jobboardlist:
        insertpage(conf, jobboardname)


def movepage(conf, jobboardname):
    """Move jobboard pages to offers"""
    utilities.db_checkandcreate(conf.globals)

    plugin = utilities.loadJobBoard(jobboardname, conf)
    plugin.moveToOffers()


def movepages(conf, selecteduser):
    """Move all pages from all jobboard"""
    jobboardlist = conf.getJobboardList()

    for jobboardname in jobboardlist:
        movepage(conf, jobboardname)


def clean(conf, jobboardname):
    utilities.db_checkandcreate(conf)
    utilities.db_delete_jobboard_datas(conf, jobboardname)


def importjobboard(conf, jobboardname):
    utilities.db_checkandcreate(conf)
    pagesinsert(conf)
    pagesmove(conf)


def imports(conf):
    jobboardlist = getjobboardlist(conf)
    for jobboardname in jobboardlist:
        importjobboard(conf, jobboardname)


def reimports(conf, jobboardname):
    clean(conf, jobboardname)
    imports(conf)

if __name__ == '__main__':

    # Load configs
    from config import configs as globalconfig
    configs = Config()
    configs.addGlobalconfig(globalconfig)
    configs.loadUsersConfig()

    parser = OptionParser(usage='syntax: %prog [options] <from> [to]')
    args = sys.argv[1:]
    selecteduser = None

    parser.set_defaults(version=False)
    parser.add_option('--user',
                      action='store',
                      metavar='USERNAME',
                      dest='user',
                      help='download feed only for the USERNAME'
    )


    parser.add_option('--all',
                      action='store_true',
                      dest='all',
                      help='sync the blacklist, fetch the offers and generates reports.'
    )

    parser.add_option('--feeds',
                      action='store_true',
                      dest='feeds',
                      help='download the all feeds in the config'
    )

    # parser.add_option('--feed',
    #                   action='store',
    #                   metavar='JOBBOARD',
    #                   dest='feed',
    #                   help='download only the feed from JOBBOARD in the config',
    # )

    parser.add_option('--pages',
                      action='store_true',
                      dest='pages',
                      help='download the all pages in the config'
    )

    # parser.add_option('--page',
    #                   action='store',
    #                   metavar='JOBBOARD',
    #                   dest='page',
    #                   help='download only the pages from JOBBOARD in the config'
    # )
    
    parser.add_option('--inserts',
                      action='store_true',
                      dest='inserts',
                      help='inserts all pages to offers'
    )

    parser.add_option('--insert',
                      action='store',
                      metavar='JOBBOARD',
                      dest='insert',
                      help='insert JOBBOARD pages to offers'
    )

    parser.add_option('--moves',
                      action='store_true',
                      dest='moves',
                      help='move datas to offer'
    )

    parser.add_option('--move',
                      action='store',
                      metavar='JOBBOARD',
                      dest='move',
                      help='move JOBBOARD datas to offer'
    )

    parser.add_option('--clean',
                      action='store',
                      metavar='JOBBOARD',
                      dest='clean',
                      help='clean offers from JOBBOARD source'
    )

    parser.add_option('--report',
                      action='store_true',
                      dest='report',
                      help='generate a full report'
    )

    parser.add_option('--blocklist',
                      action='store_true',
                      dest='blocklist',
                      help='update blocklist'
    )

    parser.add_option('--flush',
                      action='store_true',
                      dest='flush',
                      help = 'flush the blacklist and update it.'
    )

    parser.add_option('--p2pinit',
                      action='store_true',
                      dest='p2pinit',
                      help = 'init P2P'
    )

    parser.add_option('--version',
                      action='store_true',
                      dest='version',
                      help='output version information and exit'
    )
    # parser.add_option('-u', '--url',
    #                       action = 'store_true', dest = 'url',
    #                       help = 'analyse an url')
    # parser.add_option('-f', '--flush',
    #                       action = 'store_true', dest = 'flush',
    #                       help = 'flush the blacklist and update it.')

    (options, args) = parser.parse_args(args)

    # Clean
    if options.clean:
        clean(configs, options.clean)

    if options.version:
        print 'jobcatcher version %s - %s (%s)' % (
            __version__,
            __copyright__,
            __license__
        )
        sys.exit(0)

    if options.user:
        selecteduser = [options.user]

    if options.report:
        print "Report generation..."
        generatereport(configs, selecteduser)
        print "Done."
        sys.exit(0)

    if options.all:
        executeall(configs, selecteduser)
        sys.exit(0)

    #Feeds
    if options.feeds:
        downloadfeeds(configs, selecteduser)
        sys.exit(0)

    # if options.feed:
    #     downloadfeed(configs, options.feed)
    #     sys.exit(0)

    # Pages
    if options.pages:
        downloadpages(configs)
        sys.exit(0)

    # if options.page:
    #     downloadpage(configs, options.page)
    #     sys.exit(0)

    # Inserts
    if options.inserts:
        insertpages(configs, selecteduser)

    if options.insert:
        insertpage(configs, options.insert)

    # Moves
    if options.moves:
        movepages(configs, selecteduser)

    if options.move:
        movepage(configs, options.move)

    if options.blocklist:
        utilities.blocklist_load(configs)
        sys.exit(0)

    if options.flush:
        initblacklist(configs)
        sys.exit(0)

    if options.p2pinit:
        p = P2PDownloader(configs)
        p.initcache()
        p.sync()
        
