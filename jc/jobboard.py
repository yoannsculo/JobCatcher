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

import sys

import requests
import utilities
import sqlite3 as lite


class JobBoard(object):
    """Generic Class forcreate new jobboard"""
    def __init__(self, configs=None):
        self._rootdir = configs.globals['rootdir']
        self._configs = configs
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

    def isTableCreated(self):
        """Check if the table for jobboard exist"""
        return utilities.db_istableexists(
            self.configs,
            "jb_%s" % self.name
        )

    def downloadFeed(self, feed, forcedownload=False):
        """Download feed from jobboard"""
        datas = None
        if 'datas' in feed:
            datas = feed['datas']

        saveto = utilities.getFeedDestination(
            self.rootdir, self.name, feed['url'], datas
        )

        try:
            utilities.downloadFile(
                saveto, feed['url'], datas, True,
                self.configs.globals['refreshfeeds']
            )
        except:
            print ("Error for download %s feed" % feed['url'])

        return saveto

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
                utilities.db_add_offer(self.configs, o)
            else:
                print "Error moving to offers of %s" % d['url']

    def createTable(self,):
        """Create Jobboard table"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def getUrls(self):
        """Get Urls offers from feed"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def extractOfferId(self, page):
        """Extract offerid from url"""
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

    def deleteOffer(self, ref):
        """Delete Offer & jobboard data"""
        mess = "%s.%s" % (self.__class__, sys._getframe().f_code.co_name)
        raise NotImplementedError(mess)

    def fetchAllOffersFromDB(self):
        conn = lite.connect(self.configs.globals['database'])
        cursor = conn.cursor()
        sql = "SELECT * FROM offers WHERE source='%s' ORDER BY date_pub DESC" %(self.name)
        cursor.execute(sql)
        data = cursor.fetchall()
        return data
