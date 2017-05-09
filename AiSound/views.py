#coding=utf-8
from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.http import HttpResponse, StreamingHttpResponse
# from django.core.servers.basehttp import FileWrapper
import mimetypes
from wsgiref.util import FileWrapper
from ZooAI import settings

import jieba
import jieba.analyse
import codecs
from datetime import datetime
#from django.core import serializers
#from django.http import JsonResponse
import json
from textrank4zh import TextRank4Keyword, TextRank4Sentence
import sys
import time
reload(sys)
sys.setdefaultencoding('utf8')
import os
sys.path.append("../")
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
#from whoosh.highlights import *
from jieba.analyse import ChineseAnalyzer
from django.template import loader,Context,RequestContext

# from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
# Create your views here.

# @csrf_protect
@ensure_csrf_cookie
def index(request):
	return render(request,'index.html')

def audio(request):
    fileName = request.GET['name']
    filepath = os.path.join(settings.MEDIA_ROOT, "../Audio/"+fileName+".wav");
    print (filepath)
    wrapper = FileWrapper(open(filepath, 'rb'))
    content_type = mimetypes.guess_type(filepath)[0]
    response = StreamingHttpResponse(wrapper, 'content_type')
    response['Content-Disposition'] = 'attachment; filename="tts_sample.wav"'
    return response

def generate_answer(request):

    audioData = request.FILES.get('audioData',None)
    #生成时间命名的音频文件
    filetime = time.strftime("%Y-%m-%d-%H-%M-%S",time.localtime(time.time()))
    user_upload_folder = "static"
    if not os.path.exists(user_upload_folder):
        os.mkdir(user_upload_folder)
    audioFileName = filetime+".wav"
    file_upload = open(os.path.join("wav/",audioFileName),'w')
    file_upload.write(audioData.read())
    file_upload.close()

    #读取动物数据文件
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

    #音频识别，讲识别结果写入question.txt
    instructs = 'sudo ./iat_sample '+ filetime
    os.system(instructs)
    ques =  open("question.txt","r")
    t = ques.readline()
    #根据问题确定答案
    if t.strip():
        tag1 = jieba.analyse.extract_tags(t,3)
        tag2 = jieba.analyse.textrank(t,3)
        keywords=[]
        print t
        for tag in tag1:
            keywords.append(tag.decode("utf8"))
        for tag in tag2:
            if (tag not in tag1):
                keywords.append(tag.decode("utf8"))
        tr4w = TextRank4Keyword()
        tr4w.analyze(text=t, lower=True, window=2)
        for item in tr4w.get_keywords(20, word_min_len=1):
            if item.word not in keywords:
                keywords.append(item.word)
        kstr=""
        for k in keywords:
                if(len(k)!=1):
                    kstr = kstr + "AND" + k
                else:
                    if k not in kstr:
                        kstr = kstr + "AND" + k
        estr = kstr[3:]
        q = parser.parse(estr)
        results = searcher.search(q)

        if(len(results)==0):
            # f=open('questions_save.txt','a')
            # f.write(t)
            # print('\n太难了，要不换个问法试试')
            str_symptom = '太难了，要不换个问法试试'

            # f.close()
        else:
            # str_symptom = str(results[0]['content'].split(':')[1:]).replace('u\'','\'')
            # print (str_symptom.decode("unicode-escape") )
            # print("="*10)
            str_symptom = str(results[0]['content'].split(':')[1:]).replace('u\'','\'')
            str_symptom = str_symptom.decode("unicode-escape")

    else:
        # print "语音识别未成功！"
        str_symptom = '没听清楚，能不能再说一遍？'
    print (str_symptom )
    instructs = "sudo ./tts_sample "+ filetime+" "+str_symptom
    os.system(instructs)
    while(not os.path.exists(os.path.join("Audio/",filetime+".wav"),)):
        time.sleep(0.5)
        print ("结果音频未完成")
    return HttpResponse(filetime)


# ajax 纯文本交互方式 version 2.0
'''
需启动服务AIZooService，才能使用这个函数
'''
def ajax_answer(request):
    import socket
    question = request.GET['question']
    print question
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect(("localhost", 8888))
    socket.send(question)
    data = str(socket.recv(1024)).decode("utf8")
    print data
    socket.close()

    answer = {}
    answer['content'] = data
    answer_result = []
    answer_result.append(answer)

    results = json.dumps(answer_result)
    return HttpResponse(results, content_type="application/json, charset=utf-8")