import logging

# 1. Configure the "style" of your log messages
logging.basicConfig(
    level=logging.INFO,   # show INFO and above
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 2. Write some logs
logging.info("Pipeline started.")
logging.warning("Missing column 'age'. Filling with default.")
logging.error("File not found! Please check path.")
