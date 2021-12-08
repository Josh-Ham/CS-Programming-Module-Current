"""Covid news handing module

Functions:
    news_API_request -- makes API request to News API
    update_news -- gets updated news headlines
    remove_headline -- removes news headline
    schedule_news_update -- schedules updates
    get_updates -- gets uncompleted updates
    schedule_check_news -- runs scheduler
    get_news -- gets formatted news data
    remove_news_update -- removes future news update
    set_repeating_news_update -- makes an update repeat
"""
import json
import sched
import time

from newsapi import NewsApiClient

import logger
from shared_functions import remove_scheduled_update, time_format

# Load config file
with open("config.json", 'r', encoding='utf8') as config_file:
    configerables = json.load(config_file)

newsapi = NewsApiClient(api_key=configerables["api_key"])

headlines = []
deleted_headlines = []
updates = []
schedule = sched.scheduler(time.time, time.sleep)

def news_API_request(
    covid_terms: str = configerables['news_search_terms']
    ) -> list:
    """Get headlines about Covid in English.

    Optional arguements:
        covid_terms -- search terms for the API request

    Return values:
        news_articles -- list of the articles
    """
    logger.log_infomation('Fetching new news articles')

    # Get covid news articles
    news_stories = newsapi.get_everything(
        q=covid_terms,
        language=configerables['language']
    )

    if not news_stories:
        logger.log_error('No news API data')

    news_articles = news_stories['articles']

    return news_articles

def update_news() -> None:
    """Update the covid news headlines."""
    logger.log_infomation('Getting new news articles')

    news_articles = news_API_request()

    # Format articles and add to headlines if user hasn't deleted it
    for article in news_articles:
        temp_dictionary = {}
        temp_dictionary['title'] = article['title']
        temp_dictionary['content'] = article['content']
        temp_dictionary['url'] = article['url']

        if (temp_dictionary not in headlines) and (
            temp_dictionary not in deleted_headlines
            ):
            headlines.append(temp_dictionary)
        else:
            logger.log_warning('Headline already seen')

def remove_headline(headline: str) -> None:
    """Remove the selected headline.

    Keyword arguements:
        headline -- title of the headline to replace
    """
    logger.log_infomation('Remvoing headline')
    # Get the whole headline from the title
    headline = next(
        (item for item in headlines if item['title'] == headline),
        None
        )
    # Remove the headline
    if headline in headlines:
        headlines.remove(headline)
        deleted_headlines.append(headline)

def schedule_news_update(
    update_interval: str,
    update_name: str
    ) -> None:
    """Schedule news updates using sched.

    Keyword arguements:
        update_interval -- time of day update takes place,
        update_name -- name of the update
    """
    global updates
    logger.log_infomation('Scheduling new news update')

    # Format update_interval
    if isinstance(update_interval, str):
        formated_time = time_format(update_interval)
    else:
        formated_time = time.localtime(time.time()+update_interval)

    # Create the update
    current_time_s = time.time()
    readable_schedule_time = time.asctime(formated_time)
    schedule_time = time.mktime(formated_time)
    update = {
        'title':update_name,
        'content':readable_schedule_time,
        'schedule':schedule,
        'time':schedule_time,
        'interval':update_interval,
        'repeat':False,
        'type':'news'
        }

    # Add update to updates list if it is not a repeat
    repeat = False
    for current_update in updates:
        if update['time'] == current_update['time']:
            repeat = True
    if not repeat:
        schedule.enter(schedule_time-current_time_s, 1, update_news)
        updates.append(update)
        updates = sorted(updates, key=lambda x:x['time'])

def get_updates() -> list:
    """Get the list of updates.

    Return values:
        updates -- list of future updates
    """
    return updates

def schedule_check_news() -> dict or bool:
    """Run the schedular.

    Return values:
        new -- completed update or False
    """
    # Run the schedular
    logger.log_infomation('Running news schedular')
    schedule_queue_length = len(schedule.queue)
    schedule.run(blocking=False)

    # If an update occured, get it
    new = False
    if len(schedule.queue) < schedule_queue_length:
        new = updates.pop(0)
        return new
    return new

def get_news() -> list:
    """Return a list of headlines.

    Return values:
        headlines -- list of current headlines
    """
    return headlines

def remove_news_update(name: str) -> bool:
    """Remove a news update from list of updates.

    Keyword arguements:
        name -- name of update

    Return values:
        removed -- whether an update was removed
    """
    logger.log_infomation('Remving news update')

    # Remove update from list of updates
    removed = remove_scheduled_update(name, updates)

    return removed

def set_repeating_news_update(update_name: str) -> None:
    """Set a news update to be repeating.

    Keyword arguements:
        update_name -- name of the update
    """
    logger.log_infomation('Setting repeating news update')

    # Set update to be repeating
    for update in updates:
        if update['title'] == update_name:
            update['repeat'] = True
            break
