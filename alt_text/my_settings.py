"""Local configuration. Credentials are read from the environment."""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
if os.getenv("DB_ENGINE") == "mysql":
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.getenv("DB_HOST", "localhost"), "PORT": os.getenv("DB_PORT", "3306"),
    }}
AZURE_AI_CONFIG = {"endpoint": os.getenv("VISION_ENDPOINT", ""), "key": os.getenv("VISION_KEY", "")}
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
