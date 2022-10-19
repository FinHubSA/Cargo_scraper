import pandas as pd
import time
import re
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from vpn import *

def loading_page():
    loading_time = 0
    loading_page = True

    # Check for all contributors and record contr. number, github url and commits
    while loading_page == True and loading_time <= 80:
        time.sleep(1)
        loading_time += 1
        loading = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,"//*[@class = 'js-date-range Subhead-heading']"))).text
        if not loading == 'Loading contributions…':
            loading_page = False
    
    return loading_time

# Start VPN Service (choose high performance service for initial scrape)
expressvpn("../rust_scraper", "South Africa")

# import maintain_github_url file
with open("../rust_scraper/Scraper_3/Scraper_2_output.json", "r") as Scraper_2_input_json_file:
    project_github_data_list = json.load(Scraper_2_input_json_file)

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

project_prev = None

for index_project_github_data, project_github_data in enumerate(project_github_data_list):

    no = None
    contributor_github_url = None
    contributor_github_commits = None

    project = project_github_data['project']
    project_github_url = project_github_data['github_url']

    try:

        # avoid duplicates and empty cells
        if project == project_prev:

            project_prev = project

            continue
        
        # record the entry even if there is no github url (use empty to scrape projects with no github url in scraper 4)
        elif pd.isnull(project_github_url):

            with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as Scraper_3_input_json_file:
                contributor_project_data = json.load(Scraper_3_input_json_file)

            contributor_project_data.append({'project': project, 'github_url': project_github_url, 'no': no,'contributor_github_url': contributor_github_url,'contributor_github_commits': contributor_github_commits})
    
            with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as Scraper_3_output_json_file:
                json.dump(contributor_project_data, Scraper_3_output_json_file, indent=4, sort_keys=True)
            
            project_prev = project

            continue

        # get project github url
        driver.get('https://' + project_github_url)

        time.sleep(5)

        try:
            # Check if page exists, if not, add blank rows (use empty to scrape projects with no github url in scraper 4)
            error_404 = driver.find_element(By.XPATH, r"//*[@Class='js-plaxify position-absolute']")

            with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as Scraper_3_input_json_file:
                contributor_project_data = json.load(Scraper_3_input_json_file)

            contributor_project_data.append({'project': project, 'github_url': None, 'no': no,'contributor_github_url': contributor_github_url,'contributor_github_commits': contributor_github_commits})
    
            with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as Scraper_3_output_json_file:
                json.dump(contributor_project_data, Scraper_3_output_json_file, indent=4, sort_keys=True)
            
            project_prev = project

        except:       

            heading_text_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@Class='h4 mb-3']/a")]
            heading_el_list = [el for el in driver.find_elements(By.XPATH, r"//*[@Class='h4 mb-3']/a")]

            is_contributors_page = False

            for index, heading in enumerate(heading_text_list):
                
                if re.findall('Contributors', heading):

                    is_contributors_page = True
                    heading_el_list[index].click()

                    time.sleep(2)

                    loading_time = loading_page()

                    # possible error: can't load graph, rotate vpn
                    if loading_time > 80:

                        try:

                            loading_time = loading_page()

                            # Connect to new server
                            expressvpn("../rust_scraper/chromedriver", vpn_list("../rust_scraper/chromedriver"))
                            rotated = "True"
                        
                        except:

                            with open("../rust_scraper/Scraper_3/error_list.json", "r") as error_list_input_json_file:
                                error_list = json.load(error_list_input_json_file)

                            error_list.append({'failed_requests': project, 'Index': str(index_project_github_data), 'Error': str(e)})
                            
                            with open("../rust_scraper/Scraper_3/error_list.json", "w") as error_list_output_json_file:
                                json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

                            time.sleep(30)

                            break
                    
                    time.sleep(2)

                    # get contributor number
                    contributor_github_no_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@class='f5 text-normal color-fg-muted float-right']")]

                    # get contributor github url
                    contributor_github_url_list = [el.get_attribute('href') for el in driver.find_elements(By.XPATH, r"//*[@class='d-inline-block mr-2 float-left']")]

                    #get contributor number of commmits
                    contributor_github_commits_list = [el.text for el in driver.find_elements(By.XPATH, r"//*[@class='cmeta']/div/a")]

                    for contributor_index in range(0,len(contributor_github_no_list)):

                        no = contributor_github_no_list[contributor_index]
                        contributor_github_url =  contributor_github_url_list[contributor_index]
                        contributor_github_commits =  contributor_github_commits_list[contributor_index]

                        with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as contributor_project_input_json_file:
                            contributor_project_data = json.load(contributor_project_input_json_file)

                        contributor_project_data.append({'project': project, 'github_url': project_github_url, 'no': no,'contributor_github_url': contributor_github_url,'contributor_github_commits': contributor_github_commits})
                
                        with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as Scraper_3_output_json_file:
                            json.dump(contributor_project_data, Scraper_3_output_json_file, indent=4, sort_keys=True)

            if not is_contributors_page:

                # There is only one contributor, record contr. number, github url and commits
                no = '#1'
                contributor_github_url = "https://" + project_github_url.split("/")[0] + "/" + project_github_url.split("/")[1]
                contributor_github_commits = driver.find_element(By.XPATH,r"//*[@class='d-none d-sm-inline']/strong").text

                with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "r") as Scraper_3_input_json_file:
                    contributor_project_data = json.load(Scraper_3_input_json_file)

                contributor_project_data.append({'project': project, 'github_url': project_github_url, 'no': no,'contributor_github_url': contributor_github_url,'contributor_github_commits': contributor_github_commits + ' commits'})
                
                with open("../rust_scraper/Scraper_3/Scraper_3_output.json", "w") as contributor_project_output_json_file:
                    json.dump(contributor_project_data, contributor_project_output_json_file, indent=4, sort_keys=True)

            # avoid duplicates
            project_prev = project
        
    except Exception as e:

        project_prev = project

        with open("../rust_scraper/Scraper_3/error_list.json", "r") as error_list_input_json_file:
            error_list = json.load(error_list_input_json_file)

        error_list.append({'failed_requests': project, 'Index': str(index_project_github_data), 'Error': str(e)})
        
        with open("../rust_scraper/Scraper_3/error_list.json", "w") as error_list_output_json_file:
            json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

        time.sleep(60)

        continue
            








