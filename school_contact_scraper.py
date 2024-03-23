from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import numpy as np
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
import re
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(ChromeDriverManager().install())

driver.get("https://schoolsearch.schools.nyc/")

### Filter for Manhattan 

boroughElement = Select(driver.find_element_by_id('Borough'))
boroughElement.select_by_value('M')

login_link = driver.find_element("id", 'Borough')
login_link.click()

### Hit search

login_link = driver.find_element("id", 'states-autocomplete')
login_link.click()
value = " "
actions = ActionChains(driver)
actions.send_keys(Keys.ENTER)
actions.perform()

time.sleep(1)
xpath_element = "//div[contains(@class, 'iScroll')]"
fBody = driver.find_element_by_xpath(xpath_element)

scroll = 0
while scroll < 225:
    driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;',
                          fBody)
    scroll += 1
    time.sleep(1)
    print(scroll)

### Get ZIP Code / Principal / Parent Contact from each

school_names = []
roles = []
names = []
emails = []
zipcodes = []
main_dict = {}
school_items = driver.find_elements(By.CLASS_NAME, 'school-item')

for item in school_items:
    school_name = item.get_attribute('data-name')
    link = item.find_element(By.CSS_SELECTOR, "h2.title a")

    # Click the link to navigate
    link.click()

    # Wait for the new page to load or for a new window/tab to appear
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//body")))

    # If a new window/tab is expected, you need to switch to it
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])

    # Parse zip code
    try:
        meta_tag = driver.find_element_by_xpath("//meta[@name='description'][2]")
        meta_content = meta_tag.get_attribute('content')  # Use regular expression to find zip codes in the content
        zip_code_pattern = re.compile(r'\b\d{5}\b')
        match = zip_code_pattern.search(meta_content)
        zipcode = match.group()
    except Exception as e:
        print(e)
        zipcode = 0

    # Parse role, name and email 
    try:
        email_elements = driver.find_elements(By.XPATH, "//dd/a[contains(@href, 'mailto')]")
        for element in email_elements:
            email_address = element.get_attribute('href').replace('mailto:', '')  # Remove 'mailto:' part
        role_element = element.find_element(By.XPATH, "./../preceding-sibling::dt[1]")
        role = role_element.get_attribute("textContent")
        name = driver.execute_script("return arguments[0].innerText;", element).strip()

        school_names.append(school_name)
        roles.append(role)
        names.append(name)
        emails.append(email_address)
        zipcodes.append(zipcode)

        # print(f"Role: {role}, Name: {name}, Email: {email_address}, Zipcode: {zipcode}")

    except Exception as e:
        print(e)
        email_address = "NO CONTACT"

    # If you had switched to a new window/tab, you might want to close it and switch back
    if len(driver.window_handles) > 1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    print(school_name)

results = pd.DataFrame(
    {'School Name': school_names,
     'Zipcode': zipcodes,
     'Role': roles,
     'Name': names,
     'Email': emails,
     })

results[results["School Name"].str.contains("Stuyvesant")]

results.to_clipboard()