#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = [
    'Jonathan Courtoux <j.courtoux@gmail.com>',
    'Bruno Adelé <bruno@adele.im>'
]
__copyright__ = 'Copyright (C) 2013 jonathan courtoux'
__license__ = 'GPLv2'
__version__ = '0.1'

import os
import re
import time

from jobcatcher import JobCatcher
from jobcatcher import Jobboard
from jobcatcher import Offer
from jobcatcher import Location
from config import configs

from xml.dom import minidom
import datetime
import utilities

from HTMLParser import HTMLParser
from BeautifulSoup import BeautifulSoup

class Cadresonline(Jobboard):

    def __init__(self):
        self.name = "Cadresonline"
        self.url = "http://www.cadresonline.com"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/cadresonline"
        self.lastFetchDate = 0

    def fetch_url(self, url):
        filename = url.split('/')[-1]
        utilities.download_file(url, self.processingDir)

        xmldoc = minidom.parse(os.path.join(self.processingDir, filename))

        MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0]
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

            if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
                print "Downloading %s" % (link)
                utilities.download_file(link, self.processingDir)

    def fetch(self):
        print "Fetching " + self.name

        feed_list = configs['cadresonline']['feeds']
        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        for url in feed_list :
            self.fetch_url(url)

        self.processOffers()

    def processOffers(self):
        for file in os.listdir(self.processingDir):
            if (not file.lower().endswith('.html')):
                    continue

            print "Processing %s" % (file)
            offer = CadreonlineOffer()
            res = offer.loadFromHtml(os.path.join(self.processingDir, file))
            if (res != 0):
                continue
            offer.date_add = int(time.time())
            loc = Location()
            # loc.loadFromAddress(offer.location)
            offer.lat = loc.lat
            offer.lon = loc.lon
            if (offer.add_db() == 0):
                os.remove(os.path.join(self.processingDir,file))

    def setup(self):
        print "setup " + self.name

class CadreonlineOffer(Offer):

    src     = 'CADRESONLINE'
    license = ''

    def loadFromHtml(self, filename):
        fd = open(filename, 'rb')
        html = fd.read()
        fd.close()

        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        # Offer still available ?
        res = soup.body.find('div', attrs={'id':'job_offer'})
        if (res != None):
            content = res.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton c\
                i-dessous pour revenir à l\'onglet Mes Offres'):
                return 1

        # Title
        res = soup.body.find("div", attrs={'id': 'ariane'})
        if not res:
            return -1
        res = res.find('strong')
        self.title = HTMLParser().unescape(res.text)

        # Other information
        res = soup.body.find("ul", attrs={'class': 'resume'})
        if not res:
            return -1

        res = res.findAll("li")
        if not res:
            return -1

        for elt in res:
            # Contract
            m = re.match(ur'^Contrat.* :(.*)', elt.text)
            if m:
                self.contract = m.group(1)
                self.cleanContract()

            # Company
            m = re.match(ur'^Soci.* :(.*)', elt.text)  # TODO fix a UTF problem
            if m:
                self.company = m.group(1)

            # Location
            m = re.match(ur'^Localisation.* :(.*)', elt.text)
            if m:
                self.location = m.group(1)

            # Reference
            m = re.match(ur'^R.*f.*ence.* :(.*)', elt.text)
            if m:
                self.ref = m.group(1)

            # Reference
            m = re.match(ur'^Publi.* le :(.*)', elt.text)
            if m:
                self.date_pub = datetime.datetime.strptime(m.group(1), "%d/%m/%Y").strftime('%s')
                print self.date_pub


        # Content
        # res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
        # res = res.find('div', attrs={'class':'boxContentInside'})
        # self.content = HTMLParser().unescape(res.text);

        self.url = "http://cadresonline.com/" + os.path.basename(filename)

        return 0
