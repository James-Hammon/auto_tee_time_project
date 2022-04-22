import time
import yaml
import logging
import sys
from datetime import datetime
from typing import List
from helper_classes import User, Course
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from enums import Element as element_consts
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)


class JCGolfTeeTimeDriver():

    def __init__(self) -> None:
        self.driver = None
        self.login_info = None
        self.user = None
        self.logger = None
        self.tee_times = []

    def setup(self) -> bool:
        """Setup the webdriver
        :return: True if driver is setup
        """
        self.logger = logging.getLogger('JCGolfDriver')
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.info("running driver setup for chrome")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        # with headless
        # self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0, print_first_line=False).install(), chrome_options=chrome_options)
        self.driver = webdriver.Chrome(ChromeDriverManager(log_level=0, print_first_line=False).install())
        self.driver.maximize_window()
        with open(r'login.yaml') as file:
            self.login_info = yaml.full_load(file)
        self.logger.info('driver setup successful')
        return True

    def _click_button(self, button_element) -> bool:
        """Click a web element button
        :param button_class: class for button to be clicked
        :return: True if button is clicked successfully
        """
        button_element.click()
        return True

    def _enter_input(self, input_box_id: str, input: str) -> bool:
        """Enter email into input_box
        :param input_box_id: id of input_box to type email in to
        :param input: string input to go into box
        :return: True if email is entered
        """
        element = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.ID, input_box_id))
        )
        element.send_keys(input)
        element = self.driver.find_element(By.CLASS_NAME, element_consts.LOGIN_NEXT_BUTTON)
        return self._click_button(element)

    def _wait_for_element(self, element_class_name) -> bool:
        """Wait for the Tee Time list to refresh
        :param element_class_name: name of element class
        :return: True if list refreshes
        """
        self.logger.debug(f"waiting for {element_class_name}")
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, element_class_name))
        )
        return True


    def login(self, user_type='public', course_name='Encinitas Ranch') -> bool:
        """Login to the JCGolf website
        :param user_type: user type to login as
        :param course_name: Course to check times for
        :returns: True if login successful
        """
        self.user = User(user_type)
        self.course = Course(course_name)
        self.logger.info("logging into JCGolf site")
        self.driver.get(f"https://jc{self.user.sub_url}{self.course.url_number}.cps.golf/onlineresweb/search-teetime")
        if self.user.user_type is not 'public':
            self._enter_input(element_consts.LOGIN_TEXTBOX, self.login_info['email'])
            self._enter_input(element_consts.PASSWORD_TEXTBOX, self.login_info['password'])
        time.sleep(5)
        # below is broken, need to account for when current day does not have any tee times list
        # if self._wait_for_element(element_consts.TEE_TIME_LIST) or self._wait_for_element(element_consts.NO_TEE_TIME_LIST):
        self.logger.debug("tee time list generated")
        self.logger.info('jcgolf login successful')
        return True
        # return False

    def change_date(self) -> bool:
        """Change the current date for tee time search
        :return: return True if date changes
        """
        '''
        element = self.driver.find_element_by_class_name("mat-form-field"
            f".ng-tns-{self.user.date_sub_str}"
            ".mat-primary"
            ".mat-form-field-type-mat-input"
            ".mat-form-field-appearance-legacy"
            ".mat-form-field-can-float"
            ".mat-form-field-hide-placeholder")
        if not self._click_button(element):
            return False
        '''
        # today = self.driver.find_elements_by_class_name(element_consts.TODAY_DATE)[1]
        today = self.driver.find_element_by_class_name(element_consts.TODAY_DATE)
        elements = self.driver.find_elements_by_class_name(element_consts.DATE_BUTTON)
        today_index = 0
        for index, element in enumerate(elements):
            if element.text == today.text:
                today_index = index
                break
        offset_index = today_index + self.user.date_offset
        if not self._click_button(elements[offset_index]):
            return False
        # need to wait a second for click to register
        time.sleep(1)
        if not self._wait_for_element(element_consts.TEE_TIME_LIST):
            return False
        return True

    def get_available_tee_times(self) -> List:
        """Get a list of available Tee Times
        """
        # TODO: add wait for list to be available in case of auto-refresh
        tee_times =  self.driver.find_elements_by_class_name(element_consts.TEE_TIME_BUTTON)
        self.logger.debug(f'number of available tee times: {len(tee_times)}')
        return tee_times

    def filter_tee_times(self, tee_times: List) -> List:
        """Filter tee time results
        :param tee_times: list of tee_time selenium elements
        :return: filtered list of selenium elements
        """
        filtered_times = []
        self.logger.debug("filtering for only 4 person tee times")
        for tee_time in tee_times:
            # time, cart rate, holes/golfers, price
            _, _, players, _, = tee_time.text.split('\n')
            if '4 GOLFERS' in players:
                filtered_times.append(tee_time)
        self.logger.debug(f'number of filtered tee times: {len(filtered_times)}')
        return filtered_times

    def find_best_tee_time(self, tee_times: List, target_time: str):
        """Find the best tee time given a list and target star time
        :param tee_times: List of tee time web elements
        :param target_time: target starting time
        :return: tee time closest to target
        """
        self.logger.debug(f"filtering to time closest to {target_time}")
        target = datetime.strptime(target_time, "%I:%M %p")
        best_tee_time = tee_times[0]
        best_tee_time_start = datetime.strptime(best_tee_time.text.split('\n')[0], "%I:%M %p")
        for time in tee_times[1::]:
            tee_time_start = datetime.strptime(time.text.split('\n')[0], "%I:%M %p")
            if abs(target - tee_time_start) < abs(target - best_tee_time_start):
                best_tee_time = time
                best_tee_time_start = tee_time_start
            else:
                break
        best_tee_time_text = best_tee_time.text.split('\n')[0]
        self.logger.info(f'best tee time: {best_tee_time_text}')
        return best_tee_time

    def select_tee_time(self, tee_time_element: str) -> bool:
        """Select a tee time element
        :param tee_time_element: tee_time_element to click
        :return: True if button is clicked successfully
        """
        self.logger.info('selecting best tee time')
        return self._click_button(tee_time_element)

    def select_agreement_next(self) -> bool:
        """Select the next button on the agreement page
        :return: True if button is clicked successfully
        """
        time.sleep(10)
        self.logger.info('accepting agreement')
        element = self.driver.find_element_by_class_name(element_consts.AGREEMENT_NEXT_BUTTON)
        return self._click_button(element)

    def finalize_reservation(self) -> bool:
        """Click the finalize reservation button
        :returns: True if button is clicked successfully
        """
        self.logger.info('finalizing reservation!')
        # three confirmation pages confirmation page
        for _ in range(3):
            time.sleep(10)
            element = self.driver.find_element_by_class_name(element_consts.FINALIZE_RESERVATION_BUTTON)
            self._click_button(element)
