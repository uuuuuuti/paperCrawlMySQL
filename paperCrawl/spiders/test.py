from paperCrawl.models import Paper, Author, Unit, Journal, db_connect, create_table
from sqlalchemy.orm import sessionmaker
import re
# engine = db_connect()
# create_table(engine)
# Session = sessionmaker(bind=engine)
#
# paper_list = []
# session = Session()
#for id, in session.query(Paper.id).all():
#    paper_list.append(id)

#print(paper_list)

#_,name = session.query(Unit.id,Unit.name).filter_by(name = "北京大学").first()
#id,_ = session.query(Unit.id,Unit.name).filter_by(name = "北京大学").first()
#with open('urls.txt','w') as fp:
#    fp.writelines()
# str = "TurnPageToKnet('au','吴斌','05966545;10348514;');\
# TurnPageToKnet('au','史忠植','');"
# find_list = re.findall("\d+",str)
# print(find_list)

# import requests
# from lxml import etree
# url_list = ["http://kns.cnki.net/kcms/detail/frame/knetlist.aspx?code=05966545&infotype=4&codetype=1&catalogId=lcatalog_1&catalogName=%E5%8F%91%E8%A1%A8%E5%9C%A8%E6%9C%9F%E5%88%8A%E4%B8%8A%E7%9A%84%E6%96%87%E7%8C%AE&CurDBCode=CJFQ&page=18",
#             "http://kns.cnki.net/kcms/detail/frame/knetlist.aspx?code=05966545&infotype=4&codetype=1&catalogId=lcatalog_1&catalogName=%E5%8F%91%E8%A1%A8%E5%9C%A8%E6%9C%9F%E5%88%8A%E4%B8%8A%E7%9A%84%E6%96%87%E7%8C%AE&CurDBCode=CJFQ&page=19",
#             "http://kns.cnki.net/kcms/detail/frame/knetlist.aspx?code=05966545&infotype=4&codetype=1&catalogId=lcatalog_1&catalogName=%E5%8F%91%E8%A1%A8%E5%9C%A8%E6%9C%9F%E5%88%8A%E4%B8%8A%E7%9A%84%E6%96%87%E7%8C%AE&CurDBCode=CJFQ&page=17"]
#
# for url in url_list:
#     headers = {'Referer': 'http://kns.cnki.net/kcms/detail/knetsearch.aspx?sfield=au&skey=%E5%8F%B2%E5%BF%A0%E6%A4%8D&code=30977876'}
#     html = requests.get(url,headers=headers)
#     sel = etree.HTML(html.text)
#     papers_link = sel.xpath("//ul[@class='bignum']/li")
#     print("request page:"+ url)
#     for link in papers_link:
#         paper_url = link.xpath("a[1]/@href")[0]
#         # self.all_paper.append(p_url)
#         print('crawled url:' + paper_url + '\n')