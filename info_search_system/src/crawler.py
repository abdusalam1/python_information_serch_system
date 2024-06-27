import requests  # type: ignore
from lxml import etree  # type: ignore
from lxml import html
import operator

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    # 可以添加其他HTTP头信息
}


def cnew_data():
    count = 1
    text = []
    for i in range(0, 92):
        url = f"https://www.gov.cn/zhengce/zuixin/home_{i}.htm"
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            resHtml = etree.HTML(req.content.decode("utf-8"))
            for liIndex in range(1, 21):
                titles = resHtml.xpath(
                    f'//*[@class="list list_1 list_2"]/ul/li[{liIndex}]/h4/a/text()'
                )
                hrefs = resHtml.xpath(
                    f'//*[@class="list list_1 list_2"]/ul/li[{liIndex}]/h4/a/@href'
                )
                if titles and hrefs:
                    for title in titles:
                        for href in hrefs:
                            if operator.contains(f"{href}", ".."):
                                url1 = "https://www.gov.cn/zhengce" + href[2:]
                            else:
                                url1 = href
                            req1 = requests.get(url1, headers=headers)
                            resHtml1 = etree.HTML(req1.content)
                            tree = html.fromstring(req1.content)
                            elements = tree.xpath("//div[@id='UCAP-CONTENT']")
                            for element in elements:
                                text.append(element.text_content())
                            try:
                                with open(f"{title}.txt", "w", encoding="utf-8") as f:
                                    for item in text:
                                        f.write(item + "\n")
                                    text = []
                                    count += 1

                                print(count)
                            except:
                                pass
                else:
                    print(f"No titles found for item {liIndex}")

        else:
            print(f"Failed to retrieve data from {url}. Status code: {req.status_code}")

    # 打印结果前确保控制台支持UTF-8编码（通常在Windows上需要设置）


if __name__ == "__main__":
    cnew_data()
