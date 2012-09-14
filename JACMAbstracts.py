# wikirandom.py: Functions for downloading random articles from Wikipedia
#
# Copyright (C) 2010  Matthew D. Hoffman
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, urllib2, re, string, time, threading




def get_abstracts():
    """
    Downloads n articles in parallel from Wikipedia and returns lists
    of their names and contents. Much faster than calling
    get_random_wikipedia_article() serially.
    """
 
    articles = list()
    articlenames = list()
    
    for line in  file('./jacm/withIDAbstracts.txt').readlines():
        combo=line.split('\t')
        articlenames.append(combo[0])
        articles.append(combo[1])
        
#        '''
#         YEGIN: added for test
#         '''    
#        print WikiThread.articles
#        print WikiThread.articlenames
        
        
    return (articles, articlenames)

 
