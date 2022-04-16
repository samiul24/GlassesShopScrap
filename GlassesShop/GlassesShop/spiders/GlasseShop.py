import scrapy


class GlasseshopSpider(scrapy.Spider):
    name = 'GlasseShop'
    allowed_domains = ['www.glassesshop.com']
    start_urls = ['https://www.glassesshop.com/']

    def parse(self, response):
        menu_links = response.xpath("//ul/li/div/div[@class='container clearfix']/dl/dd/a")

        for menu_link in menu_links:
            try:
                menu_title = (menu_link.xpath(".//text()").get()).strip()
            except:
                print('No title')

            if menu_title == '\n' or menu_title == '':
                try:
                    menu_title = (menu_link.xpath(".//@title").get()).strip()
                except:
                    menu_title = (menu_link.xpath(".//span[2]/text()").get()).strip()

            menu_title = " ".join(menu_title.split())
            menu_link = (menu_link.xpath(".//@href").get()).strip()
            
            yield response.follow(url=menu_link, dont_filter = True, callback=self.menu_link_process, meta={'menu_title': menu_title})

    
    def menu_link_process(self, response):
        menu_title = response.request.meta['menu_title']
        menu_link = response.url
        product_links = response.xpath("//div[@id='product-lists']/div/div[@class='product-img-outer']/a[1]")
        for product_link in product_links:
            product_link = product_link.xpath(".//@href").get()
            yield response.follow(url=product_link, dont_filter = True, callback=self.product_info_process, 
            meta={'menu_title': menu_title, 'menu_link': menu_link,})
        
        next_page = response.xpath("//li[@class='page-item']/a[@rel='next']/@href").get()
        if next_page:
            print(1)
            yield response.follow(url=next_page, dont_filter = True, callback=self.menu_link_process, 
            meta={'menu_title': menu_title, 'menu_link': menu_link,})
        

    def product_info_process(self, response):
        menu_title = response.request.meta['menu_title']
        menu_link = response.request.meta['menu_link']
        product_name = (response.xpath("//div[@class='d-lg-block d-none']/h1[@class='product-info-title']/text()").get()).strip()
        product_name = " ".join(product_name.split())
        try:
            product_price = response.xpath("//div/span[@class='product-price-original']/text()").get()
            if product_price is None or product_price == '':
                product_price = response.xpath("//div[@class='d-lg-block d-none']/span[@class='product-price-cur']/text()").get()
        except:
            product_price = response.xpath("//div[@class='d-lg-block d-none']/span[@class='product-price-cur']/text()").get()
        yield{
                #'menu_title': menu_title,
                #'menu_link': menu_link,
                #'product_link': product_link,
                'name': product_name,
                'price': product_price,
                'url': response.url,
            }

