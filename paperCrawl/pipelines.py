# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient
from paperCrawl.settings import MONGO_URI
from paperCrawl.items import PaperItem, ProceedingItem, NewspaperItem, DocmasItem, UnitItem, ConferenceItem, AuthorItem, JournalItem
from sqlalchemy.orm import sessionmaker
from paperCrawl.models import Paper, Author, Unit, Journal, db_connect, create_table
import codecs, json
#from scrapy.exceptions import DropItem
#import redis

'''
存Mysql
'''
class MysqlPipeline(object):
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)

    # def process_item(self, item, spider):
    #     session = self.Session()
    #     #hn = Hn(**item)
    #     #session.add(hn)
    #     session.commit()
    #     return item
    def _process_paper(self, item):
        session = self.Session()
        paper = Paper(**item)
        data = session.query(Paper).filter_by(id= paper.id).first()
        if not data:
            session.add(paper)
            session.commit()

    def _process_author(self, item):
        session = self.Session()
        author = Author(**item)
        data = session.query(Author).filter_by(id=author.id).first()
        if not data:
            session.add(author)
            session.commit()

    def _process_unit(self, item):
        session = self.Session()
        unit = Unit(**item)
        data = session.query(Unit).filter_by(id=unit.id).first()
        if not data:
            session.add(unit)
            session.commit()

    def _process_journal(self, item):
        session = self.Session()
        journal = Journal(**item)
        data = session.query(Journal).filter_by(id=journal.id).first()
        if not data:
            session.add(journal)
            session.commit()

    # def _process_proceeding(self, item):
    #     session = self.Session()
    #     proceeding = Proceeding(**item)
    #     data = session.query(Proceeding).filter_by(id=proceeding.id).first()
    #     if not data:
    #         session.add(proceeding)
    #         session.commit()
    #
    # def _process_conference(self, item):
    #     session = self.Session()
    #     conference = Conference(**item)
    #     data = session.query(Conference).filter_by(id=conference.id).first()
    #     if not data:
    #         session.add(conference)
    #         session.commit()
    #
    # def _process_docmas(self, item):
    #     session = self.Session()
    #     docmas = Docmas(**item)
    #     data = session.query(Docmas).filter_by(id=docmas.id).first()
    #     if not data:
    #         session.add(docmas)
    #         session.commit()

    def process_item(self, item, spider):
        """
        处理item
        """
        if isinstance(item, PaperItem):
            self._process_paper(item)
        # elif isinstance(item, ProceedingItem):
        #     self._process_proceeding(item)
        # elif isinstance(item, ConferenceItem):
        #     self._process_conference(item)
        # elif isinstance(item, DocmasItem):
        #     self._process_docmas(item)
        elif isinstance(item, UnitItem):
            self._process_unit(item)
        elif isinstance(item, AuthorItem):
            self._process_author(item)
        elif isinstance(item, JournalItem):
            self._process_journal(item)
        return item


'''
存MongoDB
'''
class PapercrawlPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        #self.file = codecs.open('unit.json', 'w', encoding='utf-8')
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=MONGO_URI,
            mongo_db='new_zhiwang'
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.mongo_uri)
        self.client['new_zhiwang'].authenticate('zhiwang', 'asdasd')
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def _process_paper(self, item):
        """
        存储期刊论文信息
        """
        collection = self.db['paper']
        data = collection.find_one({
            'id':item['id']
        })
        if not data:
            self.db['paper'].insert(dict(item))


    def _process_proceeding(self, item):
        """
        存储会议论文信息
        """
        collection = self.db['proceeding']

        data = collection.find_one({
            'id':item['id']
        })
        if not data:
            self.db['proceeding'].insert(dict(item))

        #proceeding_id = item['proceeding_id']
        #collection.update({'proceeding_id':proceeding_id},
        #                 dict(item),upsert=True)
        """
        data = collection.find_one({
            'zhihu_id': item['zhihu_id'],
            'user_type': item['user_type']})
        if not data:
            self.db['relation'].insert(dict(item))
        else:
            origin_list = data['user_list']
            new_list = item['user_list']
            data['user_list'] = list(set(origin_list) | set(new_list))
            collection.update({'zhihu_id': item['zhihu_id'],
                               'user_type': item['user_type']}, data)
        """
    def _process_newspaper(self,item):
        '''
        存储发表在报纸上的文献
        '''
        collection = self.db['newspaper']
        data = collection.find_one({
            'id' : item['id']
        })
        if not data:
            self.db['newspaper'].insert(dict(item))

    def _process_docmas(self,item):
        '''
        博硕论文
        '''
        collection = self.db['docmas']
        data = collection.find_one({
            'id':item['id']
        })
        if not data:
            self.db['docmas'].insert(dict(item))

    def _process_unit(self,item):
        #line = json.dumps(dict(unitItem)) + "\n"
        #self.file.write(line.decode('unicode_escape'))
        #return unitItem
        collection = self.db['unit']
        data = collection.find_one({
            'id': item['id']
        })
        if not data:
            self.db['unit'].insert(dict(item))

    def process_item(self, item, spider):
        """
        处理item
        """
        if isinstance(item, PaperItem):
            self._process_paper(item)
        elif isinstance(item, ProceedingItem):
            self._process_proceeding(item)
        elif isinstance(item, NewspaperItem):
            self._process_newspaper(item)
        elif isinstance(item, DocmasItem):
            self._process_docmas(item)
        elif isinstance(item, UnitItem):
            self._process_unit(item)
        return item



'''
class UnitToRedis(object):
    def __init__(self):
        self.Redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def process_item(self,item,spider):
        if self.Redis.exists('url:%s' % item['id']):
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.Redis.set('url:%s' % item['id'], 1)
            return item

'''



