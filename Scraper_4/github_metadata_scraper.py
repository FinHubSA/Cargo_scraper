import time
import json
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

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


# function that gets the yearly github data (code review, issues, pull requests and commits)
def yearly_metadata(date):
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.presence_of_element_located(
                (
                    By.XPATH,
                    r"//*[@class='Box mb-5 p-3 activity-overview-box border-top border-xl-top-0']",
                )
            )
        )

        contributions = (
            WebDriverWait(driver, 5)
            .until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, r"//*[@class='f4 text-normal mb-2']")
                )
            )
            .text
        )
        contributions = contributions.split(" ")[0]
        contributions = int(contributions.replace(",", ""))

        if contributions == 0:
            code_review = 0
            issues = 0
            pull_requests = 0
            commits = 0

        else:
            try:
                code_review = (
                    WebDriverWait(driver, 5)
                    .until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                r"//*[@class='activity-overview-percentage js-highlight-percent-top']",
                            )
                        )
                    )
                    .text
                )
                code_review = int(code_review.split("%")[0])
                code_review = code_review * contributions / 100
            except:
                code_review = 0

            try:
                issues = (
                    WebDriverWait(driver, 5)
                    .until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                r"//*[@class='activity-overview-percentage js-highlight-percent-right']",
                            )
                        )
                    )
                    .text
                )
                issues = int(issues.split("%")[0])
                issues = issues * contributions / 100
            except:
                issues = 0

            try:
                pull_requests = (
                    WebDriverWait(driver, 5)
                    .until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                r"//*[@class='activity-overview-percentage js-highlight-percent-bottom']",
                            )
                        )
                    )
                    .text
                )
                pull_requests = int(pull_requests.split("%")[0])
                pull_requests = pull_requests * contributions / 100
            except:
                pull_requests = 0

            try:
                commits = (
                    WebDriverWait(driver, 5)
                    .until(
                        expected_conditions.presence_of_element_located(
                            (
                                By.XPATH,
                                r"//*[@class='activity-overview-percentage js-highlight-percent-left']",
                            )
                        )
                    )
                    .text
                )
                commits = int(commits.split("%")[0])
                commits = commits * contributions / 100
            except:
                commits = 0
    except:
        contributions = (
            WebDriverWait(driver, 5)
            .until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, r"//*[@class='f4 text-normal mb-2']")
                )
            )
            .text
        )
        contributions = contributions.split(" ")[0]
        contributions = int(contributions.replace(",", ""))

        code_review = None
        issues = None
        pull_requests = None
        commits = None

    # append the github metadata json file
    with open(
        "../rust_scraper/Scraper_4/Scraper_4_output.json", "r"
    ) as Scraper_4_input_json_file:
        contributor_metadata = json.load(Scraper_4_input_json_file)

    contributor_metadata.append(
        {
            "year": date,
            "contributor_github_url": contributor_github_url,
            "contributions": contributions,
            "code_review": code_review,
            "issues": issues,
            "pull_requests": pull_requests,
            "commits": commits,
        }
    )

    with open(
        "../rust_scraper/Scraper_4/Scraper_4_output.json", "w"
    ) as Scraper_4_output_json_file:
        json.dump(
            contributor_metadata, Scraper_4_output_json_file, indent=4, sort_keys=True
        )


# import contributor github url list
with open("../rust_scraper/contributor_github_url.csv", "r") as github_url_csv:
    contributor_github_url_data_list = csv.DictReader(github_url_csv)

    # loop through contributor github url list
    for index_contributor_github_url_data, contributor_github_url_data in enumerate(
        contributor_github_url_data_list
    ):
        contributor_github_url = contributor_github_url_data["contributor_github_url"]

        try:
            driver.get(contributor_github_url)

            # get latest year data
            date = "2023"

            yearly_metadata(date)

            # get all other years data
            year_list_len = WebDriverWait(driver, 5).until(
                expected_conditions.presence_of_all_elements_located(
                    (By.XPATH, r"//*[@class='filter-list small']/li")
                )
            )

            for year in range(1, len(year_list_len)):
                time.sleep(2)

                year_list = WebDriverWait(driver, 5).until(
                    expected_conditions.presence_of_all_elements_located(
                        (By.XPATH, r"//*[@class='filter-list small']/li")
                    )
                )

                year_element = year_list[year]
                date = year_element.text

                ActionChains(driver).move_to_element(year_element).click().perform()

                time.sleep(5)

                # driver.execute_script("arguments[0].scrollIntoView(true);", year_element)

                # driver.execute_script('arguments[0].click();', year_element)

                # ActionChains(driver).move_to_element(year_element).perform()

                # year_element.click()

                yearly_metadata(date)

        except Exception as e:
            # append the error json file
            with open(
                "../rust_scraper/Scraper_4/error_list.json", "r"
            ) as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append(
                {
                    "failed_requests": contributor_github_url,
                    "Index": str(index_contributor_github_url_data),
                    "Error": str(e),
                }
            )

            with open(
                "../rust_scraper/Scraper_4/error_list.json", "w"
            ) as error_list_output_json_file:
                json.dump(
                    error_list, error_list_output_json_file, indent=4, sort_keys=True
                )

            time.sleep(10)

            continue
