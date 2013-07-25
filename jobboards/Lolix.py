#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from jobcatcher import JobCatcher
from jobcatcher import Jobboard
from jobcatcher import Offer

from xml.dom import minidom
import datetime
import utilities

class Lolix(Jobboard):

    def __init__(self):
        self.name = "Lolix"
        self.url = "http://fr.lolix.org/"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/lolix"
        self.lastFetchDate = 0

    def fetch(self):

        print "Fetching " + self.name

        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        # self.processOffers()

    def setup(self):
        print "setup " + self.name

class LolixOffer(Offer):

    src     = 'Lolix'
    license = ''

    def cleanSalary(self):
        self.salary = utilities.filter_salary_fr(self.salary)

    def loadFromHtml(self, filename):
        return 0

