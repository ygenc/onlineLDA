#!/usr/bin/python

# printtopics.py: Prints the words that are most prominent in a set of
# topics.
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

import sys, os, re, random, math, urllib2, time, cPickle
import numpy

 

def main():
    """
    YG
    Displays topics fit by Wldap.py.  
    """
    
   #YG this is to use different prefixes to the files that are being used:
    prefix= sys.argv[1]
    
    testlambda=numpy.loadtxt('./WikiResults/{0}gamma.dat'.format(prefix))
    
    topicnames=file('./WikiDocs/{0}Topics.txt'.format(prefix)).readlines()
    
    documents={}
    
    for k, iter in enumerate(testlambda):
        documents[k]=[i for i in sorted(enumerate(iter), key=lambda x:x[1], reverse=True) if i[1]>1]
        
    File=open('./WikiResults/{0}topicdist.txt'.format(prefix), "w+")     
    for key in documents:
        File.write('Document %s \n' % key)
        mytopics=documents[key]
        for tname, tvalue in mytopics:
            File.write('topic: %s  --  value: %f \n' % (topicnames[tname].replace('\n','') , tvalue))

#    
#    
#    vocab = str.split(file(sys.argv[1]).read())
#    testlambda = numpy.loadtxt(sys.argv[2])
#
#    for k in range(0, len(testlambda)):
#        lambdak = list(testlambda[k, :])
#        lambdak = lambdak / sum(lambdak)
#        temp = zip(lambdak, range(0, len(lambdak)))
#        temp = sorted(temp, key = lambda x: x[0], reverse=True)
#        print 'topic %d:' % (k)
#        # feel free to change the "53" here to whatever fits your screen nicely.
#        for i in range(0, 53):
#            print '%20s  \t---\t  %.4f' % (vocab[temp[i][1]], temp[i][0])
#        print

if __name__ == '__main__':
    main()
