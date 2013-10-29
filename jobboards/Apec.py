#!/usr/bin/env python
# -*- coding: utf-8 -*-

__authors__ = 'Yoann Sculo'
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

""" License : http://cadres.apec.fr/delia/core/common/site/ApecViewDetailConseil/currentArticle_ART_46448/Voir+les+conditions+g%C3%A9n%C3%A9rales+d+utilisation.html
"""

class Apec(Jobboard):

    def __init__(self):
        self.name = "APEC"
        self.url = "http://www.apec.fr"
        self.lastFetch = ""
        self.processingDir = self.dlDir + "/apec"
        self.lastFetchDate = 0

    # fetch a specific  url
    def fetch_offer(self, url):
        if (not os.path.isfile(os.path.join(self.processingDir, url.split('/')[-1]))):
            print "Downloading %s" % (url)
            utilities.download_file(url, self.processingDir)
        else:
            print "Download failed. File already there."

        return os.path.join("", url.split('/')[-1])

    def fetch_url(self, url):
        filename = url.split('/')[-1]
        utilities.download_file(url, self.processingDir)

        xmldoc = minidom.parse(os.path.join(self.processingDir, filename))

        MainPubDate = xmldoc.getElementsByTagName('pubDate')[0].firstChild.data
        epochPubDate = datetime.datetime.strptime(MainPubDate, "%a, %d %b %Y %H:%M:%S +0100").strftime('%s')

        # if (epochPubDate <= self.lastFetchDate):
        #     return 0

        itemlist = xmldoc.getElementsByTagName('item')

        for elt in itemlist :
            # TODO : Test object first
            title = elt.getElementsByTagName('title')[0].firstChild.data
            link = elt.getElementsByTagName('link')[0].firstChild.data.split("?")[0]
            pubDate = elt.getElementsByTagName('pubDate')[0].firstChild.data

            if (epochPubDate <= self.lastFetchDate):
                break

            if (not os.path.isfile(os.path.join(self.processingDir, link.split('/')[-1]))):
                print "Downloading %s" % (link)
                utilities.download_file(link, self.processingDir)


    def fetch(self):
        print "Fetching " + self.name

        feed_list = configs['apec']['feeds']

        if (not os.path.isdir(self.processingDir)):
                os.makedirs(self.processingDir)

        for url in feed_list :
            self.fetch_url(url)

        self.processOffers()

    def processOffer(self, file):
        if (not file.lower().endswith('.html')):
            return 1

        print "Processing %s" % (file)
        offer = ApecOffer()
        res = offer.loadFromHtml(os.path.join(self.processingDir, file))
        if (res != 0):
            print "Couldn't add %s offer, html is bad formatted or has unknown pattern." % (file)
            # os.remove(os.path.join(self.processingDir,file))
            return 2

        offer.date_add = int(time.time())

        loc = Location()
        # loc.loadFromAddress(offer.location)
        offer.lat = loc.lat
        offer.lon = loc.lon

        # offer.printElt()
        res = offer.add_db()
        # If the offer is already there in database
        # or successfully added.
        if (res == 0 or res == 1):
            ""
            # os.remove(os.path.join(self.processingDir,file))
        else:
            print "Couldn't add %s offer, an error occured." % (file)

        return 0

    def setup(self):
        print "setup " + self.name

class ApecOffer(Offer):

    src     = 'APEC'
    license = ''

    def loadFromHtml(self, filename):
        fd = open(filename, 'rb')
        html = fd.read()
        fd.close()

        soup = BeautifulSoup(html, fromEncoding="UTF-8")

        # Offer still available ?
        res = soup.body.find('div', attrs={'class':'boxSingleMain box'})
        if (res != None):
            content = res.find('p')
            if (content.text == u'L\'offre que vous souhaitez afficher n\'est plus disponible.Cliquer sur le bouton ci-dessous pour revenir à l\'onglet Mes Offres'):
                return 1

        # Title
        res = soup.body.find('div', attrs={'class':'boxMain boxOffres box'})
        if (res == None):
            return -1
        res = res.find("h2", attrs={'class':'borderBottom0'})
        self.title = HTMLParser().unescape(res.text)
        matchObj = re.match( ur'Offre d\'emploi (.*)', self.title)
        if matchObj:
            self.title = matchObj.group(1)

        # Other information
        res = soup.body.find('div', attrs={'class':'content1_9ImbLeft'})
        res = res.findAll("tr")

        for elt in res:
            th = elt.find('th')
            td = elt.find('td')
            if (th.text == u'Référence Apec :'):
                self.ref = HTMLParser().unescape(td.text)
            if (th.text == u'Date de publication :'):
                apec_date = HTMLParser().unescape(td.text)
                self.date_pub = datetime.datetime.strptime(apec_date, "%d/%m/%Y").strftime('%s')
            if (th.text == u'Société :'):
                self.company = HTMLParser().unescape(td.text)
                matchObj = re.match( ur'(.*)Voir toutes les offres', self.company)
                if matchObj:
                    self.company = matchObj.group(1)
                matchObj = re.match( ur'(.*)Voir plus d\'infos sur la société', self.company)
                if matchObj:
                    self.company = matchObj.group(1)

            if (th.text == u'Type de contrat :' or th.text == u'Nombre de postes :'):
                self.contract = HTMLParser().unescape(td.text)
                self.cleanContract()

            if (th.text == u'Lieu :'):
                self.location = HTMLParser().unescape(td.text)
                self.cleanLocation()

            if (th.text == u'Salaire :'):
                self.salary = HTMLParser().unescape(td.text)
                self.cleanSalary()

            if (th.text == u'Expérience :'):
                self.experience = HTMLParser().unescape(td.text)

        # Content
        res = soup.body.find('div', attrs={'class':'contentWithDashedBorderTop marginTop boxContent'})
        res = res.find('div', attrs={'class':'boxContentInside'})
        self.content = HTMLParser().unescape(res.text);

        self.url = "http://cadres.apec.fr/offres-emploi-cadres/" + os.path.basename(filename)

        return 0
