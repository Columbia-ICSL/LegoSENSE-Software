# pip install coloredlogs
# To test coloredlogs: coloredlogs --demo
import coloredlogs, logging

def get_logger(name, file=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)
    # coloredlogs overrides the formatter
    # c_handler.setFormatter(logging.Formatter('[%(levelname)s] %(name)s - %(message)s'))
    logger.addHandler(c_handler)

    if file is not None:
        f_handler = logging.FileHandler(file)
        f_handler.setLevel(logging.WARNING)
        f_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s'))
        logger.addHandler(f_handler)
    
    coloredlogs.install(level='DEBUG', logger=logger)
    return logger

if __name__ == "__main__":
    logger = get_logger("LogUtil")
    logger.debug("test debug")
    logger.info("test info")
    logger.warning("test warning")
    logger.error("test error")
    logger.critical("test critical")