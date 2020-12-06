import requests
import csv
import re
from time import sleep
from lxml import etree
class dangdang_spider():

#定义爬虫类
    def __init__(self):
        self.url="http://category.dangdang.com/pg{}-cp01.00.00.00.00.00.html" 
        self.headers= {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

#爬取基本网页信息
    def parse(self,url):
         r=requests.get(url,headers=self.headers)
         return r.content.decode(encoding='gbk')

#对数据处理
    def handle_data(self, data,i):
        html = etree.HTML(data) #对信息进行html格式化
        msg_list=[]
        li_list=html.xpath("//*[@id='component_59']/li")
        
        for li in li_list:
            msg = {}
            msg['book_title'] = li.xpath('./p/a/text()')[0]
            msg['book-author'] = li.xpath('./p/span[1]/a[1]/@title')[0] if len(li.xpath('./p/span[1]/a[1]/@title')) >0 else '无'
            msg['book-publish'] = li.xpath('./p/span[3]/a/text()')[0] if len(li.xpath('./p/span[3]/a/text()')) >0 else '无'
            msg['book-publish_time'] = li.xpath('./p[5]/span[2]/text()')[0].replace(' /','') if len(li.xpath('./p[5]/span[2]/text()')) >0 else '无'
            msg['book-descrip'] = li.xpath('./p[2]/text()')[0] if len(li.xpath('./p[2]/text()')) >0 else '无'
            msg['book-price'] = li.xpath('./p[3]/span[1]/text()')[0]
            msg['book-pinglun'] = li.xpath('./p[4]/a/text()')[0]
            msg_list.append(msg)
        # print(msg_list)
 
        next_url = self.url.format(i) #构建下一页url
        return msg_list, next_url

#写入数据
    def save_data(self,data):
        for msg in data:
            #处理书名
            if(re.findall(r"(.+?)\（", msg['book_title'])):
                msg['book_title']=re.findall(r"(.+?)\（", msg['book_title'])[0][1:]
            elif(re.findall(r"(.+?)\(", msg['book_title'])):
                msg['book_title']=re.findall(r"(.+?)\(", msg['book_title'])[0][1:]
            elif(re.findall(r"(.+?)\【", msg['book_title'])):
                msg['book_title']=re.findall(r"(.+?)\【", msg['book_title'])[0][1:]        
            elif(re.findall(r"\【(.+?) ", msg['book_title'])):
                msg['book_title']=re.findall(r"\【(.+?) ", msg['book_title'])[0][1:]      
            elif(re.findall(r"(.+?) ", msg['book_title'])):
                msg['book_title']=re.findall(r"(.+?) ", msg['book_title'])[0][1:]     
            elif(re.findall(r"\！(.+?) ", msg['book_title'])):
                msg['book_title']=re.findall(r"\！(.+?) ", msg['book_title'])[0][1:]    
            #构造书籍信息
            msg_str=msg['book_title']+','+msg['book-author']+','+msg['book-publish']+','+msg['book-publish_time']+','+msg['book-descrip']+','+msg['book-price']+','+msg['book-pinglun']
            #print(msg_str)
            with open('bookinfo.csv','a',encoding='utf-8') as f: #写入文件
                f.write(msg_str)
                f.write('\n')

    def run(self):
        i=1
        next_url=self.url.format(i)
        while next_url:
            html_str=self.parse(next_url)
            i = i + 1
            msg_list, next_url=self.handle_data(html_str,i)
            self.save_data(msg_list)
            print("Successfully Get Page",i)
            sleep(2)
            if(i==100):
                return 

if __name__ == '__main__':
    d=dangdang_spider()
    d.run()