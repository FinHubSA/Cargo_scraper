import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

df = pd.read_excel('github_url_Data.xlsx')
# github_contributor_url_list = df['contributor_github_url'].tolist()
contributor_github_url_list = ['https://github.com/Moredread']

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

for contributor_github_url in contributor_github_url_list:

    driver.get(contributor_github_url)

    year_list = WebDriverWait(driver, 20).until(expected_conditions.presence_of_all_elements_located((By.XPATH, r"//*[@class='js-year-link filter-item px-3 mb-2 py-2']")))

    for index, year in enumerate(year_list):

        time.sleep(2)

        year_list = WebDriverWait(driver, 20).until(expected_conditions.presence_of_all_elements_located((By.XPATH, r"//*[@class='js-year-link filter-item px-3 mb-2 py-2']")))

        year_list[index].click()

        time.sleep(2)

        contributions = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, r"//*[@class='f4 text-normal mb-2']"))).text
        contributions = int(contributions.split(" ")[0])

        if contributions == 0:
            code_review = 0
            issues = 0
            pull_requests = 0
            commits = 0

        else:
            try:
                code_review = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, r"//*[@class='activity-overview-percentage js-highlight-percent-top']"))).text
                code_review = int(code_review.split("%")[0])
                code_review = code_review * contributions / 100
            except:
                code_review = 0
            
            try:
                issues = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, r"//*[@class='activity-overview-percentage js-highlight-percent-right']"))).text
                issues = int(issues.split("%")[0])
                issues = issues * contributions / 100
            except:
                issues = 0

            try:
                pull_requests = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, r"//*[@class='activity-overview-percentage js-highlight-percent-bottom']"))).text
                pull_requests = int(pull_requests.split("%")[0])
                pull_requests = pull_requests * contributions / 100
            except:
                pull_requests = 0

            try:
                commits = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH, r"//*[@class='activity-overview-percentage js-highlight-percent-left']"))).text
                commits = int(commits.split("%")[0])
                commits = commits * contributions / 100
            except:
                commits = 0

        element_list.append({'contributor_github_url':contributor_github_url, 'contributions':contributions,'code_review':code_review,'issues':issues,'pull_requests':pull_requests,'commits':commits})

    github_contributor_metadata = pd.DataFrame.from_records(element_list)     
    github_contributor_metadata.to_excel('github_contributor_metadata.xlsx')