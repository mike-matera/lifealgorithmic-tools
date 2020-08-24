"""
Get rosters from Cabrillo self-service.  
"""

import sys
import time
import json
import logging
import getpass 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import TimeoutException

logging.basicConfig(level=logging.INFO)


def main():
    username = input('User ID: ').strip()
    password = getpass.getpass('Password: ').strip()
    rosters = fetch(username, password)
    print(json.dumps(rosters))


def fetch(username, password):
    try:
        driver = webdriver.Firefox()
        driver.implicitly_wait(5)

        driver.get('https://success.cabrillo.edu/Student/')
        username_box = driver.find_element_by_id('userNameInput')
        password_box = driver.find_element_by_id('passwordInput')
        submit = driver.find_element_by_id('submitButton')

        username_box.send_keys(f'STUDENT\\{username}')
        password_box.send_keys(password)
        submit.submit() 

        try:
            faculty = driver.find_element_by_id('faculty')
        except:
            print('Login failed!')
            sys.exit(-1)

        driver.get('https://success.cabrillo.edu/Student/Student/Faculty')
        sectiontable = driver.find_elements_by_xpath('//td[@data-role="Section"]//a')
        section_urls = []
        for sectionlink in sectiontable:
            section_urls.append(sectionlink.get_attribute('href'))

        course_data = {}
        for section_url in section_urls:
            driver.get(section_url)
            time.sleep(0.5)
            course_fullname = driver.find_element_by_id('user-profile-name').text
            course_term = driver.find_element_by_id('section-header-term').text    
            course_id = course_fullname.split(':')[0]
            course_id += f':{course_term}'

            course_data[course_id] = {
                'term': course_term,
                'roster': [],
            }

            logging.info(f'Working on {course_fullname}')
        
            # Let the table load. Click the waitlist. 
            time.sleep(0.5)
            waitlist_button = driver.find_element_by_xpath('//a[@href="#waitlist-content-nav"]')
            waitlist_button.click()
            time.sleep(0.5)
            waitlist_button = driver.find_element_by_xpath('//a[@href="#roster-content-nav"]')
            waitlist_button.click()

            # Default wait for the first table to load. 
            driver.implicitly_wait(10) 
            roster_rows = driver.find_elements_by_xpath('//table[@id="faculty-roster-table"]//tr')
            for row in roster_rows[1:]:
                row_data = row.text.split('\n')
                if len(row_data) == 4:
                    course_data[course_id]['roster'].append({
                        'fullname': row_data[0],
                        'id': row_data[1],
                        'email': row_data[3],
                        'status': 'enrolled',
                    })
                    logging.info(f"Enrolled: {course_data[course_id]['roster'][-1]}")
                elif len(row_data) == 5:
                    # The user has added pronouns
                    course_data[course_id]['roster'].append({
                        'fullname': row_data[0],
                        'id': row_data[2],
                        'email': row_data[4],
                        'status': 'enrolled',
                    })
                    logging.info(f"Enrolled: {course_data[course_id]['roster'][-1]}")
                else:
                    logging.info(f'Failed to process: {row_data}')

            # Faster wait for the waitlist.
            waitlist_button = driver.find_element_by_xpath('//a[@href="#waitlist-content-nav"]')
            waitlist_button.click()
            driver.implicitly_wait(2)
            roster_rows = driver.find_elements_by_xpath('//table[@id="faculty-waitlist-table"]//tr')
            for row in roster_rows[1:]:
                row_data = row.text.split('\n')
                if len(row_data) == 6:
                    course_data[course_id]['roster'].append({
                        'fullname': row_data[0],
                        'id': row_data[1],
                        'email': row_data[5],
                        'status': 'wait',
                    })
                    logging.info(f"Wait list: {course_data[course_id]['roster'][-1]}")

    finally:
        driver.close()
    
    return course_data


if __name__ == '__main__':
    main()
