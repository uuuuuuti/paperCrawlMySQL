from paperCrawl.items import PaperItem,ProceedingItem,NewspaperItem,DocmasItem, UnitItem
from paperCrawl.settings import MONGO_URI
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
import logging,re,json,requests,urllib.parse
from lxml import etree
from pymongo import MongoClient
class PaperSpider(CrawlSpider):
    name = "paperHunter"
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

    exist_urls = []
    client = MongoClient(MONGO_URI)
    client['zhiwang'].authenticate('zhiwang', 'asdasd')
    db = client['zhiwang']
    paper_collection = db['paper']
    unit_collection = db['unit']
    selected_collection = db['selected_unit']

    #读取已存在的paper数据url不再爬取
    paper_datas = paper_collection.find(
        {},{'url':1}
    )
    for data in paper_datas:
        exist_urls.append(data['url'])
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
                yield Request(url=p_url, callback=self.parse_paperInfo)

    def parse_paperInfo(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            selector = Selector(response)

            paper_id = re.findall(r'filename=\w*', response.url)[0].split('=')[-1]
            dbcode = re.findall(r'dbcode=\w*', response.url)[0].split('=')[-1]
            title = selector.xpath("//div[@class='wxTitle']/h2[@class='title']/text()").extract_first()

            journal = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[@class='title']/a/text()").extract_first()
            journal_eng = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[2]/a/text()").extract_first()
            issn = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[4]/text()").extract_first()
            if issn:
                issn = issn.split('：')[-1]
            pub_date = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[3]/a/text()").extract_first()
            if pub_date:
                pub_date = pub_date.replace('\r\n', '').replace(' ', '')
            category = selector.xpath("//label[@id='catalog_ZTCLS']/parent::*/text()").extract_first()
            if category:
                category = category.split(';')
            else:
                category = []
            doi = selector.xpath("//label[@id='catalog_ZCDOI']/parent::*/text()").extract_first(default="")
            url = response.url
            keywords = []
            keyword = selector.xpath("//label[@id='catalog_KEYWORD']/parent::*/a")
            if keyword:
                for span in keyword:
                    keywords.append(
                        span.xpath("text()").extract_first().replace('\r\n', '').replace(' ', '').replace(';', ''))
            abstract = selector.xpath("//label[@id='catalog_ABSTRACT']/parent::*/span[1]/text()").extract_first()
            fund = []
            funds = selector.xpath("//label[@id='catalog_FUND']/parent::*/a")
            if funds:
                for span in funds:
                    fund.append(
                        span.xpath("text()").extract_first().replace('\r\n', '').replace(' ', '').replace('；', ''))
            organizations = []
            organizations_span = selector.xpath("//div[@class='orgn']/span/a")
            if organizations_span:
                for index in range(len(organizations_span)):
                    org_info = organizations_span[index].xpath("@onclick").extract_first()
                    # org_type = re.findall(r"'\w*'", org_info)[0].replace('\'', '')
                    org_name = organizations_span[index].xpath("text()").extract_first().replace('\r\n', '').replace(
                        ' ', '')
                    org_code = org_info.split('\',\'')[-1].split('\')')[0]
                    orgn_detial_info = {'orgn_name': org_name, 'orgn_code': org_code}
                    organizations.append(orgn_detial_info)
            # quote = requests.get(self.quote_url.format(dbcode=dbcode,filename=paper_id)).text.replace("'", "\"")
            # quote_num = json.loads(quote)['CITING']
            # quote2_num = json.loads(quote)['SUB_CITING']

            download_num = selector.xpath(
                "//div[@class='wxmain']/div[@class='wxInfo']/div[@class='wxBaseinfo']/div[@class='total']/span[@class='a']/b/text()").extract_first()
            if download_num:
                download_num = download_num.replace(
                    '(', '').replace(')', '')
            else:
                download_num = 0
            # quote = [quote_num,quote2_num]
            # print(quote)
            authors = []
            author_count = len(selector.xpath("//div[@class='author']/span"))
            # author_count = len(selector.xpath("//div[@class='author']/span/a/text()").extract_first().split('\n'))
            # 收集作者信息
            item = PaperItem(
                id=paper_id,
                title=title,
                authors=authors,
                journal=journal,
                journal_eng=journal_eng,
                issn=issn,
                db_code=dbcode,
                pub_date=pub_date,
                category=category,
                organizations=organizations,
                doi=doi,
                url=url,
                keywords=keywords,
                abstract=abstract,
                fund=fund,
                # quote_num = quote_num,
                # quote2_num = quote2_num,
                download_num=download_num
            )

            for index in range(len(selector.xpath("//div[@class='author']/span"))):
                span = selector.xpath("//div[@class='author']/span")
                author_info = span[index].xpath("a/@onclick").extract_first()
                au_type = re.findall(r"'\w*'", author_info)[0].replace('\'', '')
                au_name = span[index].xpath("a/text()").extract_first()
                au_code = author_info.split('\',\'')[-1].split('\')')[0]
                if index == 0:
                    au_first = True
                else:
                    au_first = False
                author_url = self.crawl_url.format(sfield=au_type, skey=au_name, code=au_code)
                yield Request(url=author_url,
                              meta={
                                  'item': item,
                                  'author_count': author_count,
                                  'dbcode': dbcode,
                                  'au_first': au_first
                              },
                              dont_filter=True,
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

    def parse_proceeding_info(self,response):
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
        keywords =[]
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
            id = proceeding_id,
            title = title,
            authors = authors,
            conference_name = conference_name,
            conference_date = conference_date,
            conference_loc = conference_loc,
            source = source,
            category = category,
            url = url,
            keywords = keywords,
            abstract = abstract,
            quote_num = quote_num,
            quote2_num = quote2_num,
            download_num = download_num
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

    def parse_newspaper_info(self,response):
        selector = Selector(response)
        newspaper_id = re.findall(r'filename=\w*', response.url)[0].split('=')[-1]
        dbcode = re.findall(r'dbcode=\w*', response.url)[0].split('=')[-1]
        dbname = re.findall(r'dbname=\w*', response.url)[0].split('=')[-1]
        title = selector.xpath("//div[@class='wxTitle']/h2[@class='title']/text()").extract_first()
        abstract = selector.xpath("//span[@id='ChDivSummary']/text()").extract_first()
        layout_name = selector.xpath("//label[@id='catalog_LM']/parent::*/text()").extract_first()
        layout_num = selector.xpath("//label[@id='catalog_BH']/parent::*/text()").extract_first()
        pub_date = selector.xpath("//label[@id='catalog_DATE']/parent::*/text()").extract_first()
        download_num = selector.xpath("//div[@class='total']/span[@class='a']/b/text()").extract_first()
        #报纸信息需要构造url获取
        newspaper = selector.xpath("//script/text()").re(r"WriteToPage\('(\w*)','(\w*)','(\w*)','(\w*)','(\w*)'\)")
        param_1 = newspaper[0]
        param_2 = newspaper[1]
        param_3 = newspaper[2]
        param_4 = newspaper[3]
        param_5 = newspaper[4]
        post_newspaper_url = self.newspaper_url.format(dbcode=param_3,dbname=param_2,filename=param_1,
                                                       curdbcode=param_4,reftype=param_5,catalogId='lcatalog_func'+param_5)
        html = requests.get(post_newspaper_url).content
        sele = etree.HTML(html)
        newspaper_name = sele.xpath("//div[@class='sourinfo']/p[1]/a/text()")[0]
        newspaper_loc = sele.xpath("//div[@class='sourinfo']/p[2]/text()")[0]
        newspaper_rank = sele.xpath("//div[@class='sourinfo']/p[4]/text()")[0]
        newspaper_url = sele.xpath("//div[@class='sourinfo']/p[5]/a/text()")[0]
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
        authors = []
        author_count = len(selector.xpath("//div[@class='author']/span"))
        item = NewspaperItem(
            id = newspaper_id,
            title = title,
            abstract = abstract,
            layout_name = layout_name,
            layout_num = layout_num,
            pub_date = pub_date,
            category = category,
            keywords = keywords,
            newspaper_name = newspaper_name,
            newspaper_loc= newspaper_loc,
            newspaper_rank = newspaper_rank,
            newspaper_url = newspaper_url,
            download_num = download_num,
            authors = authors
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

    def parse_docmas_info(self,response):
        selector = Selector(response)
        title = selector.xpath("//div[@class='wxTitle']/h2[@class='title']/text()").extract_first()
        id = response.url.split('=',1)[1].split('&',1)[0]
        dbcode = re.findall(r'dbcode=\w*', response.url)[0].split('=')[-1]
        dbname = re.findall(r'dbname=\w*', response.url)[0].split('=')[-1]
        abstract = selector.xpath("//span[@id='ChDivSummary']/text()").extract_first()
        author = []
        au_name = selector.xpath("//div[@class='author']/span/a/text()").extract_first()
        author_info = selector.xpath("//div[@class='author']/span/a/@onclick").extract_first()
        au_type = re.findall(r"'\w*'", author_info)[0].replace('\'', '')
        au_code = author_info.split('\',\'')[-1].split('\')')[0]
        author_url = self.crawl_url.format(sfield=au_type, skey=au_name, code=au_code)
        html0 = requests.get(author_url).content
        sele0 = etree.HTML(html0)
        au_code = sele0.xpath("//input[@id='deliveryCoutent']/@value")[0].split('#')[0]
        au_name = sele0.xpath("//input[@id='deliveryCoutent']/@value")[0].split('#')[1]
        au_orgn = sele0.xpath("//p[@class='orgn']/a/@onclick")[0]
        au_orgn_name = sele0.xpath("//p[@class='orgn']/a/text()")[0]
        au_orgn_code = re.findall(r"'\w*'", au_orgn)[-1].replace('\'', '')
        au_doma = sele0.xpath("//p[@class='doma']/text()")[0].split(';')
        if '' in au_doma:
            au_doma.remove('')
        au_url = self.crawl_url.format(sfield='au', skey=au_name, code=au_code)
        au = {'author_name': au_name, 'author_code': au_code,
                  'author_orgn_name': au_orgn_name, 'author_orgn_code': au_orgn_code,
                  'author_domain': au_doma, 'author_url': au_url}
        author.append(au)
        keywords = []
        keyword = selector.xpath("//label[@id='catalog_KEYWORD']/parent::*/a")
        if keyword:
            for a in keyword:
                keywords.append(a.xpath("text()").extract_first().replace('\r\n', '').replace(' ', '').replace(';', ''))
        category = selector.xpath(
            "//label[@id='catalog_ZTCLS']/parent::*/text()").extract_first()
        if category:
            category = category.split(';')
        else:
            category = []
        school = selector.xpath("//script/text()").re(r"WriteToPage\('(.*)','(\w*)','(\w*)','(\w*)','(\w*)'\)")
        param_1 = school[0]
        param_2 = school[1]
        param_3 = school[2]
        param_4 = school[3]
        param_5 = school[4]
        post_school_url = self.school_url.format(dbcode=param_3, dbname=param_2, filename=param_1,
                                                       curdbcode=param_4, reftype=param_5,
                                                       catalogId='lcatalog_func' + param_5)
        html = requests.get(post_school_url).content
        sele = etree.HTML(html)

        school_name = sele.xpath("//div[@class='sourinfo']/p[1]/a/text()")[0]
        school_url = sele.xpath("//div[@class='sourinfo']/p[2]/a/text()")[0]
        school_rank = sele.xpath("//div[@class='sourinfo']/p[4]/text()")[0].strip().replace('\r\n','')
        school_loc = sele.xpath("//div[@class='sourinfo']/p[3]/text()")[0]
        pub_year = re.findall(r'[1-9][0-9]{0,3}',dbname)[0]

        quote = requests.get(self.quote_url.format(dbcode=dbcode, filename=id)).text.replace("'", "\"")
        quote_num = json.loads(quote)['CITING']
        quote2_num = json.loads(quote)['SUB_CITING']
        download_num = selector.xpath(
            "//div[@class='total']/span[@class='a']/b/text()").extract_first()
        tutors = []
        tutor_count = len(selector.xpath("//label[@id='catalog_TUTOR']/parent::*/a"))
        item = DocmasItem(
            title = title,
            author = author,
            tutors = tutors,
            keywords = keywords,
            category = category,
            abstract = abstract,
            school_name = school_name,
            school_loc = school_loc,
            school_rank = school_rank,
            school_url = school_url,
            pub_year = pub_year,
            quote_num = quote_num,
            quote2_num = quote2_num,
            download_num = download_num
        )
        for span in selector.xpath("//label[@id='catalog_TUTOR']/parent::*/a"):
            author_info = span.xpath("@onclick").extract_first()
            au_type = re.findall(r"'\w*'", author_info)[0].replace('\'', '')
            au_name = span.xpath("text()").extract_first().strip().replace(';','')
            au_code = author_info.split('\',\'')[-1].split('\')')[0]
            author_url = self.crawl_url.format(sfield=au_type, skey=au_name, code=au_code)
            yield Request(url=author_url,
                          meta={
                              'item': item,
                              'tutor_count': tutor_count
                          },
                          callback=self.parse_tutor_info)

    def parse_tutor_info(self,response):
        selector = Selector(response)
        item = response.meta['item']
        au_code = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first().split('#')[0]
        au_name = selector.xpath("//input[@id='deliveryCoutent']/@value").extract_first().split('#')[1]
        au_orgn = selector.xpath("//p[@class='orgn']/a/@onclick").extract_first()
        au_orgn_name = selector.xpath("//p[@class='orgn']/a/text()").extract_first()
        au_orgn_code = re.findall(r"'\w*'", au_orgn)[-1].replace('\'', '')
        au_doma = selector.xpath("//p[@class='doma']/text()").extract_first().split(';')
        if '' in au_doma:
            au_doma.remove('')
        au_url = self.crawl_url.format(sfield='au', skey=au_name, code=au_code)
        tutor = {'author_name': au_name, 'author_code': au_code,
                  'author_orgn_name': au_orgn_name, 'author_orgn_code': au_orgn_code,
                  'author_domain': au_doma, 'author_url': au_url}

        item['tutors'].append(tutor)
        # logging.info(response.meta['author_count'])
        if item['tutors'] and len(item['tutors']) == response.meta['tutor_count']:
            yield item
        yield UnitItem(
            id=au_orgn_code,
            unit_name=au_orgn_name
        )