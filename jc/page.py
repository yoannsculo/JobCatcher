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

# System
import re

# Jobcatcher
import utilities


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
        plugin = utilities.loadJobBoard(jobboardname, self.configs)
        urls = plugin.getUrls()
        plugin.downloadPages(urls)

    def downloadPages(self):
        """Download all jobboard pages"""
        jobboardlist = self.configs.getJobboardList()
        for jobboardname in jobboardlist:
            self.downloadPage(jobboardname)
