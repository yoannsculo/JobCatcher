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
import importlib

# Jobcatcher
import utilities


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
            for jobboardname in self.users[u]:
                if 'feeds' in self.users[u][jobboardname]:
                    for f in self.users[u][jobboardname]['feeds']:
                        if 'datas' not in f:
                            f['datas'] = None
                        feedid = utilities.getEncodedURL(f['url'], f['datas'])
                        if jobboardname not in feedslist:
                            feedslist[jobboardname] = {}
                        if feedid not in feedslist[jobboardname]:
                            feedslist[jobboardname][feedid] = f

        return feedslist

    def getFeedIdsForUser(self, user):
        """Get feeds list info"""
        feedidslist = list()

        for jobboardname in self.users[user]:
            if 'feeds' in self.users[user][jobboardname]:
                for f in self.users[user][jobboardname]['feeds']:
                    if 'datas' not in f:
                        f['datas'] = None
                    feedid = utilities.getEncodedURL(f['url'], f['datas'])
                    if feedid not in feedidslist:
                        feedidslist.append(feedid)

        return feedidslist

    def getJobboardList(self, selecteduser=None):
        jobboardlist = []

        # If in debug mode return the config.py['debug_jobboard']
        if 'debug_jobboard' in self.globals:
            if len(self.globals['debug_jobboard']) > 0:
                return self.globals['debug_jobboard']

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
