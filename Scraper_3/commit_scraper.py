import csv
import time
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import remote_connection

# Set User Agent and chrome option
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.119 Safari/537.36"
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

selenium_connection = remote_connection.RemoteConnection(
    "http://localhost:4444/wd/hub"
)

driver = webdriver.Remote(
    selenium_connection,
    options=chrome_options,
)

prev_contributors_url = None
prev_project = None

def scrape_project(project, index_project, depth):

    global driver, prev_contributors_url, prev_project, selenium_connection, chrome_options

    try:

        project_name = project['project']

        project_url = "https://libraries.io/cargo/" + str(project['project'])

        driver.get(project_url)

        # Check for too many requests error
        too_many_requests = True
        count_requests_error = 0

        while too_many_requests and count_requests_error <=10:

            error_429 = driver.find_element(By.XPATH,r"//*").text

            if error_429 == '429 Too Many Requests':
                count_requests_error += 1
                print(project_name)
                print(error_429)
                time.sleep(30)
                driver.get(project_url)
            else:
                too_many_requests = False

        time.sleep(10)

        contributor_el_list = [el for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/p/a")]

        has_contributors = False

        for contributor in contributor_el_list:

            if contributor.text == "See all contributors":

                contributors_url = contributor.get_attribute('href')

                has_contributors = True

            else:

                continue             

        if has_contributors:

            print(prev_contributors_url)
            print(contributors_url)

            #add logic here to see if prev contributors same
            if contributors_url == prev_contributors_url:
                with open("Scraper_3_output.json", "r") as commit_githuburl_input_json_file:
                    commit_github_url = json.load(commit_githuburl_input_json_file)

                    for commit_item in reversed(commit_github_url):
                        if commit_item['project'] == prev_project:

                            commit_github_url.append({'project': project_name, 'contributor_name': commit_item['contributor_name'], 'contributor_commits': commit_item['contributor_commits'], 'contributor_github_url': commit_item['contributor_github_url']})
                        
                        else:

                            break

                with open("Scraper_3_output.json", "w") as commit_githuburl_output_json_file:
                        json.dump(commit_github_url, commit_githuburl_output_json_file, indent=4, sort_keys=True)

                prev_contributors_url = contributors_url

            else:

                driver.get(contributors_url)

                # Check for too many requests error
                too_many_requests = True
                count_requests_error = 0

                while too_many_requests and count_requests_error <=10:

                    error_429 = driver.find_element(By.XPATH,r"//*").text

                    if error_429 == '429 Too Many Requests':
                        count_requests_error += 1
                        print(project_name)
                        print(error_429)
                        time.sleep(30)
                        driver.get(contributors_url)
                    else:
                        too_many_requests = False

                next_page = True

                while next_page:

                    time.sleep(4)

                    commit_data_list = driver.find_elements(By.XPATH,r"//*[@class='col-sm-8']/div")

                    # get contributor commits and github url
                    with open("Scraper_3_output.json", "r") as commit_githuburl_input_json_file:
                        commit_github_url = json.load(commit_githuburl_input_json_file)

                        for commit in commit_data_list:

                            contributor_name = commit.find_element(By.XPATH,r"./div/h4/a").text

                            contributor_commits = commit.find_element(By.XPATH,r"./div/p/small/a").text

                            contributor_github_url = commit.find_element(By.XPATH,r"./div/p/small/a").get_attribute('href')
                            contributor_github_url = contributor_github_url.split("=")[-1]
                            contributor_github_url = 'https://github.com/' + contributor_github_url

                            commit_github_url.append({'project': project_name, 'contributor_name': contributor_name, 'contributor_commits': contributor_commits, 'contributor_github_url': contributor_github_url})
                    
                    with open("Scraper_3_output.json", "w") as commit_githuburl_output_json_file:
                        json.dump(commit_github_url, commit_githuburl_output_json_file, indent=4, sort_keys=True)

                    try:
                    
                        next_page_button = driver.find_element(By.XPATH, r"//*[@class='next']/a").get_attribute('href')
                        driver.get(next_page_button)

                        next_page = True
                    
                    except:

                        next_page = False

                prev_contributors_url = contributors_url
            
        else:
            
            with open("Scraper_3_output.json", "r") as commit_githuburl_input_json_file:
                commit_github_url = json.load(commit_githuburl_input_json_file)

            commit_github_url.append({'project': project_name, 'contributor_name': None, 'contributor_commits': None, 'contributor_github_url': None})
            
            with open("Scraper_3_output.json", "w") as commit_githuburl_output_json_file:
                json.dump(commit_github_url, commit_githuburl_output_json_file, indent=4, sort_keys=True)
        
        prev_project = project_name

    except Exception as e:

        driver.quit()

        driver = webdriver.Remote(
            selenium_connection,
            options=chrome_options,
        )

        if depth > 3:
            with open("error_list.json", "r") as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append({'failed_requests':project, 'Index': str(index_project), 'Error': str(e)})
            
            with open("error_list.json", "w") as error_list_output_json_file:
                json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

            with open("unscraped_projects.csv", "a+") as unscraped_projects_file:
                unscraped_projects_file.write(project + "\n")
        else:
            depth += 1

            time.sleep(10)

            scrape_project(project, index_project, depth)

# load csv list
with open("../names_projects_Cargo.csv") as csv_file:
    project_list = csv.DictReader(csv_file)

    for index_project, project in enumerate(project_list):
        scrape_project(project, index_project, 1)
        