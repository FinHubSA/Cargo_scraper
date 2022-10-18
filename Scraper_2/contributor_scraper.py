import pandas as pd
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By

# import metadata file
with open("/Users/danaebouwer/Documents/Work/rust_scraper/Scraper_2/metadata.json", "r") as metadata_input_json_file:
    metadata_list = json.load(metadata_input_json_file)

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

for index_metadata, metadata in enumerate(metadata_list):

    project = metadata['project']
    crates_url = metadata['crates_url']

    try:

        # go to the crates url page for project
        driver.get(crates_url)

        time.sleep(3)

        github_url = None
        project_maintainer_github_url = None

        # get github url of project
        url_name_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='_title_t2rnmm']")]
        url_link_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='_link_t2rnmm']")]

        for index, url_name in enumerate(url_name_list):
            if url_name == "Repository":
                github_url = url_link_list[index]
        
        time.sleep(3)

        # get the list of project maintainer url
        project_maintainer_el_list = driver.find_elements(By.XPATH,r"//*[@class='_list_181lzn _detailed_181lzn']/li/a")

        maintainer_url_list = []

        for project_maintainer_el in project_maintainer_el_list:

            # get the crates owner url
            maintainer_url = project_maintainer_el.get_attribute('href')
            maintainer_url_list.append(maintainer_url)

        for maintainer_url in maintainer_url_list:

            # get the project maintainer github repo
            driver.get(maintainer_url)

            time.sleep(3)

            project_maintainer_github_el = driver.find_element(By.XPATH,r"//*[@class='_header_yor1li _header_1c6xgh']/a")

            project_maintainer_github_url = project_maintainer_github_el.get_attribute('href')

            with open("/Users/danaebouwer/Documents/Work/rust_scraper/Scraper_2/maintainer_github_url.json", "r") as maintainer_github_input_file:
                maintainer_github_url_list = json.load(maintainer_github_input_file)

            maintainer_github_url_list.append({'project': project, 'crates_url': crates_url,'owner_url': project_maintainer_github_url, 'github_url': github_url})

            with open("/Users/danaebouwer/Documents/Work/rust_scraper/Scraper_2/maintainer_github_url.json", "w") as maintainer_github_output_file:
                json.dump(maintainer_github_url_list, maintainer_github_output_file, indent=4, sort_keys=True)

    except Exception as e:

        time.sleep(60)

        with open("/Users/danaebouwer/Documents/Work/rust_scraper/Scraper_2/error_list.json", "r") as error_list_input_json_file:
            error_list = json.load(error_list_input_json_file)

        error_list.append({'failed_requests': project, 'Index': str(index_metadata), 'Error': str(e)})
        
        with open("/Users/danaebouwer/Documents/Work/rust_scraper/Scraper_2/error_list.json", "w") as error_list_output_json_file:
            json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

        continue