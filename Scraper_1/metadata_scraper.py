import csv
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By

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
        "download.prompt_for_download": False,  # to auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,  # it will not show PDF directly in chrome
        "credentials_enable_service": False,  # gets rid of password saver popup
        "profile.password_manager_enabled": False,  # gets rid of password saver popup
    },
)
throttle = 0

# Start driver
driver = webdriver.Chrome(
    options=chrome_options,
)

count = 0

# load Cargo projects list from csv file
with open("../rust_scraper/names_projects_Cargo.csv") as csv_file:
    project_list = csv.DictReader(csv_file)

    # loop through Cargo projects list
    for index_project, project in enumerate(project_list):
        count += 1

        # restart chromedriver after x number of projects
        if count == 500:
            count = 0

            driver.close()

        # Start driver
        driver = webdriver.Chrome(
            options=chrome_options,
        )

        try:
            # go to libraries.io to retrieve the project data
            project_name = project["project"]

            project_url = "https://libraries.io/cargo/" + str(project["project"])

            driver.get(project_url)

            # Check for too many requests error
            time.sleep(1)

            too_many_requests = True
            count_requests_error = 0

            while too_many_requests and count_requests_error <= 10:
                error_429 = driver.find_element(By.XPATH, r"//*").text

                if error_429 == "429 Too Many Requests":
                    count_requests_error += 1
                    print("error_429: " + project_name)
                    time.sleep(20)
                    driver.get(project_url)
                else:
                    too_many_requests = False

            # set the time between requests to avoid error 429 (too many requests)
            time.sleep(10)

            # set variable default values
            Latest_release = None
            First_release = None
            Stars = None
            Forks = None
            Watch = None
            Contributors = None
            Repository_size = None
            Total_releases = None
            crates_url = None
            github_repo = None

            # get the project links (crates.io and GitHub)
            project_el_list = driver.find_elements(
                By.XPATH, r"//*[@class='project-links']/span/a"
            )
            for project_el in project_el_list:
                project_link_name = project_el.text
                if project_link_name == "Cargo":
                    crates_url = project_el.get_attribute("href")
                elif project_link_name == "Repository":
                    github_repo = project_el.get_attribute("href")
                else:
                    continue

            # get the project metadata
            element_tag_name_list = [
                el.text
                for el in driver.find_elements(
                    By.XPATH,
                    r"//*[@class='col-md-4 sidebar']/dl[@class='row detail-card']/dt",
                )
            ]
            element_tag_value_list = [
                el.text
                for el in driver.find_elements(
                    By.XPATH,
                    r"//*[@class='col-md-4 sidebar']/dl[@class='row detail-card']/dd",
                )
            ]

            for index, element_tag_name in enumerate(element_tag_name_list):
                if element_tag_name == "Latest release":
                    Latest_release = element_tag_value_list[index]
                elif element_tag_name == "First release":
                    First_release = element_tag_value_list[index]
                elif element_tag_name == "Stars":
                    Stars = element_tag_value_list[index]
                elif element_tag_name == "Forks":
                    Forks = element_tag_value_list[index]
                elif element_tag_name == "Watchers":
                    Watch = element_tag_value_list[index]
                elif element_tag_name == "Contributors":
                    Contributors = element_tag_value_list[index]
                elif element_tag_name == "Repository size":
                    Repository_size = element_tag_value_list[index]
                elif element_tag_name == "Total releases":
                    Total_releases = element_tag_value_list[index]
                else:
                    continue

            # append the metadata json file
            with open(
                "../rust_scraper/Scraper_1/Scraper_1_output.json", "r"
            ) as Scraper_1_input_json_file:
                metadata_list = json.load(Scraper_1_input_json_file)

            metadata_list.append(
                {
                    "project": project_name,
                    "Latest_release": Latest_release,
                    "First_release": First_release,
                    "Stars": Stars,
                    "Forks": Forks,
                    "Watch": Watch,
                    "Contributors": Contributors,
                    "repository_size": Repository_size,
                    "total_releases": Total_releases,
                    "crates_url": crates_url,
                    "github_repo": github_repo,
                }
            )

            with open(
                "../rust_scraper/Scraper_1/Scraper_1_output.json", "w"
            ) as Scraper_1_output_json_file:
                json.dump(
                    metadata_list, Scraper_1_output_json_file, indent=4, sort_keys=True
                )

        except Exception as e:
            # append the error json file
            with open(
                "../rust_scraper/Scraper_1/error_list.json", "r"
            ) as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append(
                {
                    "failed_requests": project,
                    "Index": str(index_project),
                    "Error": str(e),
                }
            )

            with open(
                "../rust_scraper/Scraper_1/error_list.json", "w"
            ) as error_list_output_json_file:
                json.dump(
                    error_list, error_list_output_json_file, indent=4, sort_keys=True
                )

            time.sleep(60)

            continue
