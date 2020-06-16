import yaml

import App


def clear_table(table_name):
    from tinydb import TinyDB
    db = TinyDB('data/db.json')
    db.drop_table(table_name)
    db.close()


def main():
    with open('config.yaml', 'r') as conf:
        config = yaml.safe_load(conf)

    urlgenerator = App.URLGenerator(config['base_url'], config)
    url = urlgenerator.generate()

    item_scraper = App.ItemScraper(url, config['selenium_timeout'])
    item_scraper.download_page()
    item_scraper.clean_page()
    item_scraper.get_items()
    item_scraper.save_item_information()
    item_scraper.quit()

    item_filter = App.ItemFilter(config)
    item_filter.filter()
    item_filter.quit()

    clear_table('all_items')

    # send to telegram
    # clear_table('best_items')


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='dmarketbot.log',
                        filemode='w', level=logging.DEBUG)
    main()
