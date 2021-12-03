"""Common functions betwee data and news handling modules

Functions
remove_scheduled_update -- removes future update
time_format -- formats time
"""
import time

from logger import log_infomation

def remove_scheduled_update(update_name: str, updates: list) -> tuple[list, bool]:
    """Cancel scheduled updates.

    Keyword arguements:
    update_name -- name of the update,
    updates -- list of updates

    Return values:
    updates -- list of updates,
    removed -- whether an updates was removed of not
    """
    log_infomation('Removing scheduled update '+update_name)
    removed = False

    # Find and remove update
    for update in updates:
        if update['title'] == update_name:
            update['schedule'].cancel(update['schedule'].queue[0])
            updates.remove(update)
            removed = True
            break

    return removed

def time_format(time_of_day: str) -> tuple:
    """Convert the format of the time for use with the time module

    Keyword arguements:
    time_of_day -- time in format "HH:MM"

    Return values:
    formatted_time -- time in format required for the time module
    """
    # Get current infomation
    log_infomation('Formatting time')
    hour = int(time_of_day[:2])
    minute = int(time_of_day[3:])
    currrent_time = time.localtime()
    day = int(currrent_time[2])
    week_day = int(currrent_time[6])
    month = int(currrent_time[1])
    year = int(currrent_time[0])

    # Check if day (and weekday), month, year change.
    if (hour < currrent_time[3]) or (
        (minute <= currrent_time[4]) and hour == currrent_time[3]
        ):
        day += 1
        if day > 31:
            month += 1
            day = 1
        elif (day > 29) and (month == 2):
            month += 1
            day = 1
        elif (day>30) and (month in [4,6, 9, 11]):
            month += 1
            day = 1
        if month > 12:
            month = 1
            year += 1
        week_day += 1
        if week_day > 6:
            week_day = 0
    formatted_time = (
        year,
        month,
        day,
        hour,
        minute,
        0,
        week_day,
        currrent_time[7],
        currrent_time[8],
        )
    return formatted_time
