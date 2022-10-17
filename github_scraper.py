import math
import pandas as pd
import time
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

df = pd.read_excel('Owner_url_Data.xlsx')
github_url_list = df['github_url'].tolist()

# Set User Agent and chrome option
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option(
    "prefs",
    {
        "download.prompt_for_download": False,  # To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,  # It will not show PDF directly in chrome
        "credentials_enable_service": False,  # gets rid of password saver popup
        "profile.password_manager_enabled": False,  # gets rid of password saver popup
    },
)
throttle = 0

# Start driver
driver = webdriver.Chrome(
    "/Users/danaebouwer/Documents/Work/rust_scraper/chromedriver",
    options=chrome_options,
)

element_list = []
github_url_prev = None

for github_url in github_url_list:
    print(github_url)

    if (github_url == github_url_prev or pd.isnull(github_url)):
        github_url_prev = github_url
        continue
    
    driver.get('https://' + github_url)

    time.sleep(5)

    heading_text_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@Class='h4 mb-3']/a")]
    heading_el_list = [el for el in driver.find_elements(By.XPATH, r"//*[@Class='h4 mb-3']/a")]

    for index, heading in enumerate(heading_text_list):
        
        if re.findall('Contributors',heading):
            heading_el_list[index].click()

    time.sleep(5)

    loading_page = True

    try:
        while loading_page == True:
            loading = driver.find_element(By.XPATH,"//*[@class = 'js-date-range Subhead-heading']").text
            if not loading == 'Loading contributions…':
                loading_page = False

        # get contributor number
        contributor_github_no_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@class='f5 text-normal color-fg-muted float-right']")]
        print(contributor_github_no_list)

        # get contributor github url
        contributor_github_url_list = [el.get_attribute('href') for el in driver.find_elements(By.XPATH, r"//*[@class='d-inline-block mr-2 float-left']")]
        print(contributor_github_url_list)

        #get contributor number of commmits
        contributor_github_commits_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@class='cmeta']/div/a")]
        print(contributor_github_commits_list)

        for index in range(0,len(contributor_github_no_list)):
            element_list.append({'github_url': github_url, 'no':contributor_github_no_list[index],'contributor_github_url': contributor_github_url_list[index],'contributor_github_commits': contributor_github_commits_list[index]})
    except:
        no = '#1'
        contributor_github_url = "https://" + github_url.split("/")[0] + "/" +github_url.split("/")[1]
        contributor_github_commits = driver.find_element(By.XPATH,r"//*[@class='d-none d-sm-inline']/strong").text

        element_list.append({'github_url': github_url, 'no': no,'contributor_github_url': contributor_github_url,'contributor_github_commits': contributor_github_commits + 'commits'})
        
    github_url_Data = pd.DataFrame.from_records(element_list)     
    github_url_Data.to_excel('github_url_Data.xlsx')

    github_url_prev = github_url
        








