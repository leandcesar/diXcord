try:
    from dotenv import load_dotenv
except ImportError:
    pass
else:
    load_dotenv()

from .bot import Bot  # noqa: F401
from .logger import logger  # noqa: F401
from .version import __version__  # noqa: F401
