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

def getSectionsFull(page, revId = None):
    #get section titles and indexes
    params = {
        u'action' : u'parse',
        u'prop'   : u'sections',
        u'page'   : page.title()
    }
    if not revId is None:
        params[u'oldid'] = revId
    result = query.GetData(params, page.site())
    sectionsDefinition = [item for item in result[u'parse'][u'sections'] if item[u'level'] == u'2']

    # get section texts
    sections = []
    params = {
        u'action'    : u'query',
        u'titles'    : page.title(),
        u'prop'      : u'revisions',
        u'rvprop'    : u'content',
        u'rvlimit'   : 1
    }
    if not revId is None:
        params[u'rvstartid'] = revId
        params[u'rvendid'] = revId

    for sectionDefinition in sectionsDefinition:
        if sectionDefinition[u'index'] is None:
            continue

        try:
            sectionIndex = int(sectionDefinition[u'index'])
        except ValueError:
            continue

        params[u'rvsection'] = sectionIndex

        result = query.GetData(params, page.site())

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

#page = pywikibot.Page(pywikibot.getSite(), u'Користувач:DixonD/sandbox')
#sections = getSectionsFull(page)
#print sections
