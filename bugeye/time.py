__author__ = 'lee'

from datetime import datetime, timezone

def midnight_time():
    # Replace the timezone so that timestamp is between local midnight and now instead of UTC midnight and now.
    return datetime.now().replace(year=1970, month=1, day=1, tzinfo=timezone.utc).timestamp()

