import logging
from time import sleep

import telebot
from telebot import types
from tinydb import Query, TinyDB

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, config):
        self.config = config

        self.bot = telebot.TeleBot(config['telegram_token'])
        self.groups = config['groups']

        self.db = TinyDB('data/db.json')
        self.items_table = self.db.table('best_items')

        @self.bot.message_handler(commands=['start'])
        def _(message):
            logger.debug('/start command received')
            self.__process_command_start(message)

        logger.debug('__init__() finished')

    def __process_command_start(self, message):
        logger.debug('__process_command_start() started')

        self.bot.reply_to(message, 'Hello! I\'ll send you best DMARKET deals')

    def send_notifications(self):
        logger.debug('send_notifications() started')

        items = self.__sort_items()
        best_items = items[:6]
        other_items = items[6:]

        for group in self.groups:
            for item in best_items:
                logger.debug('message to %s sent', group)

                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton('Link', url=item['url']))

                self.bot.send_message(
                    group, self.__generate_item_message(item),
                    parse_mode='markdown', disable_web_page_preview=True, reply_markup=kb)
                sleep(0.5)

            logger.debug('message to %s sent', group)

            self.bot.send_message(
                group, self.__generate_other_items(other_items),
                parse_mode='markdown', disable_web_page_preview=True)

        logger.info('%i items are sent to %i groups',
                    len(items), len(self.groups))

    def __sort_items(self):
        logger.debug('__sort_items() started')

        sort_type = self.config['sort_type']

        logger.debug('sort_type = %s', sort_type)

        if sort_type == 'price_lowest':
            return sorted(self.items_table.all(), key=lambda k: k['price'])

        elif sort_type == 'price_highest':
            return sorted(self.items_table.all(), key=lambda k: k['price'], reverse=True)

        elif sort_type == 'profit_highest':
            return sorted(self.items_table.all(), key=lambda k: k['profit'], reverse=True)

        elif sort_type == 'profit_lowest':
            return sorted(self.items_table.all(), key=lambda k: k['profit'])

    def __generate_item_message(self, item):
        logger.debug('__generate_item_message() started')

        base = """Title: {title}
Exterior: {exterior}
Dmarket price: {dmarket_price}
Steam price: {steam_price}
Discount: {discount}
Profit: **{profit}**
"""

        return base.format(**item)

    def __generate_other_items(self, items):
        logger.debug('__generate_other_items() started')

        base = ''

        for i in range(len(items)):
            base += '[${profit}]({url})'.format(**items[i])
            base += '\n' if (i % 5) == 0 else '    '

        return base

    def quit(self):
        logger.debug('quit() started')
        self.db.close()


if __name__ == '__main__':
    logging.basicConfig(filename='telegramnotifier.log',
                        filemode='w', level=logging.DEBUG)

    import yaml
    with open('config.yaml', 'r') as conf:
        config = yaml.safe_load(conf)
    bot = TelegramNotifier(config)
    bot.send_notifications()
    bot.quit()
