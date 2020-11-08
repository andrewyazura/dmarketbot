import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tinydb import TinyDB

logger = logging.getLogger(__name__)
LOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class ItemScraper:
    def __init__(self, addr, timeout):
        self.addr = addr

        options = Options()
        options.headless = True
        options.set_preference("dom.webnotifications.enabled", False)

        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(timeout)
        self.wait = WebDriverWait(self.driver, timeout)

        self.db = TinyDB('data/db.json')
        self.items_table = self.db.table('all_items')

        logger.debug('__init__() finished')

    def download_page(self):
        logger.debug('download_page() started')
        self.driver.get(self.addr)
        logger.info('page downloaded')

    def clean_page(self):
        logger.debug('clean_page() started')

        self.__close_overlapping_menu()
        self.__dismiss_sidebar()

    def get_items(self):
        logger.debug('get_items() started')

        self.cards = self.driver.find_elements_by_tag_name('asset-card')
        logger.info('%i cards with items found', len(self.cards))

    def save_item_information(self):
        logger.debug('save_item_information() started')

        for card in self.cards:
            is_open = self.__open_card(card)
            if not is_open:
                break

            info = self.__get_item_information()
            self.items_table.insert(info)
            logger.info('item saved')

            self.__close_overlapping_menu()

    def __open_card(self, card):
        logger.debug('__open_card() started')

        try:
            x = card.find_element_by_css_selector(
                'button.c-asset__action.c-asset__action--info')

            x.click()  # this way it's more reliable for some reason
            return True

        except Exception as e:
            logger.warning('couldn\'t open card')
            logger.debug(e)

            return False

    def __get_item_information(self):
        logger.debug('__get_item_information() started')

        try:
            overlay = self.driver.find_element_by_class_name(
                'cdk-global-overlay-wrapper')

            item_info_blocks = overlay.find_elements_by_class_name(
                'c-assetPreview__inner')

            url = self.__get_url(item_info_blocks[0])
            data = self.__get_data(item_info_blocks[1])

            return {**data, 'url': url}

        except Exception as e:
            logger.warning('couldn\'t find window')
            logger.debug(e)
            return {}

    def __get_url(self, block):
        logger.debug('__get_url() started')

        button = block.find_element_by_css_selector(
            'button.c-shareLink__btn.mat-flat-button')
        button.click()

        div = block.find_element_by_class_name('mat-form-field-infix')
        input_block = div.find_element_by_tag_name('input')
        url = input_block.get_attribute("value")

        return url

    def __get_data(self, block):
        logger.debug('__get_data() started')

        title = block.find_element_by_tag_name('h3').text.strip()
        exterior = self.__get_weapon_exterior(title)

        prices = [span.text.strip()
                  for span in
                  block.find_elements_by_class_name(
            'c-assetPreviewParam__number')]  # prices are str there

        prices = [float(''.join(price.split()))
                  for price in prices]  # converting prices to floats

        profit = round(abs(prices[1] - prices[0]), 2)
        discount = block.find_element_by_tag_name(
            'asset-discount-badge').text

        trade_lock = block.find_element_by_css_selector(
            'p.c-assetPreviewParam__value').text.strip()

        data = {
            'title': title,
            'exterior': exterior,
            'trade_lock': trade_lock,
            'dmarket_price': prices[0],
            'steam_price': prices[1],
            'profit': profit,
            'discount': discount
        }

        return data

    def __get_weapon_exterior(self, title):
        logger.debug('__get_weapon_exterior() started')

        exterior = title.split('(')[-1]
        return exterior[:-1]

    def __close_overlapping_menu(self, close_self=True):
        logger.debug('__close_overlapping_menu() started')

        try:
            overlay = self.driver.find_element_by_class_name(
                'cdk-global-overlay-wrapper')
            overlay.find_element_by_class_name('c-dialogHeader__close').click()

        except Exception as e:
            logger.warning('couldn\'t close overlay')
            logger.debug(e)

    def __dismiss_notifications(self):
        logger.debug('__dismiss_notification() started')

        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, 'onesignal-popover-cancel-button')))
            self.driver.find_element_by_id(
                'onesignal-popover-cancel-button').click()

        except Exception as e:
            logger.warning('notification didn\'t appear')
            logger.debug(e)

    def __dismiss_sidebar(self):
        logger.debug('__dismiss_sidebar() started')

        try:
            sidebar = self.driver.find_element_by_class_name('с-seoArea')
            sidebar.find_element_by_class_name(
                'с-seoArea__headerClose').click()

        except Exception as e:
            logger.warning('couldn\'t close sidebar')
            logger.debug(e)

    def quit(self):
        logger.debug('quit() started')

        self.driver.quit()
        self.db.close()


if __name__ == '__main__':
    logging.basicConfig(filename='itemscraper.log',
                        filemode='w', level=logging.INFO)

    scraper = ItemScraper(
        'https://dmarket.com/ingame-items/item-list/csgo-skins', 20)
    scraper.download_page()
    scraper.clean_page()
    scraper.get_items()
    scraper.save_item_information()
    scraper.quit()
