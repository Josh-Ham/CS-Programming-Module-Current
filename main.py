"""Main webpage module

Functions:
    process_requests -- processes user inputs
    render_page -- renders up-to-date page
"""
import json
from flask import Flask, render_template, request
from markupsafe import Markup

import covid_data_handler
import covid_news_handling
import logger

logger.log_infomation("Updating and fetching initial infomation")
covid_data_handler.update_covid_data()
covid_news_handling.update_news()
covid_data = covid_data_handler.get_covid_data()
news_articles = covid_news_handling.get_news()

app = Flask(__name__)

# Load config file
logger.log_infomation("Setting initial updates")
with open("config.json", 'r', encoding='utf8') as config:
    configerables = json.load(config)

# Set default updates from config file
if configerables['updates']:
    for set_update in configerables['updates']:
        if (
            (set_update['type'] == 'data') or
            (set_update['type'] == 'both')):
            covid_data_handler.schedule_covid_updates(
                set_update['time'], set_update['name']
            )
            if set_update['repeat'] == 'True':
                covid_data_handler.set_repeating_data_update(
                    set_update['name']
                )
        if (
            (set_update['type'] == 'news') or
            (set_update['type'] == 'both')):
            covid_news_handling.schedule_news_update(
                set_update['time'], set_update['name']
            )
            if set_update['repeat'] == 'True':
                covid_data_handler.set_repeating_data_update(
                    set_update['name']
                )

def process_requests(
    requests: any,
    data_updates: list,
    news_updates: list) -> tuple[list, list]:
    """Process user inputs.

    Keyword arguements:
        requests -- flask request,
        data_updates -- list of data updates,
        news_updates -- list of news updates

    Return values:
        data_updates -- list of data updates,
        news_updates -- list of news updates
    """
    global news_articles

    # Respond to headline removal.
    if 'notif' in requests.args:
        logger.log_infomation('Headline removal request')
        covid_news_handling.remove_headline(requests.args.get('notif'))
        news_articles = covid_news_handling.get_news()
    # Respond to new update creation.
    elif 'update' in requests.args:
        logger.log_infomation('New update request')
        if 'covid-data' in requests.args:
            covid_data_handler.schedule_covid_updates(
                requests.args.get('update'), requests.args.get('two')
                )
            if requests.args.get('repeat'):
                covid_data_handler.set_repeating_data_update(
                    requests.args.get('two')
                    )
            data_updates = covid_data_handler.get_updates()
        if 'news' in requests.args:
            covid_news_handling.schedule_news_update(
                requests.args.get('update'), requests.args.get('two')
                )
            if requests.args.get('repeat'):
                covid_news_handling.set_repeating_news_update(
                    requests.args.get('two')
                    )
            news_updates = covid_news_handling.get_updates()
        # Check if user didn't select either update
        elif 'covid-news' not in requests.args:
            logger.log_warning('No update type selected')
    # Respond to update removal.
    elif 'update_item' in requests.args:
        logger.log_infomation('Update removal request')
        if covid_data_handler.remove_data_update(
            requests.args.get('update_item')
            ):
            data_updates = covid_data_handler.get_updates()
        if covid_news_handling.remove_news_update(
            requests.args.get('update_item')
            ):
            news_updates = covid_news_handling.get_updates()

    return data_updates, news_updates

@app.route('/')
@app.route('/index')
def render_page() -> any:
    """Render the page.

    Return values:
        render_template -- render the html onto the webpage
    """
    global covid_data, news_articles

    # Run scheduler
    logger.log_infomation('Scheduler running')
    new_data = covid_data_handler.schedule_check_data()
    new_news = covid_news_handling.schedule_check_news()

    # Get latest updates
    logger.log_infomation('Getting updates')
    data_updates = covid_data_handler.get_updates()
    news_updates = covid_news_handling.get_updates()

    # Check if update should be repeated
    if new_data:
        logger.log_infomation('New covid data in main')
        if isinstance(new_data['repeat'], bool):
            covid_data_handler.schedule_covid_updates(
                new_data['interval'],
                new_data['title']
                )
            covid_data_handler.set_repeating_data_update(new_data['title'])
            data_updates = covid_data_handler.get_updates()
        covid_data = covid_data_handler.get_covid_data()
    elif new_news:
        logger.log_infomation('New news in main')
        if isinstance(new_news['repeat'], bool):
            covid_news_handling.schedule_news_update(
                new_news['interval'],
                new_news['title']
                )
            covid_news_handling.set_repeating_news_update(new_news['title'])
            news_updates = covid_news_handling.get_updates()
        news_articles = covid_news_handling.get_news()

    # Respond to user 
    data_updates, news_updates = process_requests(
        request,
        data_updates,
        news_updates
        )

    # Format updates
    logger.log_infomation('Configuring updates')
    updates = data_updates + news_updates
    updates = sorted(updates, key=lambda item: item.get('time'))

    # Merge updates that are for both data and news
    temp_updates = []
    updates_length = len(updates)
    for i in range(updates_length):
        if i == updates_length-1:
            temp_updates.append(updates[i])
        elif updates[i]['title'] == updates[i+1]['title']:
            updates[i+1]['type'] = 'data and news'
        else:
            temp_updates.append(updates[i])
    if temp_updates:
        updates = temp_updates.copy()
        for update in updates:
            if update['type'] not in update['content']:
                update['content'] = update['content']+", "+update['type']

    # Add link to each article
    for news_article in news_articles:
        if ". See more " not in news_article['content']:
            url = news_article['url']
            news_article['content'] += Markup(
                '. See more <a href='+url+'>here</a>.'
            )

    logger.log_infomation('Rednering page')
    return render_template(
        'index.html',
        updates=updates[:5],
        title=configerables['web_title'],
        location=covid_data['location'],
        local_7day_infections=covid_data['local_7day_infections'],
        nation_location=covid_data['nation'],
        national_7day_infections=covid_data['national_7day_infections'],
        hospital_cases='Hospital cases: '+str(covid_data['hospital_cases']),
        deaths_total='Total deaths: '+str(covid_data['deaths']),
        news_articles=news_articles[:4],
        image=configerables['image_path'],
        favicon='static/images/'+configerables['image_path']
        )

if __name__ == '__main__':
    app.run()
