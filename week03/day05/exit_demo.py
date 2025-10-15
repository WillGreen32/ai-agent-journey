import logging, sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def validate_data(file_path):
    try:
        logging.info(f"Validating {file_path}")
        # Pretend something goes wrong:
        raise FileNotFoundError("File not found!")
    except FileNotFoundError as e:
        logging.error(e)
        sys.exit(1)  # ❌ failure
    else:
        logging.info("Validation passed successfully!")
        sys.exit(0)  # ✅ success

validate_data("data/raw/customers.csv")
