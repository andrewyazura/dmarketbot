from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

timeout = 10

class ItemScraper:
    def __init__(self, addr):
        self.addr = addr

        options = Options()
        options.headless = True

        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(timeout)
        self.wait = WebDriverWait(self.driver, timeout)

    def download_page(self):
        self.driver.get(self.addr)
    
    def clean_page(self):
        self.__close_overlapping_menu()
        self.__dismiss_sidebar()
        self.__dismiss_notifications()

    def get_items(self):
        self.cards = self.driver.find_elements_by_tag_name('asset-card')

    def save_item_information(self):
        for card in self.cards:
            x = card.find_element_by_css_selector('button.c-asset__action.c-asset__action--info')
            x.click()  # this way it's more reliable for some reason

            info = self.get_item_information(card)

            self.__close_overlapping_menu()

    def get_item_information(self, card):
        print(card)

    def __close_overlapping_menu(self):
        try:
            overlay = self.driver.find_element_by_class_name('cdk-global-overlay-wrapper')
            overlay.find_element_by_class_name('c-dialogHeader__close').click()
        except:
            print('couldn\'t close overlay')
            self.__dismiss_notifications()
            self.__dismiss_sidebar()
            self.__close_overlapping_menu()
    
    def __dismiss_sidebar(self):
        try:
            sidebar = self.driver.find_element_by_class_name('с-seoArea')
            sidebar.find_element_by_class_name('с-seoArea__headerClose').click()
        except Exception as e:
            print('couldn\'t close sidebar')
            self.__dismiss_notifications()
            self.__dismiss_sidebar()

    def __dismiss_notifications(self):
        try:
            self.wait.until(EC.visibility_of_element_located((By.ID, 'onesignal-popover-cancel-button')))
            self.driver.find_element_by_id('onesignal-popover-cancel-button').click()
        except:
            print('notification didn\'t appear')


scraper = ItemScraper('https://dmarket.com/ingame-items/item-list/csgo-skins?price-to=200')
print('loading page...')
scraper.download_page()
print('cleaning up...')
scraper.clean_page()
print('searching items...')
scraper.get_items()
print('saving items...')
scraper.save_item_information()
