from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import re
import os
import time,math,random,os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager import firefox

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

def browserOptions():
    options = Options()
    firefoxProfileRootDir = r"C:\\Users\\brian\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\q0k65x9e.default-release"
    headless = True
    # firefoxProfileRootDir = config.firefoxProfileRootDir
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    if(headless):
        options.add_argument("--headless")

    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("-profile")
    options.add_argument(firefoxProfileRootDir)
    # Set up Firefox options
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    # options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return options

bad_email_strings = ['facebook','linkedin','email.com','ueni','info@mysite','help@gosite','john@doe.com','john.doe','jane.doe','@sentry-next.wixpress.com','domain','.png','.jpg','example','CustomersForLife','noreply','no-reply','donotreply','do-not-reply','webmaster','postmaster','marketing@','styleseat','wix','wordpress','sentry']

class WebScraper:
    def __init__(self):
        self.driver = webdriver.Firefox(options=browserOptions(),service=Service(executable_path=GeckoDriverManager().install()))
        # self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.error = 0

    def find_email_on_page(self, page_source):
        """Extract email addresses from page source using regex"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, page_source)
        return list(set(emails))  # Remove duplicates

    def is_valid_email(self, email, bad_email_strings):
        """Check if email is valid and not in bad email list"""
        email = email.lower()  # Convert to lowercase for comparison
        return not any(bad_string.lower() in email for bad_string in bad_email_strings)

    def click_contact_link(self):
        """Try to find and click contact link"""
        contact_keywords = ['contact', 'Contact', 'CONTACT', 'contact us', 'Contact Us', 'CONTACT US']
        
        for keyword in contact_keywords:
            try:
                # Try finding link by href containing 'contact'
                contact_link = self.driver.find_element(By.CSS_SELECTOR, f'a[href*="{keyword.lower()}"]')
                contact_url = contact_link.get_attribute('href')
                self.driver.get(contact_url)
                time.sleep(random.uniform(2, 4))
                return True
            except NoSuchElementException:
                continue
            
            try:
                # Try finding link by text
                contact_link = self.driver.find_element(By.PARTIAL_LINK_TEXT, keyword)
                time.sleep(random.uniform(1, 2))
                contact_link.click()
                time.sleep(random.uniform(2, 4))
                return True
            except NoSuchElementException:
                continue
                
        
        return False

    def search_sites(self, businesses):
        """Search websites for email addresses"""
        results = []
        emails = []
        for i, business in enumerate(businesses):
            if not business.get('website') or (business.get('email') and (business['email']=='email' or '@' in business['email'])):
                continue
                
            try:
                # Navigate to website
                self.driver.get(business['website'])
                time.sleep(random.uniform(2, 4))
                
                #try contact page
                if self.click_contact_link():
                    emails = self.find_email_on_page(self.driver.page_source)
                
                # If no email found
                if not emails:
                    # Search for email on main page
                    emails = self.find_email_on_page(self.driver.page_source)
                    
                clean_website = business['website'].replace('https://', '').replace('http://', '').replace('www.', '') if business['website'] else ''
                clean_website = (clean_website.split('.'))[0]

                print(clean_website)
                print(emails)
                # Add email to business data
                valid_emails = [email for email in emails if self.is_valid_email(email, bad_email_strings)]
                print(valid_emails)

                business['email'] = next((email for email in valid_emails if clean_website in email), valid_emails[0] if valid_emails else 'email')
                print(business['company_name'] + ' - email: '+business['email'])
                businesses[i] = business
                
            except Exception as e:
                print(f"Error processing {business['company_name']}: {str(e)}")
                business['email'] = 'email'
                businesses[i] = business
                self.error +=1
                if self.error > 5:
                    break
                
            # Random delay between requests
            time.sleep(random.uniform(1, 3))
        
        return businesses

def main():
    scraper = WebScraper()
    try:
        # Read businesses from CSV file
        businesses = []
        with open('business_data1.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            businesses = list(reader)
        
        # Process websites and find emails
        results = scraper.search_sites(businesses)
        
        # Save results to new CSV
        with open('business_data1.csv', 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['company_name', 'phone', 'website', 'rating', 'review_count', 'ranking', 'email']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    finally:
        os.system("taskkill /f /im firefox.exe")

if __name__ == "__main__":
    main()