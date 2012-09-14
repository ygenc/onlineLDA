from bs4 import BeautifulSoup
import requests
import os




def get_class(id): 
    r=requests.get('http://dl.acm.org/citation.cfm?id=%s&preflayout=flat'%id)
    soup=BeautifulSoup(r.content)
    cls=''  
    for node in soup.find_all('p',attrs={"class" : "Categories"}):
        cls=cls+''.join(node.findAll(text=True))
    clsclean= os.linesep.join([s for s in cls.splitlines() if s.replace(' ','')])
    return clsclean
 

File=open('./jacm/Classes.txt','w+')
ids=[id.replace('\n','') for id in open('./jacm/ID2s.txt').readlines()]
for id in ids:
    if id=='': continue
    print id
    File.write('ID: %s \n %s \n\n' %(id, get_class(id)))
    File.flush()
  

 

