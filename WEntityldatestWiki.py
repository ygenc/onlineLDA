#!/usr/bin/python

# onlinewikipedia.py: Demonstrates the use of online VB for LDA to
# analyze a bunch of random Wikipedia articles.
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

import cPickle, string, numpy, getopt, sys, random, time, re, pprint
from gensim import corpora
import WEntityldavb
import readEntityWiki

def get_documents(filename):
    ids=[]
    docs=[]
    for line in  file(filename).readlines():
        combo=line.split('\t')
        ids.append(combo[0])
        docs.append(eval(combo[1]))
    
    return (docs, ids)
def main():
    """
    Downloads and analyzes a bunch of random Wikipedia articles using
    online VB for LDA.
    """
    
  
    #YG this is to use different prefixes to the files that are being used:
    #namely WikiDictionary
    prefix=""+sys.argv[1]
    
    
    #YG: This is file that has all the documents to be analyzed
    #YG: AbstractEntities.txt
    documentsFile=""+sys.argv[2]
#    readEntityWiki.get_lambda('./Entity/TopicEntities.txt' )
    readEntityWiki.get_lambda('./Entity/TopicEntities.txt','./Entity/TopicEntitiesLink.txt')
    #Prepares the documents to be used
    index={}
    mytitles=file('./jacm/wiki_classIndexCLEAN.txt').readlines()
    
    for mtitle in [title.split('\t') for title in mytitles]:
        index[mtitle[0].strip()]=mtitle[1].strip()

    # The number of documents to analyze each iteration
    batchsize = 1
    documentstoanalyze=1
    # The total number of documents in Wikipedia
    D = 617
    # The number of topics
    K = len(mytitles)

    # How many documents to look at
   
    # Our vocabulary
    # tokens(all entities resolved)
    
    vocab = eval(file('./Entity/tokens.txt').read())
     
    W = len(vocab)
    print ' vocabulary loaded; ' + str(W) + ' words'

    # Initialize the algorithm with alpha=1/K, eta=1/K, tau_0=1024, kappa=0.7
    
    '''
    
    Initializing the updated LDA (WDA classs), the biggest difference is that lambda
    values are going to be read from file
    '''
    wda = WEntityldavb.WLDA(vocab, K, D, .5, 1./K, 1024., 0.7, './Entity/WIKIlambda.txt')
    
    # Run until we've seen D documents. (Feel free to interrupt *much*
    # sooner than this.)
    for iteration in range(0, 1):
        # Download some articles
         
        '''
        YG
        TODO
        '''
#        (docset, articlenames) = \
#            readWiki.get_articles()
        
        (docset, articlenames) = \
              get_documents(documentsFile)
        D=len(docset)
            
        # Give them to online LDA
        
        ''' 
        YG
        Instead of updating lambda we are only doing an e step
        initially do_e_sep was embedded in updating lambda
        '''
        (gamma, sstats) =  wda.do_e_step(docset)
        
        bound= wda.approx_bound(docset, gamma)
        
        # Compute an estimate of held-out perplexity
#        if not gensim:
        (wordids, wordcts) = WEntityldavb.parse_doc_list(docset, wda._vocab)
#        else:
#            print 'Not Gensim'
#            wordids=[[pair[0] for pair in corp] for corp in corpus]
#            wordcts=[[pair[1] for pair in corp] for corp in corpus]
#            print len(wordids[0])
#            print 'word ids:...',wordids[0]
#            print len(wordcts[0])
#            print 'word cts:...',wordcts[0]
            
            
        
      
        perwordbound = bound * len(docset) / (D * sum(map(sum, wordcts)))
 
        
        print '%d:  rho_t = %f,  held-out perplexity estimate = %f' % \
            (iteration, wda._rhot, numpy.exp(-perwordbound))

        # Save lambda, the parameters to the variational distributions
        # over topics, and gamma, the parameters to the variational
        # distributions over topic weights for the articles analyzed in
        # the last iteration.
         
        '''
        YG 
        No need to change the lambda values
        '''
        #numpy.savetxt('lambda-%d.dat' % iteration, wda._lambda)
        
     
        #Saving failes()
        numpy.savetxt('./Entity/{0}gamma.dat'.format(prefix), gamma)
        
        mytitles=file('./jacm/wiki_classIndexCLEAN.txt').readlines()
        topicnames=[title.split('\t')[0].strip() for title in mytitles]
        
        
        results={}
        
        #Reading Actual
        actual={}
        cls=file('./jacm/JACM_Classes.txt').readlines()        
        actual={cl.strip().replace('ID: ',''):cls[cls.index(cl)+3].strip() for cl in cls if cl.startswith('ID:')}
        
        for k, iter in enumerate(gamma):
            results[articlenames[k]]=[i for i in sorted(enumerate(iter), key=lambda x:x[1], reverse=True) if i[1]>1]
#            print articlenames[k],' Lengths ',len(results[articlenames[k]])
#            
        File=open('./WikiResults/{0}topicdist.txt'.format(prefix), "w+")     
        File2=open('./WikiResults/{0}topiccomparison.txt'.format(prefix), "w+") 
        for key in results:
            File.write('ID: %s \n' % key)
            mytopics=results[key]
            act=actual[key]
            
            if len(mytopics)>0:
                tpname= topicnames[mytopics[0][0]]
                pre=index[tpname]
            else:
                tpname=['Not Available']
                pre='Not Available'
            
            chck=str(act==pre)
           
            ranking='0'
#            print  'act: %s - pre: %s - tname: %s' %(act,pre,tpname)
#            print '%s - %s '%(key,mytopics[0:3])
            for idx, (tname, tvalue) in enumerate(mytopics):
               
                File.write('topic: %s  --  value: %f \n' % (topicnames[tname] , tvalue))
                
                if index[topicnames[tname]]==act and ranking=='0':
#                    print '%s - %s - %s - %s\n' %(key, index[topicnames[tname]], act, idx)
                    ranking=str(idx+1) 
            
            File2.write('ID:%s\t%s\t%s\t%s\t%s\n' % (key, act, pre, chck, ranking))
         #Saving first category comparison
         
         
         
            
if __name__ == '__main__':
    main()
