import logging
import sys

from rich import traceback
from rich.console import Console
from rich.logging import RichHandler

# Colorful logging
# https://rich.readthedocs.io/en/latest/logging.html
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(file=sys.stderr))],
)

# Add colorful tracebacks to crash with elegance
# https://rich.readthedocs.io/en/latest/traceback.html
traceback.install()

# Reserved name for global statistics
GLOBAL_STAT_NAME = "total"
