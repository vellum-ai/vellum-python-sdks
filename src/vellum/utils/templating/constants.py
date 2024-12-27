import datetime
import itertools
import json
import random
import re
from typing import Any, Callable, Dict, Union

import dateutil
import pydash
import pytz
import yaml

from vellum.utils.templating.custom_filters import is_valid_json_string

DEFAULT_JINJA_GLOBALS: Dict[str, Any] = {
    "datetime": datetime,
    "dateutil": dateutil,
    "itertools": itertools,
    "json": json,
    "pydash": pydash,
    "pytz": pytz,
    "random": random,
    "re": re,
    "yaml": yaml,
}
DEFAULT_JINJA_CUSTOM_FILTERS: Dict[str, Callable[[Union[str, bytes]], bool]] = {
    "is_valid_json_string": is_valid_json_string,
}
