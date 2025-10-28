from src.http.core import HttpClient, BASE_URL, TIMEOUT, RETRIES

def main():
    print("Base URL:", BASE_URL)
    print("Timeout:", TIMEOUT)
    print("Retries:", RETRIES)
    # client = HttpClient()  # will work once methods are implemented
    print("Project scaffolding OK ✅")

if __name__ == "__main__":
    main()
