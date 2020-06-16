import logging

import yaml
from tinydb import Query, TinyDB

logger = logging.getLogger(__name__)
Item = Query()


class ItemFilter:
    def __init__(self, config):
        self.db = TinyDB('data/db.json')
        self.items_table = self.db.table('all_items')
        self.best_items_table = self.db.table('best_items')
        self.config = config

        logger.debug('__init__() finished')

    def filter(self):
        logger.debug('filter() started')

        l = self.items_table.search(
            (Item.exterior.one_of(self.config['exteriors'])) &
            (Item.profit >= self.config['min_profit'])
        )

        for item in l:
            self.best_items_table.insert(item)

        logger.info('%i items are considered good', len(l))

    def quit(self):
        logger.debug('quit() started')

        self.db.close()


if __name__ == '__main__':
    logging.basicConfig(filename='itemfilter.log',
                        filemode='w', level=logging.INFO)

    with open('config.yaml', 'r') as conf:
        config = yaml.safe_load(conf)

    f = ItemFilter(config)
    f.filter()
    f.quit()
