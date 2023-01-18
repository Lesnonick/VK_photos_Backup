import logging


upload_logger = logging.getLogger('Upload_logger')
upload_logger.setLevel(logging.INFO)
upload_handler = logging.FileHandler("Upload_logger.log", mode="w")
upload_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
upload_handler.setFormatter(upload_formatter)
upload_logger.addHandler(upload_handler)
