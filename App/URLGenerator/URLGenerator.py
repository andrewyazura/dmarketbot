import logging


logger = logging.getLogger(__name__)


class URLGenerator:
    def __init__(self, base, config):
        self.base = base
        self.config = config
        logger.debug('__init__() finished')

    def generate(self):
        logger.debug('generate() started')

        url = self.base + \
            '?price-from={}&price-to={}&exterior={}'.format(
                self.config['min_price'],
                self.config['max_price'],
                (','.join(self.config['exteriors'])).lower()
            )

        logger.debug('link generated: %s', url)

        return url


if __name__ == '__main__':
    logging.basicConfig(filename='urlgenerator.log',
                        filemode='w', level=logging.INFO)

    import yaml
    with open('config.yaml', 'r') as conf:
        config = yaml.safe_load(conf)

    generator = URLGenerator(
        'https://dmarket.com/ingame-items/item-list/csgo-skins', config)
    print(generator.generate())
