import time
from shared_functions import time_format
from shared_functions import remove_scheduled_update

def test_remove_scheduled_update():
    formatted_time = time_format('12:00')
    assert isinstance(time.mktime(formatted_time), float)

def test_remove_scheduled_update():
    remove_scheduled_update('test', [])
