from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime
import calendar


def get_current_date() -> (int, int, int):
    now = datetime.now()
    return now.day, now.month, now.year


def increment_month(month: int) -> int:
    if month == 12:
        month -= 12
    month += 1
    return month


def get_num_of_days(month: int, year: int):

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29

    return days_in_month[month - 1]


class BrowserFetcher:
    def __init__(self, close_after_usage: bool = True):
        options = Options()

        if not close_after_usage:
            options.add_experimental_option('detach', True)
        options.add_argument("--incognito")
        # options.add_argument("--headless")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.driver.maximize_window()


class RyanairWrapper(BrowserFetcher):
    def __init__(self, departure_airport: str, arrival_airport: str):
        super().__init__()
        self._url = 'https://www.ryanair.com/pl/pl'
        self._flight_data = FlightData(departure_airport, arrival_airport)

    # Four months ahead
    def open_ryanair_page(self):
        self.driver.get(self._url)
        time.sleep(1.0)

        self.driver.find_element('xpath', '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[3]').click()
        self.driver.find_element('xpath', "//*[contains(text(),'jedną stronę')]").click()

        self._set_departure_airport(self._flight_data.departure_airport)

        self._set_arrival_airport(self._flight_data.arrival_airport)

    def get_flight_prices(self, number_of_days: int) -> dict:
        month = self._flight_data.month  # local variable, because month will be incremented

        self.open_ryanair_page()

        if not self._set_elastic_date(self._flight_data.month_name,
                                      self._flight_data.last_day,
                                      str(self._flight_data.year)[2:]):
            return {}

        self.driver.find_element('xpath', "//*[@aria-label='Szukaj']").click()
        time.sleep(5.0)
        days = {}
        next_month_fd = self.driver.find_element('xpath',
                                                 '//icon[@class="month-selector__'
                                                 'arrow month-selector__arrow--next-month"]')
        days_in_month = get_num_of_days(month, self._flight_data.year)
        days.update(self._get_prices(month, self._flight_data.year, min(days_in_month, number_of_days)))
        number_of_days -= (get_num_of_days(month, self._flight_data.year) - self._flight_data.day)
        time.sleep(0.25)

        while number_of_days > 0:
            month = increment_month(month)
            days_in_month = get_num_of_days(month, self._flight_data.year)
            next_month_fd.click()
            time.sleep(0.25)
            days.update(self._get_prices(month, self._flight_data.year, min(days_in_month, number_of_days)))
            time.sleep(0.25)
            number_of_days -= days_in_month

        return days

    def _get_prices(self, month: int, year: int, end_at: int = 31) -> dict:

        days_fd = self.driver.find_elements('xpath',
                                            '//priced-date[contains(@class, "priced-calendar-body__priced-date")]'
                                            )
        days = {}
        for day_fd in days_fd:
            day_info = day_fd.text.split("\n")
            if len(day_info) == 2:
                if month > 9:
                    days[f'{day_info[0]}-{month}-{year}'] = day_info[1]
                else:
                    days[f'{day_info[0]}-0{month}-{year}'] = day_info[1]
                if int(day_info[0]) >= end_at:
                    if len(days) != end_at:
                        print(f'No flights were collected for each day in {month}.')
                    return days

        if len(days) < 30:
            print(f'No flights were collected for each day in {month}.')
        return days

    def _set_departure_airport(self, airport: str):
        departure_fd = self.driver.find_element('xpath', '//*[@id="input-button__departure"]')
        departure_fd.send_keys(Keys.CONTROL + "a")
        departure_fd.send_keys(Keys.DELETE)
        departure_fd.send_keys(airport)

    def _set_arrival_airport(self, airport: str):
        destination_fd = self.driver.find_element('xpath', '//*[@id="input-button__destination"]')
        destination_fd.send_keys(airport)
        time.sleep(0.1)
        destination_fd.send_keys(Keys.ENTER)
        time.sleep(0.5)

    def _set_elastic_date(self, month: str, last_day: str, year_suffix: str) -> bool:
        try:
            destination_date_bt = self.driver.find_element('xpath', '//*[@id="ry-tooltip-11"]')
        except NoSuchElementException:
            print('Please check airports correctness.')
            return False
        destination_date_bt.find_element('xpath', "//*[contains(text(),'Elastyczne daty')]").click()
        try:
            destination_date_bt.find_element('xpath', f"//*[contains(text(),'{month} {year_suffix}')]").click()
            destination_date_bt.find_element('xpath', f"//*[contains(text(),'{last_day}')]").click()
            destination_date_bt.find_element('xpath', "//*[@aria-label='Zastosuj']").click()
        except NoSuchElementException:
            print('Please check month correctness.')
            return False
        return True


class FlightData:
    def __init__(self,
                 departure_airport: str,
                 arrival_airport: str):

        day, month, year = get_current_date()

        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.year = year
        self.month = month
        self.month_name = month
        self.day = day
        self.last_day = month

    @property
    def departure_airport(self) -> str:
        return self._departure_airport

    @departure_airport.setter
    def departure_airport(self, value: str):
        self._departure_airport = value

    @property
    def arrival_airport(self) -> str:
        return self._arrival_airport

    @arrival_airport.setter
    def arrival_airport(self, value: str):
        self._arrival_airport = value

    @property
    def year(self) -> int:
        return self._year

    @year.setter
    def year(self, value: int):
        self._year = value

    @property
    def month(self) -> int:
        return self._month

    @month.setter
    def month(self, value: int):
        self._month = value

    @property
    def month_name(self) -> str:
        return self._month_name

    @month_name.setter
    def month_name(self, value: int):
        months = {
            1: 'Sty',
            2: 'Lut',
            3: 'Mar',
            4: 'Kwi',
            5: 'Maj',
            6: 'Cze',
            7: 'Lip',
            8: 'Sie',
            9: 'Wrz',
            10: 'Paź',
            11: 'Lis',
            12: 'Gru'
        }
        if value not in months:
            self._month_name = ''
        else:
            self._month_name = months[value]

    @property
    def day(self) -> int:
        return self._day

    @day.setter
    def day(self, value: int):
        self._day = value

    @property
    def last_day(self) -> str:
        return self._last_day

    @last_day.setter
    def last_day(self, month: int):
        year = datetime.now().year
        last_day = calendar.monthrange(year, month)[1]
        day_of_the_week = datetime(year, month, last_day).strftime('%A')
        days_dist = {
            'Monday': 'Pon.',
            'Tuesday': 'Wt.',
            'Wednesday': 'Śr.',
            'Thursday': 'Czw.',
            'Friday': 'Pt.',
            'Saturday': 'Sob.',
            'Sunday': 'Niedz.'
        }
        day_of_the_week_fixed = days_dist[day_of_the_week]
        self._last_day = day_of_the_week_fixed
