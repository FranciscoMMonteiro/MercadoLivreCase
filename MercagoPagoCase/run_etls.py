import importlib
import time
from datetime import datetime



ETL_PIPELINE = [
    "etls.etl_product_id",   
    "etls.etl_items",       
    "etls.etl_currency_convertion",     
    "etls.etl_sellers"      
]

LOG_FILE = "etl_orchestrator.log"

def log(msg: str):
    """Records messages with timestamp to console and file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_etl(module_name: str):
    """Imports and executes the ETLs that is passed."""
    try:
        log(f'Initializing {module_name}')
        start = time.time()

        etl_module = importlib.import_module(module_name)
        if not hasattr(etl_module, "main"):
            raise AttributeError(f"There isn't a main() function in {module_name}")

        etl_module.main()

        duration = time.time() - start
        log(f"Finished {module_name} in {duration:.2f} seconds")

    except Exception as e:
        log(f'ERROR IN {module_name}: {e}')
        # raise

def main():
    time.sleep(3) 
    log("========== BEGGINING OF ETLs EXECUTION ==========")
    for etl_name in ETL_PIPELINE:
        run_etl(etl_name)
    log("========== END OF ETLs EXECUTION ==========")
    print("")


if __name__ == "__main__":
    main()
