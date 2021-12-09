from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import remove_headline
from covid_news_handling import schedule_news_update
from covid_news_handling import get_updates
from covid_news_handling import get_news
from covid_news_handling import remove_news_update
from covid_news_handling import schedule_check_news
from covid_news_handling import set_repeating_news_update

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news()

def test_remove_headline():
    remove_headline('test')

def test_schedule_news_update():
    schedule_news_update(100, 'test 3')

def test_get_updates():
    updates = get_updates()
    assert isinstance(updates, list)

def test_get_news():
    headlines = get_news()
    assert isinstance(headlines, list)

def test_remove_news_update():
    removed = remove_news_update('test')
    assert isinstance(removed, bool)

def test_schedule_check_news():
    schedule_check_news()

def test_set_repeating_news_update():
    schedule_news_update('10:10', 'test')
    set_repeating_news_update('test')
