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

class PageRevision():
    def __init__(self, page, revId = None, text = None):
        self.page = page
        self.revId = revId
        self.text = text


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
                    # some other error
                    return []

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

#page = pywikibot.Page(pywikibot.getSite(), u'Вікіпедія:Кнайпа (політики)')
#pageRevision = PageRevision(page)
#sections = pageRevision.getSections()
#print sections
