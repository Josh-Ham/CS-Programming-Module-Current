"""Covid data handling module.

Fuctions:
parse_csv_data -- gets CSV data from file
process_covid_csv_data -- gets specific data from the covid data
covid_API_request -- makes a API request to Cov19API
schedule_covid_updates -- schedules updates
update_covid_data -- gets updated covid data
process_covid_local_dict_data -- gets specific local covid data
process_covid_country_dict_data -- gets specific national covid data
get_updates -- gets uncompleted updates
schedule_check_data -- runs scheduler
get_covid_data -- gets formatted covid data
remove_data_update -- removes future update
set_repeating_data_update -- makes an update repeat
"""
import time
import sched
import json

from uk_covid19 import Cov19API

import logger

from shared_functions import remove_scheduled_update, time_format

# Load config file
with open("config.json", 'r', encoding='utf8') as config:
    configerables = json.load(config)

# Declare global variables
updates = []
covid_data = {}
schedule = sched.scheduler(time.time, time.sleep)

def parse_csv_data(csv_filename: str) -> list:
    """Get a list of strings for each line of the file.

    Keyword arguements:
    csv_filename -- csv data filename

    Return values:
    csv_data -- list of line of the csv file
    """
    with open(csv_filename, encoding='utf8') as csv_file:
        csv_data = csv_file.readlines()
    return csv_data

def process_covid_csv_data(
    covid_csv_data: list
    ) -> tuple[int, int, int]:
    """Get cases, hospital cases and deaths from the Covid data.

    Keyword arguements:
    covid_csv_data -- list of strings of lines from a csv file

    Return values:
    last7days_cases -- number of covid cases in the last 7 days,
    current_hospital_cases -- number of current hospital cases,
    total_deaths -- total number of covid related deaths
    """
    # Calculate the last 7 day cases
    last7days_cases = 0
    start = 1
    while not covid_csv_data[start].strip().split(",")[-1]:
        start += 1
    start += 1
    for count in range(7):
        day = covid_csv_data[count+start].strip().split(",")[-1]
        last7days_cases += int(day)

    # Get the latest hospital cases
    index = 1
    while not covid_csv_data[index].strip().split(",")[-2]:
        index += 1
    current_hospital_cases = int(covid_csv_data[index].strip().split(",")[-2])

    # Get the latest total deaths
    found = False
    row = 1
    while not found and row < len(covid_csv_data):
        total_deaths = covid_csv_data[row].strip().split(",")[-3]
        if  total_deaths:
            found = True
            total_deaths = int(total_deaths)
        row += 1
    if not found:
        total_deaths = 0

    return last7days_cases, current_hospital_cases, total_deaths

def covid_API_request(
    location: str = configerables['location'],
    location_type: str = configerables['location_type']) -> dict:
    """Get up-to-date Covid data as a dictionary.

    Optional arguements:
    location -- location to get data from,
    location_type -- type of location to get data from
    """
    # Set up search terms
    filters = ['areaType='+location_type, 'areaName='+location]
    metrics = {
        'areaCode':'areaCode',
        'areaName':'areaName',
        'areaType':'areaType',
        'date':'date',
        'cumDailyNsoDeathsByDeathDate':'cumDailyNsoDeathsByDeathDate',
        'hospitalCases':'hospitalCases',
        'newCasesBySpecimenDate':'newCasesBySpecimenDate'
    }

    # Get data from API
    logger.log_infomation('Getting covid data')
    new_data = Cov19API(filters=filters, structure=metrics)
    json_data = new_data.get_json()

    if not json_data:
        logger.log_error('No covid API data')

    return json_data

def schedule_covid_updates(
    update_interval: str,
    update_name: str
    ) -> None:
    """Schedule data updates using sched

    Keyword arguements:
    update_interval -- time of day the update takes place
    update_name -- name of the update
    """
    global updates

    # Format the update_iterval.
    if isinstance(update_interval, str):
        formated_time = time_format(update_interval)
    else:
        formated_time = time.localtime(time.time()+update_interval)

    # Create update.
    logger.log_infomation('Creating data update')
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
        'type':'data'
        }

    # Add update to updates list if it's not a repeat.
    repeat = False
    for current_update in updates:
        if update['time'] == current_update['time']:
            logger.log_warning('Data update already at specified time')
            repeat = True
    if not repeat:
        updates.append(update)
        schedule.enter(schedule_time-current_time_s, 1, update_covid_data)
        updates = sorted(updates, key=lambda x:x['time'])

def update_covid_data() -> None:
    """Update the Covid-19 data."""
    global covid_data

    # Get local and national covid data.
    logger.log_infomation('Updating covid data')
    location, local_7day_infections = (
        process_covid_local_dict_data(covid_API_request())
    )
    nation, national_7day_infactions, hospital_cases, deaths_total = (
        process_covid_country_dict_data(
            covid_API_request(location="England", location_type='nation')
            )
    )
    # Combine the covid data.
    covid_data =  {
        'location':location,
        'local_7day_infections':local_7day_infections,
        'nation':nation,
        'national_7day_infections':national_7day_infactions,
        'hospital_cases':hospital_cases,
        'deaths':deaths_total
        }

def process_covid_local_dict_data(
    covid_dict_data: dict
    ) -> tuple[str, int]:
    """Gets the location and 7 day infections.

    Keyword arguements:
    covid_dict_data -- local covid data

    Return values:
    location -- data location,
    local_7day_infections -- last 7 days infections
    """
    # Get data and location (from the data)
    logger.log_infomation('Processing local covid data')
    data = covid_dict_data['data']
    location = data[0]['areaName']

    # Calculate the local 7 day infection rate.
    index = 0
    while not data[index]['newCasesBySpecimenDate']:
        index += 1
    index += 1
    local_7day_infections = 0
    for counter in range(7):
        if (counter+index) < len(data):
            local_7day_infections += (
                data[counter+index]['newCasesBySpecimenDate']
            )
        else:
            break

    return location, local_7day_infections

def process_covid_country_dict_data(
    covid_dict_data: dict
    ) -> tuple[str, int, int, int]:
    """Get the location, weekly infections, hospital cases and deaths.

    Keyword arguements:
    covid_dict_data -- national covid data

    Return values:
    location -- data location
    national_7day_infections -- last 7 day infections
    hospital_cases -- current hospital cases
    deaths_total -- current death toll
    """
    # Get data and location (from the data)
    logger.log_infomation('Processing national covid data')
    data = covid_dict_data['data']
    location = data[0]['areaName']

    # Calculate national 7 day infection rate.
    index = 0
    while not data[index]['newCasesBySpecimenDate']:
        index += 1
    index += 1
    national_7day_infections = 0
    for counter in range(7):
        if (counter+index) < len(data):
            national_7day_infections += (
                data[counter+index]['newCasesBySpecimenDate']
            )
        else:
            break

    # Get national hospital cases.
    index = 0
    while not data[index]['hospitalCases']:
        index += 1
    hospital_cases = data[index]['hospitalCases']
    if not hospital_cases:
        logger.log_warning('No hospital cases found')
        hospital_cases = 0

    # Get national deaths.
    index = 0
    while not data[index]['cumDailyNsoDeathsByDeathDate']:
        index += 1
    deaths_total = data[index]['cumDailyNsoDeathsByDeathDate']

    return location, national_7day_infections, hospital_cases, deaths_total

def get_updates() -> list:
    """Get the list of updates."""
    return updates

def schedule_check_data() -> dict or bool:
    """Runs the schedular.

    Return values:
    done -- completed update or False
    """
    # Run schedular
    logger.log_infomation('Data schedular running')
    schedule_queue_length = len(schedule.queue)
    schedule.run(blocking=False)

    # Get completed update if an update occured.
    done = False
    if len(schedule.queue) < schedule_queue_length:
        done = updates.pop(0)
        return done

    return done

def get_covid_data() -> dict:
    """Get the covid data."""
    return covid_data

def remove_data_update(name: str) -> bool:
    """Remove a data update from the list of updates.

    Keyword arguments:
    name -- name of the update

    Return values:
    removed -- whether the update was removed or not
    """
    logger.log_infomation('Removing data update')

    # Remove update from list of updates
    removed = remove_scheduled_update(name, updates)

    return removed

def set_repeating_data_update(update_name: str) -> None:
    """Set a data update to be repeating.

    Keyword arguements:
    update_name -- name of the update
    """
    logger.log_infomation('Set update to be repeating')

    # Find update, and set to be repeating
    for update in updates:
        if update['title'] == update_name:
            update['repeat'] = True
            break
