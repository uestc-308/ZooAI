#coding=utf-8
from __future__ import unicode_literals
import jieba
import jieba.analyse
import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import sys
reload(sys)   
sys.setdefaultencoding('utf8')
import os
sys.path.append("../")
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
#from whoosh.highlights import *
from jieba.analyse import ChineseAnalyzer
from datetime import datetime

analyzer = ChineseAnalyzer()

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
if not os.path.exists("tmp"):
    os.mkdir("tmp")
ix = create_in("tmp", schema)
writer = ix.writer()

file_name = "panda.txt"

with open(file_name,"rb") as inf:
    i=0
    for line in inf:
	#print(line)
        i+=1
        writer.add_document(
            title="line"+str(i),
            path="/a",
            content=line.decode('utf8','ignore')
        )
writer.commit()

searcher = ix.searcher()
parser = QueryParser("content", schema=ix.schema)
  
while(True):
	t=raw_input("请输入问题:[q退出]")
	if (t!='q'):
		tag1 = jieba.analyse.extract_tags(t,3)
		tag2 = jieba.analyse.textrank(t,3)
		keywords=[]
#print tags.decode("utf-8")
		for tag in tag1:
			keywords.append(tag.decode("utf8"))
		for tag in tag2:
			if (tag not in tag1):
				keywords.append(tag.decode("utf8"))
		'''for keyword in keywords:
			print keyword.decode("utf-8")	
		'''		
		tr4w = TextRank4Keyword()
		tr4w.analyze(text=t, lower=True, window=2)
		for item in tr4w.get_keywords(20, word_min_len=1):
			if item.word not in keywords:
				keywords.append(item.word)
		#for keyword in keywords:
			#print keyword.decode("utf-8")		
				
		kstr=""
		for k in keywords:
			if(len(k)!=1):
				kstr = kstr + "AND" + k
			else:
				if k not in kstr:
					kstr = kstr + "AND" + k
			#print(k)
		estr = kstr[3:]
		print (estr)
		q = parser.parse(estr)
		results = searcher.search(q)
		if(len(results)==0):
			f=open('questions.txt','a')
			now = datetime.now()
			f.write(now.strftime("'%Y-%m-%d %H:%M:%S'")+":")
			f.write(t+"\n")
			print('\n太难了，要不换个问法试试')
			f.close()
		else:
			str_symptom = str(results[0]['content'].split(':')[1:]).replace('u\'','\'')  
			print (str_symptom.decode("unicode-escape") )
			print("="*10)
	else:
		break
