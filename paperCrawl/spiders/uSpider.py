from paperCrawl.settings import MONGO_URI
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider
from scrapy.http import Request
from paperCrawl.items import PaperItem,ProceedingItem,NewspaperItem,DocmasItem, UnitItem, JournalItem, AuthorItem
from paperCrawl.models import Paper, Author, Unit, Journal, db_connect, create_table
from sqlalchemy.orm import sessionmaker
import logging,re,json,urllib
from lxml import etree
from pymongo import MongoClient
class USpider(CrawlSpider):
    name = "uSpider"
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
    #start_urls =[crawl_url.format(sfield='in',skey='中山大学',code='0140250')]


    start_urls = []
    exist_ids = []

    def __init__(self, unit=None, *args, **kwargs):
        super(USpider, self).__init__(*args, **kwargs)
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        session = self.Session()
        #这样的话效率较低
        # if session.query(Paper.id).first():
        #     for id, in session.query(Paper.id).all():
        #         self.exist_ids.append(id)
        code, _ = session.query(Unit.id, Unit.name).filter_by(name=unit).first()
        self.start_urls.append(self.crawl_url.format(sfield='in', skey=unit, code=code))


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
            # newspaper_url = self.post_url.format(code=code, infotype=14, codetype=4,
            #                                 catalogId='lcatalog_4', catalogName='发表在报纸上的文献')
            # patent_url = self.post_url.format(code=code, infotype=21, codetype='inzl',
            #                              catalogId='lcatalog_inzl', catalogName='申请的专利')

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

            # 未找到相关数据
            if paper_num is None:
                logging.WARNING('No related data!!!!!!!')
                return
            else:
                page_num = int((int(paper_num) + 10 - 1) / 10)
                i = 1
                while i < page_num + 1:
                    next_url = self.page_url.format(code=code, infotype=infotype, codetype=codetype,
                                                    catalogId=catalogId, catalogName=catalogName, curDB=cur_db,
                                                    curPage=i)
                    i += 1
                    yield Request(url=next_url, callback=self.parse_paper_url)


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
                #p_id = re.findall(r'filename=\w*', p_url)[0].split('=')[-1]
                #可能性比较小 还是不做判断比较好
                #if p_id not in self.exist_ids:
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
            dbname = re.findall(r'dbname=\w*', response.url)[0].split('=')[-1]
            title = selector.xpath("//div[@class='wxTitle']/h2[@class='title']/text()").extract_first()

            journal_name = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[@class='title']/a/text()").extract_first()
            journal_id = selector.xpath(
                "//div[@class='wxInfo']/div[@class='wxsour']/div[@class='sourinfo']/p[@class='title']/a/@onclick").extract_first()
            if journal_id:
                journal_id = journal_id.split(',')[-1].replace("'","").replace(')','').replace(';','')
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

            organizations_span = selector.xpath("//div[@class='orgn']/span/a")
            org_names = None
            org_ids = None
            if organizations_span:
                org_info = organizations_span.xpath("@onclick").extract_first()
                org_name_list = re.findall("\',\'([\u4e00-\u9fa5a-zA-Z 0-9]+)\',\'",org_info)
                org_code_list = re.findall("(\d+);",org_info)
                org_names = ",".join(org_name_list)
                org_ids = ",".join(org_code_list)

            download_num = selector.xpath(
                "//div[@class='wxmain']/div[@class='wxInfo']/div[@class='wxBaseinfo']/div[@class='total']/span[@class='a']/b/text()").extract_first()
            if download_num:
                download_num = download_num.replace(
                    '(', '').replace(')', '')
            else:
                download_num = 0

            author_info = selector.xpath("//div[@class='author']/span/a/@onclick").extract_first()
            au_name_list = re.findall("\',\'([\u4e00-\u9fa5a-zA-Z 0-9]+)\',\'", author_info)
            au_code_list = re.findall("(\d+);", author_info)
            au_names = ",".join(au_name_list)
            au_ids = ",".join(au_code_list)

            author_urls = []
            for span in selector.xpath("//div[@class='author']/span"):
                author_span = span.xpath("a/@onclick").extract_first()
                au_type = re.findall(r"'\w*'", author_span)[0].replace('\'', '')
                au_name = re.findall("\',\'([\u4e00-\u9fa5a-zA-Z 0-9]+)\',\'", author_span)[0]
                au_code = re.findall("(\d+);", author_span)
                author_url = self.crawl_url.format(sfield=au_type, skey=au_name, code=au_code)
                author_urls.append(author_url)

            p_item = PaperItem(
                id=paper_id,
                title=title,
                journal_id = journal_id,
                journal_name=journal_name,
                author_ids = au_ids,
                author_names = au_names,
                db_code=dbcode,
                db_name= dbname,
                pub_date=pub_date,
                categorys=",".join(category),
                org_names=org_names,
                org_ids = org_ids,
                doi=doi,
                url=url,
                keywords=",".join(keywords),
                abstract=abstract,
                funds=",".join(fund),
                download_num=int(download_num)
            )

            j_item = JournalItem(
                id = journal_id,
                name = journal_name,
                issn = issn,
                eng_name = journal_eng,
                db_code = dbcode
            )
            yield j_item

            quote_url = self.quote_url.format(dbcode=dbcode, filename=paper_id)
            yield Request(quote_url, meta={
                'item': p_item
            }, callback=self.parse_quote_info)

            #TODO:没有code的到底要不要parse,但是只有parse完才知道有没有效
            for url in author_urls:
                yield Request(url=url,
                              meta={
                                  'dbcode': dbcode
                              },
        #                      dont_filter=True,
                              callback=self.parse_author_info)

    def parse_author_info(self, response):
        if response.status != 200:
            req = response.request
            req.meta["change_proxy"] = True
            yield req
        else:
            selector = Selector(response)
            #item = response.meta['item']
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
                # author = {'author_name': au_name, 'author_code': au_code,
                #           'author_orgn_name': au_orgn_name, 'author_orgn_code': au_orgn_code,
                #           'author_domain': au_doma, 'author_first': response.meta['au_first'], 'author_url': au_url}
                a_item = AuthorItem(
                    id = au_code,
                    name = au_name,
                    unit_id = au_orgn_code,
                    unit_name = au_orgn_name,
                    domains = au_doma,
                    url = au_url
                )
                u_item = UnitItem(
                    id = au_orgn_code,
                    name = au_orgn_name,
                    url = self.crawl_url.format(sfield='in', skey=au_orgn_name, code=au_orgn_code)
                )
                yield a_item, u_item

                #item['authors'].append(author)
                #if len(item['authors']) == response.meta['author_count']:
                #    quote_url = self.quote_url.format(dbcode=response.meta['dbcode'], filename=item['id'])
                #    yield Request(quote_url, meta={
                #        'item': item
                #    }, callback=self.parse_quote_info)
            else:
                au_name = response.url.split('&skey=')[-1].split('&')[0]
                au_name = urllib.parse.unquote(au_name)
                au_code = response.url.split('&code=')[-1].replace(';', '')
                au_url = self.crawl_url.format(sfield='au', skey=au_name, code=au_code)
                a_item = AuthorItem(
                    id=au_code,
                    name=au_name,
                    url=au_url
                )
                yield a_item

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
            item['quote_num'] = int(quote_num)
            item['quote2_num'] = int(quote2_num)
            yield item

