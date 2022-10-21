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
    "../rust_scraper/chromedriver",
    options=chrome_options,
)
count = 0

# load csv list
with open("../rust_scraper/names_projects_Cargo.csv") as csv_file:
    project_list = csv.DictReader(csv_file)

    for index_project, project in enumerate(project_list):

        try:

            project_name = project['project']

            project_url = "https://libraries.io/cargo/" + str(project['project'])

            driver.get(project_url)

            # Check for too many requests error
            error_429 = driver.find_element(By.XPATH,r"//*").text

            if error_429 == '429 Too Many Requests':
                time.sleep(20)
                driver.get(project_url)

            time.sleep(5)

            contributor_el_list = [el for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/p/a")]

            has_contributors = False

            for contributor in contributor_el_list:

                if contributor.text == "See all contributors":

                    contributors_url = contributor.get_attribute('href')

                    has_contributors = True

                else:

                    continue             

            if has_contributors:

                driver.get(contributors_url)

                # Check for too many requests error
                error_429 = driver.find_element(By.XPATH,r"//*").text

                if error_429 == '429 Too Many Requests':
                    time.sleep(20)
                    driver.get(contributors_url)

                next_page = True

                while next_page:

                    time.sleep(2)

                    commit_data_list = driver.find_elements(By.XPATH,r"//*[@class='col-sm-8']/div")

                    # get contributor commits and github url
                    for commit in commit_data_list:

                        contributor_name = commit.find_element(By.XPATH,r"./div/h4/a").text

                        contributor_commits = commit.find_element(By.XPATH,r"./div/p/small/a").text

                        contributor_github_url = commit.find_element(By.XPATH,r"./div/p/small/a").get_attribute('href')
                        contributor_github_url = contributor_github_url.split("=")[-1]
                        contributor_github_url = 'https://github.com/' + contributor_github_url

                        with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as commit_githuburl_input_json_file:
                            commit_github_url = json.load(commit_githuburl_input_json_file)

                        commit_github_url.append({'project': project_name, 'contributor_name': contributor_name, 'contributor_commits': contributor_commits, 'contributor_github_url': contributor_github_url})
                        
                        with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as commit_githuburl_output_json_file:
                            json.dump(commit_github_url, commit_githuburl_output_json_file, indent=4, sort_keys=True)

                    try:
                    
                        next_page_button = driver.find_element(By.XPATH, r"//*[@class='next']/a").get_attribute('href')
                        driver.get(next_page_button)

                        next_page = True
                    
                    except:

                        next_page = False
                
            else:
                
                with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as commit_githuburl_input_json_file:
                    commit_github_url = json.load(commit_githuburl_input_json_file)

                commit_github_url.append({'project': project_name, 'contributor_name': None, 'contributor_commits': None, 'contributor_github_url': None})
                
                with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as commit_githuburl_output_json_file:
                    json.dump(commit_github_url, commit_githuburl_output_json_file, indent=4, sort_keys=True)

        except Exception as e:

            with open("../rust_scraper/Scraper_3/error_list.json", "r") as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append({'failed_requests':project, 'Index': str(index_project), 'Error': str(e)})
            
            with open("../rust_scraper/Scraper_3/error_list.json", "w") as error_list_output_json_file:
                json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

            time.sleep(10)

            continue