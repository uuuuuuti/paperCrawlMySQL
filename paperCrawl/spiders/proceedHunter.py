from paperCrawl.items import PaperItem,ProceedingItem,NewspaperItem,DocmasItem, UnitItem
from paperCrawl.settings import MONGO_URI
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
import logging,re,json,requests,urllib.parse
from lxml import etree
from pymongo import MongoClient
class ProceedSpider(CrawlSpider):
    name = "proceedHunter"
    domains =["http://kns.cnki.net/"]
    crawl_url = "http://kns.cnki.net/kcms/detail/knetsearch.aspx?sfield={sfield}&skey={skey}&code={code}"
    post_url = "http://kns.cnki.net/kcms/detail/frame/knetlist.aspx?code={code}&" \
               "infotype={infotype}&codetype={codetype}&catalogId={catalogId}&catalogName={catalogName}"
    page_url = "http://kns.cnki.net/kcms/detail/frame/knetlist.aspx?code={code}&infotype={infotype}" \
               "&codetype={codetype}&catalogId={catalogId}&catalogName={catalogName}&CurDBCode={curDB}" \
               "&page={curPage}"
    quote_url = "http://kns.cnki.net/kcms/detail/block/refcount.aspx?dbcode={dbcode}&filename={filename}&vl="
    newspaper_url = "http://kns.cnki.net/kcms/detail/frame/asynlist.aspx?dbcode={dbcode}&dbname={dbname}&filename={filename}" \
                    "&curdbcode={curdbcode}&reftype={reftype}&catalogId={catalogId}&catalogName="
    school_url = "http://kns.cnki.net/kcms/detail/frame/asynlist.aspx?dbcode={dbcode}&dbname={dbname}" \
                 "&filename={filename}&curdbcode={curdbcode}&reftype={reftype}&catalogId={catalogId}&catalogName="
    start_urls =[crawl_url.format(sfield='in',skey='中山大学',code='0140250')]

    # exist_urls = []
    # client = MongoClient(MONGO_URI)
    # db = client['zhiwang']
    # paper_collection = db['paper']
    # unit_collection = db['unit']
    # selected_collection = db['selected_unit']

    #读取已存在的paper数据url不再爬取
    # paper_datas = paper_collection.find(
    #     {},{'url':1}
    # )
    # for data in paper_datas:
    #     exist_urls.append(data['url'])
    #读取已存在的unit数据不再爬取
    #exist_units = []
    #unit_datas = unit_collection.find()
    #for u_data in paper_datas:
    #    exist_units.append(u_data['unit_name'])
    #读入start_urls
    #start_urls = []
    #selected_datas = selected_collection.find()
    #for s_data in selected_datas:
    #    skey = s_data['unit_name']
    #    code = s_data['id']
    #    start_urls.append(crawl_url.format(sfield='in',skey=skey,code=code))

    def __init__(self, unit=None, *args, **kwargs):
        super(ProceedSpider, self).__init__(*args, **kwargs)
        client = MongoClient(MONGO_URI)
        client['zhiwang'].authenticate('zhiwang', 'asdasd')
        db = client['zhiwang']
        # 读取已存在的paper数据url不再爬取
        # paper_collection = db['paper']
        # paper_datas = paper_collection.find(
        #    {},{'url':1}
        # )
        # for data in paper_datas:
        #    exist_urls.append(data['url'])
        selected_collection = db['selected_unit'].find({'unit_name': unit})
        code = ""
        for i in selected_collection:
            code = i['id']
        self.start_urls = [self.crawl_url.format(sfield='in', skey=unit, code=code)]

    def parse(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            selector = Selector(response)
            code = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first()
            if code:
                code = code.split('#')[0]
            #unit_name = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first().split('#')[1]
            #unit_location = selector.xpath("//div[@class='info']/div[@class='aboutIntro']/p[3]/text()").extract_first(default=None)

            journal_url = self.post_url.format(code=code, infotype=14, codetype=1,
                                          catalogId='lcatalog_1', catalogName='发表在期刊上的文献')
            doctor_url = self.post_url.format(code=code, infotype=14, codetype=2,
                                         catalogId='lcatalog_2', catalogName='发表在博硕上的文献')
            proceeding_url = self.post_url.format(code=code, infotype=14, codetype=3,
                                             catalogId='lcatalog_3', catalogName='发表在会议上的文献')
            newspaper_url = self.post_url.format(code=code, infotype=14, codetype=4,
                                            catalogId='lcatalog_4', catalogName='发表在报纸上的文献')
            patent_url = self.post_url.format(code=code, infotype=21, codetype='inzl',
                                         catalogId='lcatalog_inzl', catalogName='申请的专利')

            #yield Request(url="http://kns.cnki.net//kcms/detail/detail.aspx?filename=XXWX201003013&dbcode=CJFQ&dbname=CJFD2010&v=",callback=self.parse_paperInfo)
            yield Request(journal_url,
                          meta={
                              'infoType':14,
                              'codeType':1,
                              'catalogId':'lcatalog_1',
                              'catalogName':'发表在期刊上的文献',
                              'code':code
                          },
                          callback=self.parse_page)
            """
            yield Request(doctor_url,
                          meta={
                              'infoType': 14,
                              'codeType': 2,
                              'catalogId': 'lcatalog_2',
                              'catalogName': '发表在博硕上的文献',
                              'code': code
                          },
                          callback=self.parse_docmas_info)
            yield Request(proceeding_url,
                          meta={
                              'infoType': 14,
                              'codeType': 3,
                              'catalogId': 'lcatalog_3',
                              'catalogName': '发表在会议上的文献',
                              'code': code
                          },
                          callback=self.parse_proceeding_info)
            yield Request(newspaper_url,
                          meta={
                              'infoType': 14,
                              'codeType': 4,
                              'catalogId': 'lcatalog_4',
                              'catalogName': '发表在报纸上的文献',
                              'code': code
                          },
                          callback=self.parse_newspaper_info)


            """

    def parse_page(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            code = response.meta['code']
            infotype = response.meta['infoType']
            codetype = response.meta['codeType']
            catalogId = response.meta['catalogId']
            catalogName = response.meta['catalogName']
            selector = Selector(response)
            paper_num = selector.xpath("//b[@class='titleTotle']/span/text()").extract_first()
            cur_db = selector.xpath("//div[@class='pageBar']/span/@id").extract_first()

            papers_url = []
            # 未找到相关数据
            if paper_num is None:
                logging.WARNING('No related data!!!!!!!')
            else:
                # all_paper = []
                page_num = int((int(paper_num) + 10 - 1) / 10)
                i = 1
                while i < page_num + 1:
                    next_url = self.page_url.format(code=code, infotype=infotype, codetype=codetype,
                                                    catalogId=catalogId, catalogName=catalogName, curDB=cur_db,
                                                    curPage=i)
                    i += 1
                    yield Request(url=next_url, callback=self.parse_paper_url)
                    # print(len(self.all_paper))

                    # for url in self.all_paper:
                    #    yield Request(url=url, callback=self.parse_paperInfo)

    def parse_paper_url(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            selector = Selector(response)
            papers_link = selector.xpath("//ul[@class='bignum']/li")
            for link in papers_link:
                paper_url = link.xpath("a[1]/@href").extract_first()
                p_url = self.domains[0] + paper_url
                yield Request(url=p_url, callback=self.parse_proceeding_info)

    def parse_proceeding_info(self, response):
        selector = Selector(response)
        proceeding_id = re.findall(r'filename=\w*', response.url)[0].split('=')[-1]
        dbcode = re.findall(r'dbcode=\w*', response.url)[0].split('=')[-1]
        dbname = re.findall(r'dbname=\w*', response.url)[0].split('=')[-1]
        url = response.url
        title = selector.xpath("//h2[@class='title']/text()").extract_first()

        conference_name = selector.xpath(
            "//label[@id='catalog_HY_NAME']/parent::*/text()").extract_first()
        conference_date = selector.xpath(
            "//label[@id='catalog_DATE']/parent::*/text()").extract_first()
        conference_loc = selector.xpath(
            "//label[@id='catalog_ADDR']/parent::*/text()").extract_first()
        source = selector.xpath(
            "//div[@class='sourinfo']/p[2]/text()").extract_first()
        category = selector.xpath(
            "//label[@id='catalog_ZTCLS']/parent::*/text()").extract_first()
        if category:
            category = category.split(';')
        else:
            category = []
        keywords = []
        keyword = selector.xpath("//label[@id='catalog_KEYWORD']/parent::*/a")
        if keyword:
            for a in keyword:
                keywords.append(a.xpath("text()").extract_first().replace('\r\n', '').replace(' ', '').replace(';', ''))

        abstract = selector.xpath(
            "//label[@id='catalog_ABSTRACT']/parent::*/span/text()").extract_first()

        quote = requests.get(self.quote_url.format(dbcode=dbcode, filename=proceeding_id)).text.replace("'", "\"")
        quote_num = json.loads(quote)['CITING']
        quote2_num = json.loads(quote)['SUB_CITING']
        download_num = selector.xpath(
            "//div[@class='total']/span[@class='a']/b/text()").extract_first()
        authors = []
        author_count = len(selector.xpath("//div[@class='author']/span"))
        item = ProceedingItem(
            id=proceeding_id,
            title=title,
            authors=authors,
            db_code = dbcode,
            db_name = dbname,
            conference_name=conference_name,
            conference_date=conference_date,
            conference_loc=conference_loc,
            source=source,
            category=category,
            url=url,
            keywords=keywords,
            abstract=abstract,
            quote_num=quote_num,
            quote2_num=quote2_num,
            download_num=download_num
        )
        for span in selector.xpath("//div[@class='author']/span"):
            author_info = span.xpath("a/@onclick").extract_first()
            au_type = re.findall(r"'\w*'", author_info)[0].replace('\'', '')
            au_name = span.xpath("a/text()").extract_first()
            au_code = author_info.split('\',\'')[-1].split('\')')[0]
            author_url = self.crawl_url.format(sfield=au_type, skey=au_name, code=au_code)
            yield Request(url=author_url,
                          meta={
                              'item': item,
                              'author_count': author_count
                          },
                          callback=self.parse_author_info)

    def parse_author_info(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            selector = Selector(response)
            item = response.meta['item']
            au_code = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first()
            if au_code:
                au_code = au_code.split('#')[0]
                au_name = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first()
                if au_name:
                    au_name = au_name.split('#')[1]
                au_orgn = selector.xpath("//p[@class='orgn']/a/@onclick").extract_first()
                au_orgn_name = selector.xpath("//p[@class='orgn']/a/text()").extract_first()
                if au_orgn:
                    au_orgn_code = re.findall(r"'\w*'", au_orgn)[-1].replace('\'', '')
                else:
                    au_orgn_code = None
                au_doma = selector.xpath("//p[@class='doma']/text()").extract_first()
                if au_doma:
                    au_doma = au_doma.split(';')
                if '' in au_doma:
                    au_doma.remove('')
                au_url = self.crawl_url.format(sfield='au', skey=au_name, code=au_code)
                author = {'author_name': au_name, 'author_code': au_code,
                          'author_orgn_name': au_orgn_name, 'author_orgn_code': au_orgn_code,
                          'author_domain': au_doma, 'author_first': response.meta['au_first'], 'author_url': au_url}

                item['authors'].append(author)
                if len(item['authors']) == response.meta['author_count']:
                    quote_url = self.quote_url.format(dbcode=response.meta['dbcode'], filename=item['id'])
                    yield Request(quote_url, meta={
                        'item': item
                    }, callback=self.parse_quote_info)

            else:
                au_name = response.url.split('&skey=')[-1].split('&')[0]
                au_name = urllib.parse.unquote(au_name)
                au_code = response.url.split('&code=')[-1].replace(';', '')
                au_url = self.crawl_url.format(sfield='au', skey=au_name, code=au_code)
                if response.meta['au_first'] == True:
                    # au_orgn_name = item['organizations'][0]['orgn_name'].split()[0]
                    au_orgn_code = item['organizations'][0]['orgn_code']
                else:
                    # au_orgn_name = item['organizations'][len(item['organizations']) - 1]['orgn_name'].split()[0]
                    au_orgn_code = item['organizations'][len(item['organizations']) - 1]['orgn_code']
                author = {'author_name': au_name, 'author_code': au_code, 'author_orgn_name': "",
                          'author_orgn_code': au_orgn_code,
                          'author_domain': "", 'author_first': response.meta['au_first'], 'author_url': au_url}
                item['authors'].append(author)
                # logging.info(response.meta['author_count'])
                if len(item['authors']) == response.meta['author_count']:
                    quote_url = self.quote_url.format(dbcode=response.meta['dbcode'], filename=item['id'])
                    yield Request(quote_url, meta={
                        'item': item
                    }, callback=self.parse_quote_info)

    def parse_quote_info(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            quote = response.body_as_unicode().replace("'", "\"")
            quote_num = json.loads(quote)['CITING']
            quote2_num = json.loads(quote)['SUB_CITING']
            item = response.meta['item']
            item['quote_num'] = quote_num
            item['quote2_num'] = quote2_num
            yield item

