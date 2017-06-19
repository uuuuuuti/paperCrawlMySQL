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
from paperCrawl.items import PaperItem, ProceedingItem, NewspaperItem, DocmasItem, UnitItem
import codecs, json
#from scrapy.exceptions import DropItem
#import redis

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
        elif  isinstance(item, NewspaperItem):
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



