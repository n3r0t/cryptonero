import logging


def setup(module):
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s | %(name)s | %(message)s')

    file_handler = logging.FileHandler('bot.log')
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
