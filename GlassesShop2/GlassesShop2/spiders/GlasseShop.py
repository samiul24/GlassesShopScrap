import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class GlasseshopSpider(CrawlSpider):
    name = 'GlasseShop'
    allowed_domains = ['www.glassesshop.com']
    #start_urls = ['https://www.glassesshop.com/']

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

    def start_requests(self):
        yield scrapy.Request(url='https://www.glassesshop.com/', headers={
            'User-Agent': self.user_agent
        })

    rules = (
        Rule(LinkExtractor(restrict_xpaths="//ul/li/div/div[@class='container clearfix']/dl/dd/a"),
        callback='parse_item', follow=True, ),
    )

    def set_user_agent(self, request):
        request.headers['User-Agent'] = self.user_agent
        return request

    def parse_item(self, response):
        product_category = response.xpath("//div[@class='container']/nav/ol/li[2]/text()").get()
        product_links = response.xpath("//div[@id='product-lists']/div/div[@class='product-img-outer']/a[1]")
        for product_link in product_links:
            product_link = product_link.xpath(".//@href").get()
            yield response.follow(url=product_link, callback=self.product_info, meta={'product_category':product_category})

        next_page = response.xpath("//li[@class='page-item']/a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(url=next_page, dont_filter = True, callback=self.parse_item)


    def product_info(self, response):
        product_category = response.request.meta['product_category']
        product_name = response.xpath("//div[@class='d-lg-block d-none']/h1/text()").get().strip()
        try:
            product_price = response.xpath(".//div/span[@class='product-price-original']/text()").get()
            if product_price is None or product_price == '':
                product_price = response.xpath("//div[@class='d-lg-block d-none']/span[@class='product-price-cur']/text()").get()
        except:
            product_price = response.xpath("//div[@class='d-lg-block d-none']/span[@class='product-price-cur']/text()").get()
        yield{
            'product_category': product_category,
            'product_name': product_name,
            'product_price': product_price,
                
            }
