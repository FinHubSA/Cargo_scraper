import csv
import pandas as pd
import time
import json
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote import remote_connection

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.119 Safari/537.36"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument(f"user-agent={USER_AGENT}")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_experimental_option(
    "prefs",
    {
        # Set default directory for downloads.
        # It doesn't matter here because the download happens in the remote machines file system
        # "download.default_directory": os.path.join(directory, 'data'),
        # Auto download files
        "download.prompt_for_download": False,
        # "download.directory_upgrade": True,
        # It will not show PDF directly in chrome
        "plugins.always_open_pdf_externally": True,
        # gets rid of password saver popup
        "credentials_enable_service": False,
        # gets rid of password saver popup
        "profile.password_manager_enabled": False,
    },
)

selenium_connection = remote_connection.RemoteConnection(
    "http://localhost:4444/wd/hub"
)

driver = webdriver.Remote(
    selenium_connection,
    options=chrome_options,
)

count = 0

# load csv list
with open("../names_projects_Cargo.csv") as csv_file:
    project_list = csv.DictReader(csv_file)
    
    #print("loading projects")
    for index_project, project in enumerate(project_list):
        
        if count == 500:
            count = 0
            driver.close()
            driver = webdriver.Remote(
                selenium_connection,
                options=chrome_options,
            )

        try:
            project_name = project['project']

            # try:

            project_url = "https://libraries.io/cargo/" + str(project['project'])

            driver.get(project_url)

            # Check for too many requests error
            time.sleep(1)

            error_429 = driver.find_element(By.XPATH,r"//*").text

            if error_429 == '429 Too Many Requests':
                time.sleep(15)
                driver.get(project_url)

            time.sleep(10)

            Latest_release = None
            First_release = None
            Stars = None
            Forks = None
            Watch = None
            Contributors = None
            Repository_size = None
            crates_url = None
            github_repo = None

            # get the project links
            project_el_list = driver.find_elements(By.XPATH,r"//*[@class='project-links']/span/a")
            for project_el in project_el_list:
                #print("getting project links")                    
                project_link_name = project_el.text
                if project_link_name == 'Cargo':
                    crates_url = project_el.get_attribute('href')
                elif project_link_name == 'Repository':
                    github_repo = project_el.get_attribute('href')
                else:
                    continue
            
            # get the metadata
            element_tag_name_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/dl[@class='row']/dt")]
            element_tag_value_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/dl[@class='row']/dd")]
	
            #print("getting metadata")
            for index, element_tag_name in enumerate(element_tag_name_list):
		
                if element_tag_name == 'Latest release':
                    Latest_release = element_tag_value_list[index]
                elif element_tag_name == 'First release':
                    First_release = element_tag_value_list[index]
                elif element_tag_name == 'Stars':
                    Stars = element_tag_value_list[index]
                elif element_tag_name == 'Forks':
                    Forks = element_tag_value_list[index]
                elif element_tag_name == 'Watchers':
                    Watch = element_tag_value_list[index]
                elif element_tag_name == 'Contributors':
                    Contributors = element_tag_value_list[index]
                elif element_tag_name == 'Repository size':
                    Repository_size = element_tag_value_list[index]
                else:
                    continue
            
            #print("appending metadata")
            with open("metadata.json", "r") as metadata_input_json_file:
                metadata_list = json.load(metadata_input_json_file)
            
            metadata_list.append({'project': project_name, 'Latest_release': Latest_release, 'First_release': First_release, 'Stars': Stars, 'Forks': Forks, 'Watch': Watch, 'Contributors': Contributors, 'crates_url': crates_url, 'github_repo': github_repo})

            with open("metadata.json", "w") as metadata_output_json_file:
                json.dump(metadata_list, metadata_output_json_file, indent=4, sort_keys=True)

            #print("after appending metadata")

        except Exception as e:
            time.sleep(60)

            with open("error_list.json", "r") as error_list_input_json_file:
                error_list = json.load(error_list_input_json_file)

            error_list.append({'failed_requests':project, 'Index': str(index_project), 'Error': str(e)})
            
            with open("error_list.json", "w") as error_list_output_json_file:
                json.dump(error_list, error_list_output_json_file, indent=4, sort_keys=True)

            continue



        
        

