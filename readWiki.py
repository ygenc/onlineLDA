#!/usr/bin/python

import urllib
import requests 
from xml.dom import minidom
from collections import Counter, OrderedDict
import re
import numpy
from bs4 import BeautifulSoup
from gensim import corpora, models


categories=[]
pages={}
page_wordCounts={}
page_wordFreqs={}
UniversalC=Counter()
UniversalC.__init__()
category_base_url=""
page_base_url="http://en.wikipedia.org/w/api.php?action=query&format=xml&titles={0}&limit=50&prop=revisions&rvprop=content&redirects"
maxLevel=2


docs=[]
articlenames=[]
_lambda=[]
stopwords=[ word.replace('\n','') for word in file('./WikiDocs/Stopwords_English.txt').readlines()]

def ngrams(tokens, MIN_N, MAX_N):
    n_tokens = len(tokens)
    for i in xrange(n_tokens):
        for j in xrange(i+MIN_N, min(n_tokens, i+MAX_N)+1):
            yield tokens[i:j]
       
def find_category( mytitle, level):
     
    my_url=category_base_url.format(mytitle.replace(" ","_"))
    usock=urllib.urlopen(my_url.encode("utf-8"))
    xmldoc=minidom.parse(usock)
    usock.close()
    Cms=xmldoc.getElementsByTagName("cm")
    
    for item in Cms:    
        if item.getAttribute("ns") == "0":
            pages[item.getAttribute("title")]=mytitle
        if item.getAttribute("ns") =="14" and level<maxLevel:
            if item.getAttribute("title") in categories:
                continue
            categories.append(item.getAttribute("title"))
            find_category(item.getAttribute("title"), level+1)
#            print 'parent: ' , mytitle, ' child: ',  item.getAttribute("title"), ' ', level
 
      
        
def get_pages(): 
    print 'Getting pages'
    print len(pages)
    l=len(pages)
    titles=[]
   
    for i in range(0,(l/50)+1):
        start=i*50
        finish= min((i+1)*50,l) 
       
        title="|".join(pages.keys()[start:finish])
  
        try:
            my_url=page_base_url.format(title.encode('utf-8'))
            titles.append(my_url)
        except:
             my_url=page_base_url.format(title)
             titles.append(my_url)
    File2=open('./WikiDocs/wikifiles.txt',"w+")    
    for title in titles:        
#   
        r=requests.get(title)
        xmldoc=minidom.parseString(r.content)
        t_pages=xmldoc.getElementsByTagName("page")
        
     
        for page in t_pages:
            mtitle=None
            try:
                m_title=page.getAttribute('title') 
                m_text= page.getElementsByTagName('rev')[0].firstChild.nodeValue 
                File2.write(re.sub(r'[\s+\n+]', ' ',m_text.encode('utf-8'))+'\n')
                print m_title
                get_count(m_text, m_title)
                docs.append(m_text)
                articlenames.append(m_title)
            except:
                print "can't resolve %s" % m_title
                continue
        
    File2.close()
#            break
#        break
      
        


     
 
def get_count(text , title):
     
    global UniversalC  
    clean=re.sub(r'[\s+\n+]', ' ',text).lower()
    reg=re.compile(r'[^a-z0-9 ]|(http)')
    words=clean.split(' ')
    
    reg2=re.compile(r'(\[\[[0-9a-z \|{1}]*?\]\])')
    phrases=[re.sub(r'[\[\]]','',phrase) for phrase in re.findall(reg2,clean) if phrase.count('|')<2]
    
    '''
     Remove stopwords from the list
    '''
    
    words=[word for word in words if not reg.search(word) and word]
    for phrase in phrases:
        words= words+ [x for x in re.compile('[ \|]').split(phrase) if x]
    
##    print 'before stopwords',len(words)
#    words=[word for word in words if word not in stopwords]
#    print 'after stopwords',len(words)
    total=len(words)
    cnt = Counter()
    for word in words:
        cnt[word] +=1
    fcnt=zip(cnt.keys(), map(lambda x: float(x) / total, cnt.values()))
    page_wordCounts[title]=cnt 
    page_wordFreqs[title]=fcnt
    UniversalC=UniversalC+cnt
    print UniversalC.most_common(5)
    

    '''
    _lambda is the word counts for each wiki page(topic)
    0s are replaced with .01
    '''
def get_lambda(prefix):
    
    vocab = file('./WikiDocs/{0}WIKIDictionary.txt'.format(prefix)).readlines()
    W = len(vocab)
    print 'Populating _lambda for %s words' % (W)
    File=open('./WikiDocs/{0}Topics.txt'.format(prefix),"w+")
    for key, value in page_wordCounts.items():
     #   print 'lambda', key.encode('utf-8')
        File.write(key.encode('utf-8')+'\n')
        
        pcounter=value
        _lambda.append([pcounter[word.replace('\n','')]+1 for word in vocab])    
        
    File.close()    
    '''
    Saving _lambda 
    '''
    numpy.savetxt('./WikiDocs/{0}WIKILambda.txt'.format(prefix), _lambda)
    
   

def save_toFile(prefix): 
    
    ''' Saving word counts per title'''
    File=open('./WikiDocs/{0}WIKIWordCounts.txt'.format(prefix),"w+")
    for key, value in page_wordCounts.items():
        File.write(str(key.encode('utf-8')).replace(r'\s+', '') +'\t'+ str(value) +'\n')
    File.close()
    
    ''' Saving word frequencies (word count/total # of words)  per title'''
    File=open('./WikiDocs/{0}WIKIWordFreqs.txt'.format(prefix),"w+")
    for key, value in page_wordFreqs.items():
        File.write(str(key.encode('utf-8')).replace(r'\s+', '') +'\t'+ str(value) +'\n')
    File.close() 
    
    ''' Saving overall frequencies of each word across all titles'''
    File=open('./WikiDocs/{0}WIKIOverallWordFrequencies.txt'.format(prefix), "w+")
    for key, value in  UniversalC.items():
        File.write(str(key.encode('utf-8')).replace(r'\s+', '') +'\t'+ str(value) +'\n')    
    File.close
    
    '''
    Saving wikipedia dictionary
    '''
    File=open('./WikiDocs/{0}WIKIDictionary.txt'.format(prefix), "w+")
    for key, value in  UniversalC.items():
        File.write(str(key.encode('utf-8')).replace(r'\s+', '') +'\n')    
    File.close


def get_count_entity(filename, topicnames, gamma):
    topics=file(topicnames).readlines()
    topics=[topic.replace('\n','') for topic in topics]
    docs= file(filename).readlines()
   
    for i in range(len(docs)):
        docs[i]= docs[i].replace('\n',' ') + int(gamma)*(topics[i]+ ' ') 
    
    
    texts = [[word for word in clean_entity(doc).split() if word not in stopwords]for doc in docs]
    dictionary = corpora.Dictionary(texts)
    dictionary.save('wiki.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]
     
  
    tfidf = models.TfidfModel(corpus)
    converted= [tfidf[text] for text in corpus]
   
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    corpora.MmCorpus.serialize('tfdif.mm', converted)  
  
  
def clean_entity(doc):
     clean=doc.lower()
     reg=re.compile(r'[^a-z0-9 ]|(http)')
     reg2=re.compile(r'(\[\[[0-9a-z \|{1}]*?\]\])')
#     words=clean.split(' ')
#     cleanwords= [word for word in words if not reg.search(word) and word]
     phrases=[re.sub(r'[\[\]]','',phrase) for phrase in re.findall(reg2,clean) if phrase.count('|')<2]
     words= [[word for word in re.compile('[ \|]').split(phrase) if word] for phrase in phrases   ]
     words=sum(words,[])
#     words = set(word for word in set(words) if words.count(word) > 1)
     return " ".join(words)   
 
def get_count2(filename, topicnames, gamma):
    topics=file(topicnames).readlines()
    topics=[topic.replace('\n','') for topic in topics]
    docs= file(filename).readlines()
   
    for i in range(len(docs)):
        docs[i]= docs[i].replace('\n',' ') + int(gamma)*(topics[i]+ ' ') 
    
    File=file('updatedText.txt','w+')
    for doc in docs:
        File.write(doc+ '\n')
    File.close()
    
    texts = [[word for word in clean(doc).split() if word not in stopwords]for doc in docs]
    dictionary = corpora.Dictionary(texts)
    dictionary.save('wiki.dict')
    corpus = [dictionary.doc2bow(text) for text in texts]
     
  
    tfidf = models.TfidfModel(corpus)
    converted= [tfidf[text] for text in corpus]
   
    corpora.MmCorpus.serialize('corpus.mm', corpus)
    corpora.MmCorpus.serialize('tfdif.mm', converted)
     
def get_lambda2(prefix):
    docs= file('./WikiDocs/wikifiles.txt').readlines()
    corpus = corpora.MmCorpus('corpus.mm')
    tfdif= corpora.MmCorpus('tfdif.mm')
    dictionary= corpora.Dictionary.load('wiki.dict')
    
    for doc in corpus:
        _lambda.append([dict(doc).get(i,1) for i in range(len(dictionary))])
         
    numpy.savetxt('./WikiDocs/{0}WIKILambda.txt'.format(prefix), _lambda)

def get_wordcounts():
    dictionary= corpora.Dictionary.load('wiki.dict')
    ditems=dictionary.items()
    vocab=dictionary.id2token.values()
    ids=[]
    docs=[]
    wordcounts=[]
    for line in  file('./jacm/withIDAbstracts.txt').readlines():
        combo=line.split('\t')
        ids.append(combo[0])
        docs.append(combo[1]) 
     
    for doc in docs: 
        cnt = Counter()
        for word in doc.split(' '):
            cnt[word] +=1 
        wordcounts.append([cnt.get(dictionary.get(i),0) for i in range(len(dictionary))])
        
        
    
    numpy.savetxt('./WikiResults/gensim4_wordcounts.txt', wordcounts)
    
def get_pages2(pages2, filename): 
    print 'Getting pages'
    print len(pages2)
    l=len(pages2)
    titles=[]
   
    for i in range(0,(l/50)+1):
        start=i*50
        finish= min((i+1)*50,l) 
       
        title="|".join(pages2.keys()[start:finish])
  
        try:
            my_url=page_base_url.format(title.encode('utf-8'))
            titles.append(my_url)
        except:
             my_url=page_base_url.format(title)
             titles.append(my_url)
    File2=open(filename,"w+")    
    for title in titles:        
#   
        r=requests.get(title)
        xmldoc=minidom.parseString(r.content)
        t_pages=xmldoc.getElementsByTagName("page")
        
     
        for page in t_pages:
            mtitle=None
            try:
                m_title=page.getAttribute('title') 
                m_text= page.getElementsByTagName('rev')[0].firstChild.nodeValue 
#                File2.write(re.sub(r'[\s+\n+]', ' ',m_text.encode('utf-8'))+'\n')
                File2.write(m_title+'\n')
                print m_title
                get_count(m_text, m_title)
                docs.append(m_text)
                articlenames.append(m_title)
            except:
                print "can't resolve %s" % m_title
                continue
        
    File2.close()    
    
        
def clean(doc):
     clean=doc.lower()
     reg=re.compile(r'[^a-z0-9 ]|(http)')
     reg2=re.compile(r'(\[\[[0-9a-z \|{1}]*?\]\])')
     words=clean.split(' ')
     cleanwords= [word for word in words if not reg.search(word) and word]
     phrases=[re.sub(r'[\[\]]','',phrase) for phrase in re.findall(reg2,clean) if phrase.count('|')<2]
     words= [[word for word in re.compile('[ \|]').split(phrase) if word] for phrase in phrases   ]
     words=sum(words,[])
#     words = set(word for word in set(words) if words.count(word) > 1)
     return " ".join(cleanwords)+" "+" ".join(words) 
  
def get_linksfromfile(filename): 
    global pages
    f=open(filename).read() 
    soup=BeautifulSoup(f) 
    mytitles= [link.get('href').replace('http://en.wikipedia.org/wiki/','') for link in soup.find_all('a')]
    
    for title in mytitles:
        pages[title]='Category'
     
    print len(pages) 
  
def get_jacmcategories(filename, prefix):
    get_linksfromfile(filename)
    get_pages()
    save_toFile(prefix) 
    get_lambda(prefix) 
    
def get_jacm_selected_categories(prefix):
     
    mytitles=file('./jacm/wiki_classIndexCLEAN.txt')
    
    for mtitle in [title.split('\t') for title in mytitles]:
        pages[mtitle[0].strip()]=mtitle[1].strip()
        
    get_pages()
    save_toFile(prefix) 
    get_lambda(prefix)     
    return pages
 

def get_articles():
    get_pages()
    print 'Get articles completed'
    print 'Number of doc: ', len(docs)
    print 'Number of article names', len(articlenames)
    for i, article in enumerate(articlenames):
            print  i,article
    return (docs, articlenames)
    
 
def populate(category, prefix):
    find_category( "Category:%s"%category,1)
    get_pages()
    save_toFile(prefix) 
    get_lambda(prefix)
 
#get_jacmcategories('jacmclass.html', 'class_')



def test():
    mytitles=file('./WikiDocs/wikifiles.txt').readlines()
    
    for i, title in enumerate(mytitles):
        get_count(title.strip(), i)
    
    save_toFile('mapping_')
    
    
#    for mtitle in [title.split('\t') for title in mytitles]:
#        pages[mtitle[0].strip()]=mtitle[1].strip()
#    get_pages()
#    readWiki.get_count2('./WikiDocs/wikifiles.txt', './WikiDocs/gensim2Topics.txt', 10)



    
