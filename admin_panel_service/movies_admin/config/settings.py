from pathlib import Path
from dotenv import load_dotenv
from split_settings.tools import include


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

include(
    'components/base.py',
    'components/database.py',
)
