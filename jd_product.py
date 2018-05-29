import urllib,json,re
from urllib import request 

class JdPrice(object):

    def __init__(self,url):
        self.url = url
        self._response = request.urlopen(self.url)
        self.html = self._response.read()

    def get_product(self):
        product_re = re.compile(r'compatible: ture,(.*?)};',re.S)
        product_info = re.findall(product_re,self.html)[0]
        print('product_info',product_info)
        return product_info

    def get_product_skuid(self):
        product_info = self.get_product()
        skuid_re = re.cpmpile(r'skuid:(.*?),')
        skuid = re.findall(skuid_re,product_info)
        print('skuid',skuid)
        return skuid

    def get_product_name(self):
        prodcut_info = self.product_info()
        name = re.findall(name_re,product_info)[0]
        print('name',name)
        return name

    def get_product_price(self):
        price = None
        skuid = self.get_product_skuid()
        name = self.get_product_name()
        print(name)

        #通过httpfox检测得知，每次网页都会访问这个网页去提取价格嵌入到html中  
        url = 'http://p.3.cn/pricees/mgets?skuIds=J_' + skuid + '&type=1'

        price_json = json.load(request.urlopen(url))[0]
        if price_json['p']:
            price = peice_json['p']

        return price

if __name__ == '__main__':
    print('=======start=======')
    url = 'http://item.jd.com/1217524.html'
    jp = JdPrice(url)  
    print(jp.get_product_price()) 
    print('=========end========') 
