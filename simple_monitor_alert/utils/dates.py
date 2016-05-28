import datetime

import dateutil
import dateutil.tz
import dateutil.parser
from humanize import naturaltime


def human_since(since, include_tz=False):
    tz = dateutil.tz.tzlocal() if include_tz else None
    return naturaltime(datetime.datetime.now(tz=tz) - dateutil.parser.parse(since))