
import requests
from lxml import etree
from tqdm import tqdm
 
 
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}
 
 
# 组合日期链接
def cnew_url():
    f = open(r'cnew_url.txt', 'w', encoding='utf8')
    for i in range(1, 32):
        if i < 10:
            url = 'https://www.chinanews.com.cn/scroll-news/2024/050' + str(i) + '/news.shtml'
        else:
            url = 'https://www.chinanews.com.cn/scroll-news/2024/05' + str(i) + '/news.shtml'
        f.write(url + '\n')
    f.close()
 
def cnew_data():  
    with open(r'src/cnew_url.txt', encoding='utf8') as f  :  # 打开一个新的txt文件用于写入数据  
        for i in f:  
            url = i.strip()  # 去除换行符  
            req = requests.get(url, headers=headers)  
            req.encoding = 'utf8'  
            ht = etree.HTML(req.text)  
            fl = ht.xpath("//div[@class='dd_lm']/a/text()")  
            lj = ht.xpath("//div[@class='dd_bt']/a/@href")  
            lj1 = []  
            for j in lj:  
                if j[:5] == '//www':  
                    lj1.append('https:' + j)  
                else:  
                    lj1.append('https://www.chinanews.com.cn/' + j)  
            for k in tqdm(lj1):  
                try:  
                    reqs = requests.get(k, headers=headers, timeout=10)  
                    reqs.encoding = 'utf8'  
                    ht1 = etree.HTML(reqs.text)  
                    bt = ht1.xpath("//h1[@class='content_left_title']/text()")  # 标题  
                    if bt:  
                        title = bt[0]  
                        intro = '\n'.join(ht1.xpath("//div[@class='left_zw']/p/text()"))  # 简介  
                    else:  
                        title = ht1.xpath("//div[@class='content_title']/div[@class='title']/text()")[0]  
                        intro = '\n'.join(ht1.xpath("//div[@class='content_desc']/p/text()"))  # 简介  
                    # 写入标题和简介到txt文件  
                    fname=title+'.txt'
                    with open(fname, 'w', encoding='utf8') as outfile:
                        outfile.write(f"标题: {title}\n")  
                        outfile.write(f"简介: {intro}\n\n")  
                except Exception as e:  
                    print(f"Error fetching data from {k}: {e}")
 
 
if __name__ == '__main__':
    # cnew_url()
    cnew_data()