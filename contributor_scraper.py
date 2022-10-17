import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

df = pd.read_excel('project_metadata.xlsx')
crates_url_list = df['crates_url'].tolist()

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

for crates_url in crates_url_list:

    driver.get(crates_url)

    time.sleep(5)

    github_url = None
    project_owner_github_url = None

    # get github url
    url_name_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='_title_t2rnmm']")]
    url_link_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='_link_t2rnmm']")]

    for index, url_name in enumerate(url_name_list):
        if url_name == "Repository":
            github_url = url_link_list[index]
    
    time.sleep(5)

    # get the list of crates owner url
    project_owner_el_list = driver.find_elements(By.XPATH,r"//*[@class='_list_181lzn _detailed_181lzn']/li/a")

    owner_url_list = []

    for project_owner_el in project_owner_el_list:

        # get the crates owner url
        owner_url = project_owner_el.get_attribute('href')
        owner_url_list.append(owner_url)

    for owner_url in owner_url_list:

        # get the crates owner github repo
        driver.get(owner_url)

        time.sleep(3)

        project_owner_github_el = driver.find_element(By.XPATH,r"//*[@class='_header_yor1li _header_1c6xgh']/a")

        project_owner_github_url = project_owner_github_el.get_attribute('href')

        element_list.append({'crates_url': crates_url,'owner_url': project_owner_github_url, 'github_url': github_url})

Owner_url_Data = pd.DataFrame.from_records(element_list)     
Owner_url_Data.to_excel('Owner_url_Data.xlsx')