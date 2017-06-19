# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
        期刊论文
        paper_id:     论文标识id 如JSJX200112013 期刊首字母加出版时间
        title:  论文名
        authors:
            author_name 通过该作者的文献列表爬取的该论文
            author_id   上述author_name的相应的id 如skey=史忠植&code=05966545 code为id
            author_org 上述作者的单位机构
            author_subj 上述作者的研究学科
            authors 该论文的所有作者
            authors_unit 所有作者的单位机构
        journal 期刊名
        journal_eng 期刊英文名
        issn 期刊的issn码 可以作为期刊的唯一标识码
        pub_date 该paper在此期刊上的出版时间
        doi
        category 论文分类号
        url 该论文的url
        keywords 论文关键词
        abstract 论文摘要
        fund 基金
        quote_num 被引用次数
        download_num 被下载次数

        """
    id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    journal = scrapy.Field()
    journal_eng = scrapy.Field()
    issn = scrapy.Field()
    doi = scrapy.Field()
    db_code = scrapy.Field()
    db_name = scrapy.Field()
    pub_date = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    organizations = scrapy.Field()
    keywords = scrapy.Field()
    abstract = scrapy.Field()
    fund = scrapy.Field()
    quote_num = scrapy.Field()
    quote2_num = scrapy.Field()
    download_num = scrapy.Field()


class ProceedingItem(scrapy.Item):
    """
    会议论文
    proceeding_id:     论文标识id 如JSJX200112013 期刊首字母加出版时间
    title:  论文名
    authors 作者的信息
    conference_name 会议名称
    conference_date 会议时间
    conference_loc 会议地点
    source 会议论文来源
    category 分类号
    url 该论文的url
    keywords 论文关键词
    abstract 论文摘要
    quote_num 被引用次数
    quote2_num 二次引用次数
    download_num 被下载次数
    """
    id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    db_code = scrapy.Field()
    db_name = scrapy.Field()
    conference_name = scrapy.Field()
    conference_date = scrapy.Field()
    conference_loc = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    abstract = scrapy.Field()
    quote_num = scrapy.Field()
    quote2_num = scrapy.Field()
    download_num = scrapy.Field()


class NewspaperItem(scrapy.Item):
    '''
    title       名字
    authors     作者信息
    keywords    关键词
    layout_name 版名
    layout_num  版号
    category    分类号
    pub_date    出版日期
    newspaper_name  报名
    newspaper_loc   报纸位置
    newspaper_rank  报纸等级
    newspaper_url   报纸官网
    download_num    下载数

    '''
    id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    db_code = scrapy.Field()
    db_name = scrapy.Field()
    abstract = scrapy.Field()
    keywords = scrapy.Field()
    layout_name = scrapy.Field()
    layout_num = scrapy.Field()
    category = scrapy.Field()
    pub_date = scrapy.Field()
    newspaper_name = scrapy.Field()
    newspaper_loc = scrapy.Field()
    newspaper_rank = scrapy.Field()
    newspaper_url = scrapy.Field()
    download_num = scrapy.Field()
    url = scrapy.Field()


class DocmasItem(scrapy.Item):
    '''
    博硕论文
    title
    author
    keywords
    tutor
    category
    abstract
    school_name
    school_loc
    school_rank
    pub_year
    quote_num
    quote2_num
    download_num
    '''
    title = scrapy.Field()
    author = scrapy.Field()
    keywords = scrapy.Field()
    db_code = scrapy.Field()
    db_name = scrapy.Field()
    tutors = scrapy.Field()
    category = scrapy.Field()
    abstract =  scrapy.Field()
    school_name = scrapy.Field()
    school_loc = scrapy.Field()
    school_rank = scrapy.Field()
    school_url = scrapy.Field()
    pub_year = scrapy.Field()
    quote_num = scrapy.Field()
    quote2_num = scrapy.Field()
    download_num = scrapy.Field()
    url = scrapy.Field()

class PatentItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    parse_from = scrapy.Field()
    unit = scrapy.Field()
    db_name = scrapy.Field()
    abstract = scrapy.Field()
    category = scrapy.Field()
    main_clain = scrapy.Field()#主权项
    pub_date = scrapy.Field() #公开日
    apply_date = scrapy.Field() #申请日
    url = scrapy.Field()


class UnitItem(scrapy.Item):
    id = scrapy.Field()
    unit_name = scrapy.Field()

'''
refer_list 参考文献列表
quote_list 引用文献列表
'''
class ReferItem(scrapy.Item):
    id = scrapy.Field()
    title = scrapy.Field()
    db_code =scrapy.Field()
    db_name = scrapy.Field()
    authors = scrapy.Field()
    quote_list = scrapy.Field()
    refer_list = scrapy.Field()