# -*- coding: utf-8 -*-
#!/usr/bin/env python2.7

# Copyright 2013 DixonD-git

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

import wikipedia as pywikibot
import query
import itertools
import datetime

class PageRevision():
    def __init__(self, page, revId = None, text = None, editDate = None):
        self.page = page
        self.revId = revId
        self.text = text
        self.editDate = editDate

    def getSectionDefinitions(self):
        #get section titles and indexes
        params = {
            u'action': u'parse',
            u'prop': u'sections',
            u'page': self.page.title()
        }
        if not self.revId is None:
            params[u'oldid'] = self.revId
        result = query.GetData(params, self.page.site())

        # check errors
        if u'error' in result:
            errorCode = result[u'error'][u'code']
            # skip deleted revisions
            if errorCode == u'permissiondenied':
                return []
            raise RuntimeError(result[u'error'])
            return

        sectionsDefinition = [item for item in result[u'parse'][u'sections'] if item[u'level'] == u'2']
        return sectionsDefinition

    def getSectionsFull(self):
        sectionsDefinition = self.getSectionDefinitions()

        # get section texts
        sections = []
        params = {
            u'action'    : u'query',
            u'titles'    : self.page.title(),
            u'prop'      : u'revisions',
            u'rvprop'    : u'content',
            u'rvlimit'   : 1
        }
        if not self.revId is None:
            params[u'rvstartid'] = self.revId
            params[u'rvendid'] = self.revId

        for sectionDefinition in sectionsDefinition:
            if sectionDefinition[u'index'] is None:
                continue

            try:
                sectionIndex = int(sectionDefinition[u'index'])
            except ValueError:
                continue

            params[u'rvsection'] = sectionIndex

            result = query.GetData(params, self.page.site())

            if u'error' in result:
                errorCode = result[u'error'][u'code']
                if errorCode == u'rvnosuchsection':
                    # skip this section
                    continue
                else:
                    raise RuntimeError("%s" % result['error'])

            sectionContent = result[u'query'][u'pages'].values()[0][u'revisions'][0][u'*']

            sections.append({u'title':sectionDefinition[u'line'], u'text': sectionContent})

        return sections

    def getText(self):
        # get text if not provided
        if self.text is None:
            params = {
                u'action': u'query',
                u'titles': self.page.title(),
                u'prop': u'revisions',
                u'rvprop': u'content',
                u'rvlimit': 1
            }
            if not self.revId is None:
                params[u'rvstartid'] = self.revId
                params[u'rvendid'] = self.revId

            result = query.GetData(params, self.page.site())
            if 'error' in result:
                raise RuntimeError("%s" % result['error'])
            self.text = result[u'query'][u'pages'].values()[0][u'revisions'][0][u'*']

        return self.text

    def getSections(self):
        # get text if not provided
        if self.text is None:
            self.getText()

        # get sections definitions
        sectionDefinitions = self.getSectionDefinitions()

        # check if response is proper; see https://bugzilla.wikimedia.org/show_bug.cgi?id=25203
        for sectionInfo in sectionDefinitions:
            if sectionInfo[u'byteoffset'] >= len(self.text):
                # we need to go with slow but correct way
                return self.getSectionsFull()

        #split text to sections
        sections = [{u'title':pair[0][u'line'], u'text': self.text[pair[0][u'byteoffset']:pair[1][u'byteoffset']].strip()} for pair in itertools.izip(sectionDefinitions, sectionDefinitions[1:] + [{u'byteoffset': len(self.text)}])]

        return sections

class PageHistory():
    def __init__(self, page):
        self.page = page

    def _getRawHistory(self, reverseOrder = False, revCount = None, startRevId = None, retrieveTexts = False,
                       properties = u'ids|timestamp|user|comment|size|tags'):
        dataQ = []
        thisHistoryDone = False

        params = {
            u'action': u'query',
            u'prop': u'revisions',
            u'titles': self.page.title(),
            u'rvprop': properties
        }

        # set content or not
        if retrieveTexts:
            params[u'rvprop'] += u'|content'

        # set limit
        if revCount is None:
            params[u'rvlimit'] = u'max'
        else:
            params[u'rvlimit'] = revCount

        #set first revision from which to start
        if not startRevId is None:
            params[u'rvstartid'] = startRevId

        # set order
        if reverseOrder:
            params[u'rvdir'] = u'newer'

        # while not retrieved
        while not thisHistoryDone:
            #get data
            result = query.GetData(params, self.page.site())
            if u'error' in result:
                raise RuntimeError(u"{0".format(result[u'error']))

            # check if the result is proper
            pageInfo = result[u'query'][u'pages'].values()[0]
            if result[u'query'][u'pages'].keys()[0] == "-1":
                if u'missing' in pageInfo:
                    raise pywikibot.NoPage(self.page.site(), unicode(self.page), u"Page does not exist.")
                elif u'invalid' in pageInfo:
                    raise pywikibot.BadTitle(u'BadTitle: {0}'.format(self))

            for r in pageInfo['revisions']:
                # set defaults
                values = {
                    u'ids': None,
                    u'timestamp': None,
                    u'user': None,
                    u'flags': None,
                    u'comment': u'',
                    u'size': -1,
                    u'tags': [],
                    u'content': u'',
                }
                values.update(r)

                if u'revid' in r:
                    values[u'ids'] = r[u'revid']
                if u'*' in r:
                    values[u'content'] = r[u'*']
                elements = params[u'rvprop'].split('|')
                values = dict((e, values[e]) for e in elements)
                dataQ.append(values)

            if u'query-continue' in result and (revCount is None or len(dataQ) < revCount):
                params.update(result[u'query-continue'][u'revisions'])
                if not revCount is None:
                    params[u'rvlimit'] = revCount - len(dataQ)
            else:
                thisHistoryDone = True

        return dataQ

    def getFullHistory(self, reverseOrder = False, revCount = None, startRevId = None):
        return self.getHistory(reverseOrder = reverseOrder, revCount = revCount, startRevId = startRevId, retrieveTexts = True)

    def getHistory(self, reverseOrder = False, revCount = None, startRevId = None, retrieveTexts = False):
        rawHistory = self._getRawHistory(reverseOrder = reverseOrder, revCount = revCount, startRevId = startRevId, retrieveTexts = retrieveTexts)

        pageRevisions = []
        for item in rawHistory:
            revId = int(item[u'ids'])
            revDate = datetime.datetime.strptime(item[u'timestamp'], "%Y-%m-%dT%H:%M:%SZ")

            text = item[u'content'] if u'content' in item else None

            pageRevision = PageRevision(self.page, revId = revId, editDate = revDate, text = text)
            pageRevisions.append(pageRevision)

        return pageRevisions

    def getAllRevisionsCount(self):
        rawHistory = self._getRawHistory(properties = u'ids')
        return len(rawHistory)
