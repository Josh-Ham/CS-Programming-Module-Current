from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import process_covid_local_dict_data
from covid_data_handler import process_covid_country_dict_data
from covid_data_handler import get_updates
from covid_data_handler import get_covid_data
from covid_data_handler import remove_data_update
from covid_data_handler import update_covid_data
from covid_data_handler import schedule_check_data
from covid_data_handler import set_repeating_data_update

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test')

def test_process_covid_local_dict_data():
    location, local_7day_infections = \
        process_covid_local_dict_data(
        covid_API_request()
    )
    assert location == 'Exeter'
    assert isinstance(local_7day_infections, int)

def test_process_covid_country_dict_data():
    location, day7_infections, hospital_cases, deaths_total = \
    process_covid_country_dict_data(
        covid_API_request(location='England', location_type='nation')
    )
    assert location == 'England'
    assert isinstance(day7_infections, int)
    assert isinstance(hospital_cases, int)
    assert isinstance(deaths_total, int)

def test_get_updates():
    updates = get_updates()
    assert isinstance(updates, list)

def test_get_covid_data():
    covid_data = get_covid_data()
    assert isinstance(covid_data, dict)

def test_remove_data_update():
    removed = remove_data_update('Test Name')
    assert isinstance(removed, bool)

def test_update_covid_data():
    update_covid_data()

def test_schedule_check_data():
    schedule_check_data()

def test_set_repeating_data_update():
    schedule_covid_updates('10:10', 'test')
    set_repeating_data_update('test')