import logging

from tinydb import Query, TinyDB

logger = logging.getLogger(__name__)


class ItemFilter:
    def __init__(self):
        self.db = TinyDB('data/db.json')
        self.items_table = self.db.table('all_items')
        self.best_items_table = self.db.table('best_items')

    def filter(self):
        pass

    def quit(self):
        self.db.close()


if __name__ == '__main__':
    logging.basicConfig(filename='itemfilter.log',
                        filemode='w', level=logging.INFO)

    f = ItemFilter()
    f.filter()
    f.quit()
