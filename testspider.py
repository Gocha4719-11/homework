import scrapy

class TestspiderSpider(scrapy.Spider):
    handle_httpstatus_list = [404]
    name = "testspider"
    allowed_domains = ["merchantpoint.ru"]
    id_number = 3
    start_urls = ["https://merchantpoint.ru/brand/1"]

    def parse(self, response):
        org_description_list= response.xpath("//div[contains(@class, 'tab-pane container')]//div[@class='form-group mb-2']//p[2]/text()").getall()
        hrefs=response.xpath('//div[@class="table-responsive"]//a/@href').getall()
        org_description = ''
        next_page='https://merchantpoint.ru/brand/1'
        for i in org_description_list:
            org_description+=str(i)
        for href in hrefs:

            yield scrapy.Request(
                url=response.urljoin(href),
                callback=self.parse_points,
                meta={
                    'link':next_page,
                    "org_description": org_description
                }
            )
            yield scrapy.Request(url=response.urljoin(href),
                                 callback=self.parse_points
                                 )
        next_page = 'https://merchantpoint.ru/brand/' + str(TestspiderSpider.id_number) + '/'
        if TestspiderSpider.id_number <300:
            TestspiderSpider.id_number+=1
            yield response.follow(next_page, callback=self.parse)

    def parse_points(self, response):
        org_name = response.xpath("//div[@class='col-lg-10 mt-3']//a/text()").extract_first()
        merchant_name = response.xpath("//p[contains(., 'MerchantName')]/text()").extract()
        merchant_name=str(merchant_name[0])
        merchant_name=merchant_name[3:]
        mcc = response.xpath("//p[contains(., 'MCC код')]/a/text()").extract()
        if len(mcc)==0:
            mcc= 'no mcc'
        address = response.xpath("//p[contains(., 'Адрес торговой ')]/text()").extract()
        if len(address) == 0:
            address='no address'
        geo_coordinates = response.xpath("//p[contains(., 'Геокоординаты')]/text()").extract()
        if len(geo_coordinates) == 0:
            geo_coordinates='no coordinates'
        org_description = response.meta.get('org_description')
        org_description = org_description.replace('\n', '')
        if len(org_description) == 0:
            org_description = 'no description'
        source_url = response.meta.get('link')

        return {'org_name': org_name,'merchant_name': merchant_name, 'mcc': mcc, 'address': address, 'geo_coordinates': geo_coordinates, 'org_description': org_description, 'link': source_url}
