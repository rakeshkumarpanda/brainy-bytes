import os

from dotenv import load_dotenv

load_dotenv()   # reads .env when it exists, so a laptop and CI can use different settings

# Settings that change between machines (a laptop, CI, staging) live here and nowhere else
BASE_URL = os.getenv("BASE_URL", "http://localhost:4173")
