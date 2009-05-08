LOGGING = True
LOGGER="Contacts"

# Setup logging
if LOGGING:
    import logging
    logger=logging.getLogger(LOGGER)
    logger.setLevel(logging.DEBUG)
    handler=logging.StreamHandler()
    formatter=logging.Formatter("%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    log=logging.getLogger(LOGGER)
else:
    class log:
        @staticmethod
        def debug(msg):
            pass
        
