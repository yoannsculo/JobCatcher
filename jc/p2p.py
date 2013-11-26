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
import os
import re

# Jobcatcher
import utilities


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

    def initLocalCache(self):
        #p2plist = self.listServers()
        plugins = self.configs.getJobboardList()

        for name, url in self.configs.globals['p2pservers'].iteritems():
            # Download feed ifnormations
            print 'Search for %s' % name
            destdir = "%s/%s" % (self.p2pdir, name)
            saveto = "%s/feeds.txt" % destdir
            utilities.downloadFile(saveto, '%s/feeds.txt' % url)

            # Search pages for jobboards
            for jobboardname in plugins:
                saveto = "%s/%s.txt" % (destdir, jobboardname)
                page = utilities.downloadFile(
                    saveto, '%s/%s.txt' % (url, jobboardname)
                )
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
                            utilities.downloadFile(local, remote)
