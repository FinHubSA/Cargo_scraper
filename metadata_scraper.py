import csv
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# from vpn import *

# # set up and start vpn service (get too many requests error need to rotate if get blocked)
# directory = os.path.dirname(__file__)
# expressvpn(directory, "South Africa")

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

# load csv list
with open("names_projects_Cargo.csv") as csv_file:
    project_list = csv.DictReader(csv_file)

    element_list = []

    for project in project_list:

        project_url = "https://libraries.io/cargo/" + str(project['project'])

        driver.get(project_url)

        Latest_release = None
        First_release = None
        Stars = None
        Forks = None
        Watch = None
        Contributors = None
        Repository_size = None
        crates_url = None
        github_repo = None

        # project_links_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='project-links']/span/a")]
        project_el_list = driver.find_elements(By.XPATH,r"//*[@class='project-links']/span/a")
        for project_el in project_el_list:
                       
            project_link_name = project_el.text
            if project_link_name == 'Cargo':
                crates_url = project_el.get_attribute('href')
            elif project_link_name == 'Repository':
                github_repo = project_el.get_attribute('href')
            else:
                continue


        element_tag_name_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/dl[@class='row']/dt")]
        element_tag_value_list = [el.text for el in driver.find_elements(By.XPATH,r"//*[@class='col-md-4 sidebar']/dl[@class='row']/dd")]

        for index, element_tag_name in enumerate(element_tag_name_list):

            if element_tag_name == 'Latest release':
                Latest_release = element_tag_value_list[index]
            elif element_tag_name == 'First release':
                First_release = element_tag_value_list[index]
            elif element_tag_name == 'Stars':
                Stars = element_tag_value_list[index]
            elif element_tag_name == 'Forks':
                Forks = element_tag_value_list[index]
            elif element_tag_name == 'Watch':
                Watch = element_tag_value_list[index]
            elif element_tag_name == 'Contributors':
                Contributors = element_tag_value_list[index]
            elif element_tag_name == 'Repository size':
                Repository_size = element_tag_value_list[index]
            else:
                continue

            
        element_list.append({'Latest_release': Latest_release, 'First_release': First_release, 'Stars': Stars, 'Forks': Forks, 'Watch': Watch, 'Contributors': Contributors, 'crates_url': crates_url, 'github_repo': github_repo})
    
    Reference_Data = pd.DataFrame.from_records(element_list)     
    Reference_Data.to_excel('project_metadata.xlsx')


