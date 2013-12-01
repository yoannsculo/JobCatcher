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
import datetime

# Jobcatcher
import utilities


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
        self.offerid = u""
        self.lastupdate = 0
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

        # Salary
        self.salary = u""
        self.salary_cleaned = u""
        self.salary_unit = 0
        self.salary_nbperiod = 0
        self.salary_min = 0
        self.salary_max = 0
        self.salary_bonus = u""
        self.salary_minbonus = 0
        self.salary_maxbonus = 0

        self.url = u""
        self.content = u""
        self.date_add = u""
        self.date_pub = u""
        self.lat = u""
        self.lon = u""

        self.state = u"ACTIVE"

    def load(
            self, src, offerid, lastupdate, ref, feedid, date_pub, date_add,
            title, company, contract, duration, location, department, lat, lon,
            salary, salary_cleaned, salary_unit, salary_nbperiod, salary_min,
            salary_max, salary_bonus, salary_minbonus, salary_maxbonus, url,
            content, state
    ):

        self.src = src
        self.offerid = offerid
        self.lastupdate = lastupdate
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

        # Salary
        self.salary = salary
        self.salary_cleaned = salary_cleaned
        self.salary_unit = salary_unit
        self.salary_nbperiod = salary_nbperiod
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary_bonus = salary_bonus
        self.salary_minbonus = salary_minbonus
        self.salary_maxbonus = salary_maxbonus
        self.url = url
        self.content = content

        self.state = state

    def loadFromHtml(self, filename):
        ""

    def salaryToText(self, salary):
        if salary > 10000:
            salary = "%sK€" % (salary / 1000)
        else:
            salary = "%s€" % salary
        return salary

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
        minbonus = 0
        maxbonus = 0

        # Not find the salary, return de origin text
        if self.salary_min == 0:
            self.salary_cleaned = utilities.filter_salary_fr(self.salary)
            return

        # Month salary
        if self.salary_unit == 1:
            self.salary_min = self.salary_min * self.salary_nbperiod

            if self.salary_max != '':
                self.salary_max = self.salary_max * self.salary_nbperiod

        # Annual salary
        if self.salary_unit == 12 and self.salary_nbperiod != 12:

            # Calc month salary
            minmonth = self.salary_min / self.salary_nbperiod
            if self.salary_max > 0:
                maxmonth = self.salary_max / self.salary_nbperiod

            # Calc annual salary
            self.salary_min = minmonth * 12
            if self.salary_max > 0:
                self.salary_min = maxmonth * 12

            # Calc bonus
            minbonus = minmonth * (self.salary_nbperiod - 12)
            maxbonus = maxmonth * (self.salary_nbperiod - 12)

        # Round value
        if self.salary_min > 100:
            self.salary_min = int(self.salary_min)

        if self.salary_max > 100:
            self.salary_max = int(self.salary_max)

        if minbonus > 100:
            minbonus = int(minbonus)

        if maxbonus > 100:
            maxbonus = int(maxbonus)

        # Calc range if needed
        if self.salary_min and self.salary_max:
            self.salary_cleaned = '%s - %s' % (
                self.salaryToText(self.salary_min),
                self.salaryToText(self.salary_max)
            )
        else:
            if self.salary_min:
                self.salary_cleaned = '%s' % self.salaryToText(self.salary_min)
            else:
                self.salary_cleaned = '%s' % self.salaryToText(self.salary_max)

        # Add bonus
        if minbonus > 0 and maxbonus > 0:
            self.salary_cleaned = "%s + (%s/%s)" % (
                self.salary_cleaned,
                self.salaryToText(minbonus),
                self.salaryToText(maxbonus)
            )
        elif minbonus > 0:
            self.salary_cleaned = "%s + %s" % (
                self.salary_cleaned,
                self.salaryToText(minbonus)
            )

        self.salary_cleaned = "%s / an" % self.salary_cleaned

        if self.salary_bonus != "":
            self.salary_cleaned = "%s + prime (%s)" % (
                self.salary_cleaned,
                self.salary_bonus
            )

        self.salary_cleaned = utilities.filter_salary_fr(self.salary_cleaned)

        return

    def add_db(self):
        return utilities.db_add_offer(self)

    def printElt(self):
        #print "Title :" + self.title
        print "Company : " + self.company
