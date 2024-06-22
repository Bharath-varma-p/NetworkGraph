from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the ChromeDriver executable
chrome_driver_path = '/Users/bharath/Downloads/chromedriver-mac-x64/chromedriver'

# Configure Chrome options to use remote debugging
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

# Function to get the correct tab with LinkedIn open
def get_linkedin_tab():
    try:
        response = requests.get('http://127.0.0.1:9222/json')
        response.raise_for_status()
        tabs = response.json()
        for tab in tabs:
            if "linkedin.com" in tab["url"]:
                return tab["webSocketDebuggerUrl"]
        logging.error("LinkedIn tab not found. Please ensure LinkedIn is open in the browser.")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Chrome DevTools: {e}")
        return None

# Get the LinkedIn tab WebSocket URL
linkedin_tab_ws_url = get_linkedin_tab()
if not linkedin_tab_ws_url:
    logging.error("LinkedIn tab not found or connection error. Please ensure LinkedIn is open in the browser and Chrome is started with remote debugging.")
    exit()

# Initialize the WebDriver with the specified options
service = Service(chrome_driver_path)

try:
    logging.info('Starting WebDriver')
    driver = webdriver.Chrome(service=service, options=options)

    # Define the URL of the LinkedIn profile
    profile_url = 'https://www.linkedin.com/in/thakurhimanshu111/'

    # Navigate to the LinkedIn profile
    logging.info('Navigating to LinkedIn profile')
    driver.get(profile_url)
    time.sleep(5)

    # Wait for the mutual connections link to be present and then click it
    logging.info('Waiting for mutual connections link')
    mutual_connections_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="profile-content"]/div/div[2]/div/div/main/section[1]/div[2]/a/span'))
    )
    mutual_connections_link.click()
    time.sleep(5)

    # Get the page source and parse it with BeautifulSoup
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all mutual connection links using BeautifulSoup
    logging.info('Finding all mutual connections using BeautifulSoup')
    mutual_connections = soup.select('ul > li > div > div > div > div:nth-of-type(2) > div:nth-of-type(1) > div:nth-of-type(1) > div > span:nth-of-type(1) > span > a')

    # List to hold mutual connections details
    mutual_connections_details = []

    for connection in mutual_connections:
        connection_url = connection['href']
        logging.info(f"Opening mutual connection: {connection_url}")
        driver.get(connection_url)
        time.sleep(5)
        
        # Get the new page source and parse it with BeautifulSoup again
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Extract the name of the connection
        logging.info('Extracting the name of the mutual connection')
        name = soup.select_one('h1.text-heading-xlarge.inline.t-24.v-align-middle.break-words')
        
        if name:
            mutual_connections_details.append(name.get_text().strip())
        else:
            logging.error('Name not found for this connection')
    
    # Print all mutual connections names
    for name in mutual_connections_details:
        print(f"Name: {name}")

    # Close the WebDriver
    logging.info('Closing WebDriver')
    driver.quit()

except Exception as e:
    logging.error(f"Error: {e}")
    if 'driver' in locals():
        driver.quit()
    exit()
