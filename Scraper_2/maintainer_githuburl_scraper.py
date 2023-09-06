import time
import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# import metadata file
with open(
    "../rust_scraper/Scraper_1/Scraper_1_output.json", "r"
) as Scraper_1_input_json_file:
    metadata_list = json.load(Scraper_1_input_json_file)

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
    options=chrome_options,
)

# loop through crates.io project url list
for index_metadata, metadata in enumerate(metadata_list):
    try:
        project = metadata["project"]
        crates_url = metadata["crates_url"]
    except:
        continue

    if not crates_url is None:
        try:
            # go to the crates.io project page
            driver.get(crates_url)

            project_maintainer_github_url = None

            # get github url of project
            try:
                url_name_list = [
                    el.text
                    for el in WebDriverWait(driver, 2).until(
                        expected_conditions.presence_of_all_elements_located(
                            (By.XPATH, r"//*[@class='_title_t2rnmm _heading_rj9k29']")
                        )
                    )
                ]
                url_link_list = [
                    el.text
                    for el in WebDriverWait(driver, 2).until(
                        expected_conditions.presence_of_all_elements_located(
                            (By.XPATH, r"//*[@class='_link_t2rnmm']")
                        )
                    )
                ]

                for index, url_name in enumerate(url_name_list):
                    if url_name == "Repository":
                        github_url = url_link_list[index]

            except:
                github_url = None

            # get the list of project maintainer url
            try:
                project_maintainer_el_list = WebDriverWait(driver, 5).until(
                    expected_conditions.presence_of_all_elements_located(
                        (By.XPATH, r"//*[@class='_list_181lzn _detailed_181lzn']/li/a")
                    )
                )
            except:
                project_maintainer_el_list = WebDriverWait(driver, 5).until(
                    expected_conditions.presence_of_all_elements_located(
                        (By.XPATH, r"//*[@class='_list_181lzn']/li/a")
                    )
                )

            maintainer_url_list = []

            for project_maintainer_el in project_maintainer_el_list:
                # get the crates owner url
                maintainer_url = project_maintainer_el.get_attribute("href")
                maintainer_url_list.append(maintainer_url)

            for maintainer_url in maintainer_url_list:
                # get the project maintainer github repo
                driver.get(maintainer_url)

                try:
                    project_maintainer_github_el = WebDriverWait(driver, 2).until(
                        expected_conditions.presence_of_element_located(
                            (By.XPATH, r"//*[@class='_header-row_pld0lu']/a")
                        )
                    )

                    project_maintainer_github_url = (
                        project_maintainer_github_el.get_attribute("href")
                    )

                except:
                    project_maintainer_github_el = driver.find_element(
                        By.XPATH, r"//*[@class='_header_yor1li _header_1c6xgh']/a"
                    )

                    project_maintainer_github_url = (
                        project_maintainer_github_el.get_attribute("href")
                    )

                # append the maintainer/owner json file
                with open(
                    "../rust_scraper/Scraper_2/Scraper_2_output.json", "r"
                ) as Scraper_2_input_file:
                    maintainer_github_url_list = json.load(Scraper_2_input_file)

                maintainer_github_url_list.append(
                    {
                        "project": project,
                        "crates_url": crates_url,
                        "owner_url": project_maintainer_github_url,
                        "github_url": github_url,
                    }
                )

                with open(
                    "../rust_scraper/Scraper_2/Scraper_2_output.json", "w"
                ) as Scraper_2_output_file:
                    json.dump(
                        maintainer_github_url_list,
                        Scraper_2_output_file,
                        indent=4,
                        sort_keys=True,
                    )

        except Exception as e:
            # append the error json file
            with open(
                "../rust_scraper/Scraper_2/error_list.json", "r"
            ) as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append(
                {
                    "failed_requests": project,
                    "Index": str(index_metadata),
                    "Error": str(e),
                }
            )

            with open(
                "../rust_scraper/Scraper_2/error_list.json", "w"
            ) as error_list_output_json_file:
                json.dump(
                    error_list, error_list_output_json_file, indent=4, sort_keys=True
                )

            continue
