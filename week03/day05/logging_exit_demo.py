import logging, sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logging.info("Validation started.")
file_found = False  # pretend this fails

if not file_found:
    logging.error("Invalid input file — stopping pipeline.")
    sys.exit(1)
else:
    logging.info("Validation passed.")
    sys.exit(0)
