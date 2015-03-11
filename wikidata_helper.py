# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

# Copyright 2014 DixonD-git

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pywikibot

class WikidataHelper():
    def __init__(self):
        pass

    @staticmethod
    def getFirstItemStatement(item, propertyId):
        item.get()

        claims = item.claims

        return claims[propertyId][0].target if propertyId in claims else None

    @staticmethod
    def itemStatementExists(item, propertyId, statementItemId = None):
        item.get()

        claims = item.claims

        if propertyId not in claims:
            return False

        statements = claims[propertyId]

        if statementItemId is None:
            return True

        for statement in statements:
            if statement.target.id == statementItemId:
                return True

        return False

    @staticmethod
    def getSitelink(item, siteName):
        item.get()

        sitelinks = item.sitelinks

        return sitelinks[siteName] if siteName in sitelinks else None

    @staticmethod
    def getItemsByItemStatement(propertyId, statementItem):
        items = [pywikibot.ItemPage(item.site, item.title()) for item in statementItem.getReferences(namespaces=0)]
        items = [item for item in items if WikidataHelper.itemStatementExists(item, propertyId, statementItem.id)]

        return items