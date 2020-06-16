from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

timeout = 20


class ItemScraper:
    def __init__(self, addr):
        self.addr = addr

        options = Options()
        # options.headless = True

        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(timeout)
        self.wait = WebDriverWait(self.driver, timeout)

    def download_page(self):
        self.driver.get(self.addr)

    def clean_page(self):
        self.__dismiss_notifications()
        self.__close_overlapping_menu()
        self.__dismiss_sidebar()

    def get_items(self):
        self.cards = self.driver.find_elements_by_tag_name('asset-card')

    def save_item_information(self):
        for card in self.cards:
            self.__open_card(card)

            info = self.__get_item_information()
            print(info)

            self.__close_overlapping_menu()

    def __open_card(self, card):
        try:
            x = card.find_element_by_css_selector(
                'button.c-asset__action.c-asset__action--info')
            x.click()  # this way it's more reliable for some reason

        except:
            self.__dismiss_sidebar()
            self.__open_card(card)

    def __get_item_information(self):
        overlay = self.driver.find_element_by_class_name(
            'cdk-global-overlay-wrapper')

        item_info_blocks = overlay.find_elements_by_class_name(
            'c-assetPreview__inner')

        url = self.__get_url(item_info_blocks[0])
        data = self.__get_data(item_info_blocks[1])

        return {**data, 'url': url}

    def __get_url(self, block):
        button = block.find_element_by_css_selector(
            'button.c-shareLink__btn.mat-flat-button')
        button.click()

        div = block.find_element_by_class_name('mat-form-field-infix')
        input_block = div.find_element_by_tag_name('input')
        url = input_block.get_attribute("value")

        return url

    def __get_data(self, block):
        title = block.find_element_by_tag_name('h3').text.strip()
        exterior = self.__get_weapon_exterior(title)

        prices = [float(span.text.strip())
                  for span in
                  block.find_elements_by_class_name(
            'c-assetPreviewParam__number')]

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
        exterior = title.split('(')[-1]

        return exterior[:-1]

    def __close_overlapping_menu(self):
        try:
            overlay = self.driver.find_element_by_class_name(
                'cdk-global-overlay-wrapper')
            overlay.find_element_by_class_name('c-dialogHeader__close').click()

        except:
            print('couldn\'t close overlay')
            self.__dismiss_notifications()
            self.__close_overlapping_menu()

    def __dismiss_notifications(self):
        try:
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, 'onesignal-popover-cancel-button')))
            self.driver.find_element_by_id(
                'onesignal-popover-cancel-button').click()

        except:
            print('notification didn\'t appear')

    def __dismiss_sidebar(self):
        try:
            sidebar = self.driver.find_element_by_class_name('с-seoArea')
            sidebar.find_element_by_class_name(
                'с-seoArea__headerClose').click()

        except:
            print('couldn\'t close sidebar')


scraper = ItemScraper(
    'https://dmarket.com/ingame-items/item-list/csgo-skins?price-to=200')
print('loading page...')
scraper.download_page()
print('cleaning up...')
scraper.clean_page()
print('searching items...')
scraper.get_items()
print('saving items...')
scraper.save_item_information()
