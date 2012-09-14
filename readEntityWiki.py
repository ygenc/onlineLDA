#!/usr/bin/python

import urllib
import requests 
from xml.dom import minidom
from collections import Counter, OrderedDict
import re
import numpy
from bs4 import BeautifulSoup
from gensim import corpora, models
import pickle
import threading, time
 

page_title_check_url= "http://en.wikipedia.org/w/api.php?action=query&format=xml&titles={0}&limit=50&redirects"
category_disam_check_url='http://en.wikipedia.org/w/api.php?action=query&format=xml&titles={0}&prop=categories&rvprop=content&redirects&cllimit=500'
backlinks_url="http://en.wikipedia.org/w/api.php?action=query&format=xml&blnamespace=0&list=backlinks&blredirect&bllimit=500&bltitle={0}{1}"
inlinks_url="http://en.wikipedia.org/w/api.php?action=query&prop=links&format=xml&titles={0}&pllimit=500&limit=500&redirects{1}"
stopwords=[ word.replace('\n','') for word in file('./WikiDocs/Stopwords_English.txt').readlines()]
Entities=[]
Tokens={}

entities={}
ids=[]
docs=[]


def get_lambda(TopicEntityFile1,TopicEntityFile2=''):
    _lambda=[]
    tokens_dict=eval(file('Entity/tokens.txt').read())
    tokens=[l for l in set(tokens_dict.values())]
    
    
    tnames,topics=zip(*[(topic.split('\t')) for topic in file(TopicEntityFile1).readlines()  ])
    topics=[eval(t.replace('\n','')) for t in topics]
    

    
    
    for key, topic in enumerate(topics):
          tlambda=[topic.count(val)+ 1 for val in tokens]
          for i in range(len(tlambda)):
              if tokens[i]==tnames[key]:
                  tlambda[i]=(tlambda[i]- 1)*2.+ 1
                  print tnames[key], ' ', i, ' ',key  
          _lambda.append(tlambda)
          
    if TopicEntityFile2!='':
        tnames2,topics2=zip(*[(topic.split('\t')) for topic in file(TopicEntityFile2).readlines()  ])      
        topics2=[eval(t.replace('\n','')) for t in topics2]
        
   
    
        for key, tlamda in enumerate(_lambda):
#            print 'key ',key
#            print topics2[key]
            for i in range(len(tlamda)):               
                if tokens[i] in topics2[key]:
#                     print tokens[i]
                     tlambda[i]=tlambda[i]+ .5*(topics2[key].count(tokens[i]))    
        
    numpy.savetxt('./Entity/WIKILambda.txt', _lambda)
    
    
def get_pages():
   
    mytitles=file('./jacm/wiki_classIndexCLEAN.txt').readlines()
    topic_pages=[title.split('\t')[0].strip() for title in mytitles]

    topic_Entities={}
    
    File=file('./Entity/TopicEntities.txt', 'w+')
    for topic in topic_pages:
        topic_Entities[topic]=get_backlinks(topic)
        File.write('%s\t%s\n'%(topic,topic_Entities[topic]))
    File.close()
    
def get_pages2():
   
    mytitles=file('./jacm/wiki_classIndexCLEAN.txt').readlines()
    topic_pages=[title.split('\t')[0].strip() for title in mytitles]

    topic_Entities={}
    
    File=file('./Entity/TopicEntitiesLink.txt', 'w+')
    for topic in topic_pages:
        topic_Entities[topic]=get_links(topic)
        File.write('%s\t%s\n'%(topic,topic_Entities[topic]))
    File.close()    

def get_backlinks(title,cntid=''):
   
    my_bl_url=backlinks_url.format(title,cntid)
    print  my_bl_url
    r=requests.get(my_bl_url)
    soup=BeautifulSoup(r.content)
    links=[tag['title'] for tag in soup.find_all('bl')]
    
    if soup.find('backlinks', {'blcontinue':True})==None:

        return links
    else:
        cnt='&blcontinue='+soup.find('backlinks', {'blcontinue':True})['blcontinue']
 
        return links+get_backlinks(title,cnt)
    
def get_links(title,cntid=''):
   
    my_bl_url=inlinks_url.format(title,cntid)
    print  my_bl_url
    r=requests.get(my_bl_url)
    soup=BeautifulSoup(r.content)
    links=[tag['title'] for tag in soup.find_all('pl')]
    
    if soup.find('links', {'plcontinue':True})==None:

        return links
    else:
        cnt='&plcontinue='+soup.find('links', {'plcontinue':True})['plcontinue']
 
        return links+get_backlinks(title,cnt)
    
    
def populate_Entities(input_filename,output_filename):
    global entities
    global ids
    global docs
    global Tokens
   
    for line in  file(input_filename).readlines():
        combo=line.split('\t')
        ids.append(combo[0])
        docs.append(combo[1]) 
#    File=open(output_filename,'w+')
    
    threads = []
    for key,doc in enumerate(docs):
        t = threading.Thread(target=worker, args=(key,doc))
        threads.append(t)
        t.start()

    while threading.activeCount()>1:
        time.sleep(10)
        print 'Active thread count: ',threading.activeCount()
    
    #Remove the entities that are categoirezed under disambiguation categories
    remove_disambiguation()
    
    #save entities and their counts per text
    File=open(output_filename,'w+')
    for key,value in entities.items():
        value=[v[0:3] for v in value if v[0] in Tokens.values()]
        File.write('%s\t%s\n'%(key,value))
        File.flush()
    File.close    

#for multithreading
def worker(key, value):
    entities[ids[key]]=get_Entities(get_candidates(value,3))
    print key,' Done' 
    
    return

#chunks the text into n grams and cleans the text    
def get_candidates(text, max_n):
    global Tokens
    text=re.sub(r'\s+', ' ',re.sub(r'[^a-z0-9\'-_ ]',' ',text.lower()))
    pages=[" ".join(page) for page in [p for p in ngrams(text.split(' '), 1, 3)]]
    entity_dict=dict([(x, pages.count(x)) for x in set(pages) ])
    
    return entity_dict
    

def ngrams(tokens, MIN_N, MAX_N):
    n_tokens = len(tokens)
    for i in xrange(n_tokens):
        for j in xrange(i+MIN_N, min(n_tokens, i+MAX_N)+1):
            yield tokens[i:j]
       
#find wiki Entities in the candidates (cleaned n-grams)
def get_Entities(candidates ): 
    global Tokens
    print 'Getting pages'
    print len(candidates)
    entities=[]
     
    existing=[candidate for candidate in candidates.keys() if candidate in Tokens.keys()]
    for exists in existing:
        entities.append((Tokens[exists], exists, candidates.get(exists,0)))
     
    for e in existing:
        candidates.pop(e)
    l=len(candidates)
     
    URLs=populate_URLS(page_title_check_url,candidates.keys(),50)
    
   
    for url in URLs:        
        r=requests.get(url)
        soup=BeautifulSoup(r.content)
        ExistingTags=soup.findAll( 'page',{'pageid': True} ) 
        existing_titles=[page['title'] for page in ExistingTags]
        for title in existing_titles:
            ''' Check for dambiguity''' 
            try:
                tfrom=soup.find(['r','n'],to=title)['from']
            except:
                tfrom=title
                print 'can\'t find %s' %title    
            entities.append((title, tfrom, candidates.get(tfrom.lower(),0)))
            Tokens[tfrom]=title
        xmldoc=minidom.parseString(r.content)
        t_pages=xmldoc.getElementsByTagName("page")

    return entities 


# final step in populate_Entities, removes the disambiguations
def remove_disambiguation():
    global Tokens
    disam_titles=[] 
    URLs=populate_URLS(category_disam_check_url,Tokens.values(),25)
   
    for url in URLs:
        r=requests.get(url)
        soup=BeautifulSoup(r.content)
        disam_cats=soup.findAll('cl', title=re.compile('isambiguation|English grammar'))
        my_disam_titles=[disam.findParent('page')['title'] for disam in disam_cats]
        my_disam_titles=[disam for disam in set(my_disam_titles)]
        disam_titles+=my_disam_titles

    Tokens= {key:value for key,value in Tokens.items() if value not in disam_titles}
    File=open('./Entity/disam.txt','w+')
    File.write(str(disam_titles))
    File.close()
    
    File=open('./Entity/tokens.txt','w+')
    File.write(str(Tokens))
    File.close()
    
    print "Disams ",len(disam_titles)
    print  "Tokens", len(Tokens)
    
def populate_URLS(base_url, item_array,limit):
    l=len(item_array)
    URL=[]
    for i in range(0,(l/limit)+1):
        start=i*limit
        finish= min((i+1)*limit,l) 
        
        url="|".join(item_array[start:finish])   
        try:
            my_url=base_url(url.encode('utf-8'))
            URL.append(my_url)
            
        except:
            try:
                my_url=base_url.format(url)
                URL.append(my_url)
            except:
                continue
    return URL