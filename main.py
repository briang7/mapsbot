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

daily_limit=random.uniform(500, 700);

def browserOptions():
    options = Options()
    firefoxProfileRootDir = r"C:\\Users\\brian\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\q0k65x9e.default-release"
    headless = False
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

stateTimeZones = { 'AL': 'GMT-06:00 US/Central (CST)' , 'AZ': 'BMT-07:00 US/Mountain (MST)' , 'AR': 'GMT-06:00 US/Central (CST)' , 'CA': 'GMT-08:00 America/Los_Angeles (PST)' , 'CO': 'BMT-07:00 US/Mountain (MST)' , 'CT': 'GMT-05:00 America/New_York (EST)' , 'DE': 'GMT-05:00 America/New_York (EST)' , 'FL': 'GMT-05:00 America/New_York (EST)' , 'GA': 'GMT-05:00 America/New_York (EST)' , 'ID': 'BMT-07:00 US/Mountain (MST)' , 'IL': 'GMT-06:00 US/Central (CST)' , 'IN': 'GMT-05:00 America/New_York (EST)' , 'IA': 'GMT-06:00 US/Central (CST)' , 'KS': 'GMT-06:00 US/Central (CST)' , 'KY': 'GMT-05:00 America/New_York (EST)' , 'LA': 'GMT-06:00 US/Central (CST)' , 'ME': 'GMT-05:00 America/New_York (EST)' , 'MD': 'GMT-05:00 America/New_York (EST)' , 'MA': 'GMT-05:00 America/New_York (EST)' , 'MI': 'GMT-05:00 America/New_York (EST)' , 'MN': 'GMT-06:00 US/Central (CST)' , 'MS': 'GMT-06:00 US/Central (CST)' , 'MO': 'GMT-06:00 US/Central (CST)' , 'MT': 'BMT-07:00 US/Mountain (MST)' , 'NE': 'GMT-06:00 US/Central (CST)' , 'NV': 'GMT-08:00 America/Los_Angeles (PST)' , 'NH': 'GMT-05:00 America/New_York (EST)' , 'NJ': 'GMT-05:00 America/New_York (EST)' , 'NM': 'BMT-07:00 US/Mountain (MST)' , 'NY': 'GMT-05:00 America/New_York (EST)' , 'NC': 'GMT-05:00 America/New_York (EST)' , 'ND': 'GMT-06:00 US/Central (CST)' , 'OH': 'GMT-05:00 America/New_York (EST)' , 'OK': 'GMT-06:00 US/Central (CST)' , 'OR': 'GMT-08:00 America/Los_Angeles (PST)' , 'PA': 'GMT-05:00 America/New_York (EST)' , 'RI': 'GMT-05:00 America/New_York (EST)' , 'SC': 'GMT-05:00 America/New_York (EST)' , 'SD': 'GMT-06:00 US/Central (CST)' , 'TN': 'GMT-06:00 US/Central (CST)' , 'TX': 'GMT-06:00 US/Central (CST)' , 'UT': 'BMT-07:00 US/Mountain (MST)' , 'VT': 'GMT-05:00 America/New_York (EST)' , 'VA': 'GMT-05:00 America/New_York (EST)' , 'WA': 'GMT-08:00 America/Los_Angeles (PST)' , 'WV': 'GMT-05:00 America/New_York (EST)' , 'WI': 'GMT-06:00 US/Central (CST)' ,'WY': 'BMT-07:00 US/Mountain (MST)' }


class GoogleMapsScraper:
    def __init__(self):
        self.driver = webdriver.Firefox(options=browserOptions(),service=Service(executable_path=GeckoDriverManager().install()))
        # self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        self.existing_businesses = []
        self.cities = self.get_cities()

    def get_cities(self, filename='cities.csv'):
        """Load existing businesses from CSV file"""
        cities = []
        with open('cities.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            cities = list(reader)
            cities.reverse()
        return cities

    def load_existing_businesses(self, filename='business_data.csv'):
        """Load existing businesses from CSV file"""
        existing_businesses = set()
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Create a tuple of business data to use as a unique identifier
                    business_key = (row['company_name'], row['website'])
                    existing_businesses.add(business_key)
        return existing_businesses

    def is_business_exists(self, business_name, website):
        """Check if business already exists in our records"""
        return (business_name, website) in self.existing_businesses

    def search_places(self, search_query, location):
        self.driver.get("https://www.google.com/maps")
        
        time.sleep(random.uniform(1, 3))
        search_box = self.wait.until(EC.presence_of_element_located(
            (By.ID, "searchboxinput")))
        search_box.clear()
        search_box.send_keys(f"{location}")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(random.uniform(3,5))
        
        search_box.clear()
        search_box.send_keys(f"{search_query}")
        search_box.send_keys(Keys.RETURN)
        
        time.sleep(random.uniform(1,3))

        # try:
        #     self.wait.until(lambda driver: 
        #         len(driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')) > 0 or
        #         len(driver.find_elements(By.CSS_SELECTOR, '.section-no-result-title')) > 0
        #     )
        # except TimeoutException:
        #     print("Warning: Timeout waiting for results to load")
            

    def get_quick_business_info(self, business_element):
        """Get basic business info without clicking"""
        
        business_data = {
            'company_name': '',
            'phone': '',
            'website': '',
            'rating': '',
            'review_count': 0,
            'ranking': ''
        }
        try:
            # Try different selectors for business name
            for selector in ['h1.fontHeadlineLarge', '.fontHeadlineSmall', 'h3', '.section-result-title']:
                try:
                    company_name = business_element.find_element(By.CSS_SELECTOR, selector).text
                    if company_name:
                        business_data['company_name'] = company_name
                        break
                except:
                    continue

        except Exception as e:
            print(f"Error in get_quick_business_info: {str(e)}")

        rating_selectors = [
            'span.MW4etd',  # New primary selector based on the HTML
            '.e4rVHe span[role="img"] .MW4etd',
            'span[role="img"] .MW4etd',
            'div.F7nice span[aria-hidden="true"]',
            '.F7nice span:first-child',
            'div[jslog*="76333"] span[aria-hidden="true"]'
        ]

        for selector in rating_selectors:
            try:
                rating_element = business_element.find_element(By.CSS_SELECTOR, selector)
                if rating_element:
                    rating_text = rating_element.get_attribute('textContent') or rating_element.text
                    if rating_text:
                        business_data['rating'] = rating_text.strip()
                        break
            except:
                continue

        # Get review count
        review_selectors = [
            'span.ZkP5Je span.UY7F9',  # New primary selector based on the HTML
            'span[role="img"][aria-label*="Reviews"] .UY7F9',
            'span[role="img"][aria-label*="stars"] .UY7F9',
            'span.e4rVHe span.UY7F9',
            'span[aria-label*="reviews"]',
            '.F7nice span span span'
        ]

        for selector in review_selectors:
            try:
                review_element = business_element.find_element(By.CSS_SELECTOR, selector)
                if review_element:
                    # Extract just the number from the text (e.g., "(68)" -> "68")
                    review_text = review_element.text.strip('()')  # Remove parentheses
                    review_count = re.search(r'\d+', review_text)
                    if review_count:
                        count = review_count.group().replace(',', '')
                        business_data['review_count'] = int(count.group())
                    break
            except:
                continue

        # Get website
        website_selectors = [
            'a.lcr4fd[aria-label*="website"]',  # New primary selector based on the HTML
            'div.etWJQ a[aria-label*="website"]',
            'a[jslog*="track:click"][href*="http"]',
            'a[data-item-id="authority"]',
            'a[aria-label*="Website"]',
            '.CsEnBe[aria-label*="Website"] a',
            'a[href*="www."]'
        ]

        for selector in website_selectors:
            try:
                website_element = business_element.find_element(By.CSS_SELECTOR, selector)
                href = website_element.get_attribute('href')
                if website_element and 'facebook' not in href and 'linkedin' not in href and 'godaddy' not in href and 'google' not in href:
                    business_data['website'] = href
                    break
            except:
                continue

        # Get phone number
        phone_selectors = [
            'span.UsdlK',  # New primary selector based on the HTML
            '.W4Efsd .UsdlK',
            'button[data-item-id^="phone"] .fontBodyMedium',
            'button[aria-label*="Phone:"] .fontBodyMedium',
            '.CsEnBe[aria-label*="Phone"] .Io6YTe',
            'div[data-item-id*="phone"] .Io6YTe'
        ]

        for selector in phone_selectors:
            try:
                phone_element = business_element.find_element(By.CSS_SELECTOR, selector)
                if phone_element:
                    # Remove any parentheses and clean up the phone number
                    phone_text = phone_element.text.strip()
                    # Remove any non-digit characters except + and -
                    phone_clean = ''.join(char for char in phone_text if char.isdigit() or char in '+')
                    business_data['phone'] = phone_clean
                    break
            except:
                continue

        return business_data

    def get_business_info(self, industry, city, state):
        businesses = []
        processed_count1 = 0
        skipped_count = 0
        
        try:
            # Wait for results to be visible
            time.sleep(random.uniform(4,6))
            
            # Try different selectors for the results container
            results_container = None
            selectors = [
               'div[role="feed"]',
               'div[aria-label="Results for"]',
               'div.section-layout.section-scrollbox',
               'div.section-layout',
               'div.m6QErb.DxyBCb.kA9KIf.dS8AEf', # New selector
               'div[class*="section-layout"]' # Partial class match
            ]

            for selector in selectors:
               try:
                   results_container = self.driver.find_element(By.CSS_SELECTOR, selector)
                   if results_container:
                       print(f"Found results container using selector: {selector}")
                       break
               except:
                   continue

            if not results_container:
                print("Could not find results container")
                return businesses

            business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')

            # First check if the quick view has only images (indicating need to click through)
            image_selectors = [
                '.SpFAAb img[src*="googleusercontent"]',
                '.FQ2IWe img[src*="googleusercontent"]',
                '.xwpmRb.qisNDe img',
                '.SpFAAb .FQ2IWe img'
            ]

            needs_click_through = False

            # Check if the image elements exist and if there's no direct website link
            print(business_elements[3])
            for img_selector in image_selectors:
                try:
                    print(img_selector)
                    images = business_elements[3].find_elements(By.CSS_SELECTOR, img_selector)
                    print(images)
                    if len(images) > 0:
                        needs_click_through = True
                        break
                except:
                    continue

            # if not needs_click_through:
            #     return businesses


            # Scroll through results
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", results_container)
            while True:
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", results_container)
                time.sleep(random.uniform(3,5))
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", results_container)
                if new_height == last_height:
                    break
                last_height = new_height
            # Try to find business listings after each scroll
            business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK')
            if not business_elements:
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            if not business_elements:
                business_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a[href^="https://www.google.com/maps/place"]')
            

            # # Get all business listings
            # business_lists = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="article"]')
            if not business_elements:
                print("No business listings found")
                return businesses
            


            for x,business in enumerate(reversed(business_elements)):
                print((len(business_elements)) - x, ' of ' , len(business_elements))
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", business)
                    business_data = self.get_quick_business_info(business)
                    business_data['ranking'] = (len(business_elements)) - x
                    # print(business_data)
                    name = business_data["company_name"] 

                    if self.is_business_exists(name,business_data['website']):
                        print(f"Skipping existing business: {name,business_data['website']}")
                        skipped_count += 1
                        continue

                    # if business_data['website'] != '':

                    #     print(f"Skipping business bc of website : {business_data}")
                    #     time.sleep(random.uniform(.25,.75))
                    #     continue
                    

                    # if int(business_data["review_count"]) > 100:
                    #     print(f"Skipping business bc of review_count: {business_data}")
                    #     time.sleep(random.uniform(.25,.75))
                    #     continue

                    skip_names = ['']
                    if not name or any(skip_name.lower() in name for skip_name in skip_names):  # Skip if we couldn't get the business name
                        print(f"Skipping business bc of name : {business_data}")
                        continue


                        
                    # add industry, city, state, and timezone
                    business_data['city'] = city
                    business_data['state'] = state
                    business_data['industry'] = industry
                    business_data['timezone'] = stateTimeZones[state]

                    if business_data["phone"] !='' and not needs_click_through:
                        
                        businesses.append(business_data)

                        processed_count1 += 1
                        
                        # Add to existing businesses set
                        self.existing_businesses.add(
                            (business_data['company_name'])
                        )
                        
                        print(f"Processed business: {business_data['company_name']}, {business_data['phone']}, {business_data['website']}, {business_data['rating']}, {business_data['review_count']}, {business_data['ranking']}, {business_data['state']}, {business_data['timezone']}")
                        time.sleep(random.uniform(.5,1.5))
                        continue
                    
                    print('clicking')
                    time.sleep(random.uniform(.5,1))
                    # Click only if business is new
                    business.click()
                    time.sleep(random.uniform(2,3))
                    

                    try:
                        # Try multiple selectors for phone number
                        phone_selectors = [
                            'button[data-item-id^="phone"] .fontBodyMedium',
                            'button[aria-label*="Phone:"] .fontBodyMedium',
                            '.CsEnBe[aria-label*="Phone"] .Io6YTe',
                            'div[data-item-id*="phone"] .Io6YTe'
                        ]
                        
                        # Get phone number
                        for selector in phone_selectors:
                            try:
                                phone_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if phone_element:
                                    business_data['phone'] = phone_element.text
                                    break
                            except:
                                continue

                        # Try multiple selectors for website
                        # website_selectors = [
                        #     'a[data-item-id="authority"] .Io6YTe',
                        #     'a[aria-label*="Website"] .fontBodyMedium',
                        #     '.CsEnBe[aria-label*="Website"] .Io6YTe',
                        #     'a[href*="www."] .Io6YTe'
                        # ]
                        website_selectors = [
                            'a.CsEnBe[aria-label*="Website"]',
                            'a[href*="http"].CsEnBe',
                            'a[aria-label*="Website"]',
                            '.RcCsl a.CsEnBe'
                        ]
                        # Get website
                        for selector in website_selectors:
                            try:
                                website_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                href = website_element.get_attribute('href')
                                if website_element and 'facebook' not in href and 'linkedin' not in href and 'godaddy' not in href and 'google.com' not in href:
                                    business_data['website'] = href
                                    break
                            except:
                                continue                      
                        
                        
                        # Get rating (5.0)
                        rating_selectors = [
                            'div.F7nice span[aria-hidden="true"]',
                            '.F7nice span:first-child',
                            'div[jslog*="76333"] span[aria-hidden="true"]'
                        ]
                        
                        for selector in rating_selectors:
                            try:
                                rating_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if rating_element:
                                    business_data['rating'] = rating_element.text
                                    break
                            except:
                                continue

                        

                        # Get review count (34)
                        review_selectors = [
                            'span[aria-label*="reviews"]',
                            '.F7nice span span span',
                            'div[jslog*="76333"] span[aria-label*="reviews"]'
                        ]
                        
                        for selector in review_selectors:
                            try:
                                review_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                if review_element:
                                    # Extract just the number from the text (e.g., "(34)" -> "34")
                                    review_count = re.search(r'\d+', review_element.text)
                                    if review_count:
                                        count = review_count.group().replace(',', '')
                                        business_data['review_count'] = int(count.group())
                                    break
                            except:
                                continue


                        if business_data['website'] != '':
                            print(f"Skipping business bc of website : {business_data}")
                            time.sleep(random.uniform(.25,.75))
                            continue

                        if business_data["phone"] !='':
                            businesses.append(business_data)
                            processed_count1 += 1
                            
                            # Add to existing businesses set
                            self.existing_businesses.add(
                                (business_data['company_name'])
                            )
                            
                            print(f"Processed business: {business_data['company_name']}, {business_data['phone']}, {business_data['website']}, {business_data['rating']}, {business_data['review_count']}, {business_data['ranking']}")
                    
                    except Exception as e:
                        print(f"Error processing individual business 1* : {str(e)}")
                        time.sleep(random.uniform(3,5))
                        continue

                except Exception as e:
                    print(f"Error processing individual business: {str(e)}")
                    time.sleep(random.uniform(3,5))
                    continue

            print(f"\nProcessing Summary:")
            print(f"New businesses processed: {processed_count1}")
            print(f"Existing businesses skipped: {skipped_count}")
            return businesses

        except Exception as e:
            print(f"Error in get_business_info: {str(e)}")
            return businesses

    def save_to_csv(self, businesses, filename='business_data.csv'):
        # If file exists, append new data
        mode = 'a' if os.path.exists(filename) else 'w'
        write_header = not os.path.exists(filename)
        
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'phone', 'website', 'rating', 'review_count', 'ranking', 'city', 'state', 'timezone', 'industry'])
            if write_header:
                writer.writeheader()
            writer.writerows(businesses)
    
    def save_to_csv1(self, businesses, filename='business_data1.csv'):
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['company_name', 'phone', 'website', 'rating', 'review_count', 'ranking', 'city', 'state', 'timezone', 'industry'])
            writer.writeheader()
            writer.writerows(businesses)

    def close(self):
        self.driver.quit()

def save_progress(industry, city, filename='progress.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['current_industry', 'current_city'])
        writer.writeheader()
        writer.writerow({'current_industry': industry, 'current_city': city})

def load_progress(filename='progress.csv'):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            row = next(reader, None)
            if row:
                return row['current_industry'], row['current_city']
    return None, None

def main():
    # daily_limit=random.uniform(100, 101);

    scraper = GoogleMapsScraper()
    print(scraper.cities)

    industries = ["Car detailing", "Tire service", "Car repair shop", "Auto body shop", 
                "Alternative medicine", "Therapist", "Veterinarian","Dentist", "Chiropractor", 
                 "Physical therapy", "Optometrist", "Hair salon", "Nail salon", "Massage therapist", 
                 "Esthetician", "Tattoo artist", "Tanning salon", "Waxing service", "Lawyer", 
                 "Accountant", "Financial advisor", "Insurance agent", "Career counselor", 
                 "Marriage counselor", "Business consultant", 
                 "Plumber", "Electrician", "HVAC technician", "Moving company",
                 "Pest control", "House cleaner", "Landscaper", "Interior designer", "Home inspector", 
                 "Pet groomers", "Pet trainers", "Pet boarding", "Computer repair", 
                 "Wedding officiant", "Wedding planner", "Party planner", "Caterer", "DJ or Musician", 
                 ]
    
    processed_count = 0
    start_industry, start_city = load_progress()
    
    # Find starting points in the lists
    industry_index = industries.index(start_industry) if start_industry in industries else 0
    city_index = next((index for (index, d) in enumerate(scraper.cities) if d["city"] == start_city), 0) if start_city else 0
    
    try:
        # Start from the saved industry
        for industry in industries[industry_index:]:  # Added : to slice the list
        # for industry in industries[industry_index:]:  # Added : to slice the list
            businesses1 = []  # Reset businesses list for each industry
            scraper.existing_businesses = scraper.load_existing_businesses(f'business_data{industry}.csv')

            # Start from the saved city for this industry
            # for city_dict in scraper.cities:  # Added : to slice the list
            for city_dict in scraper.cities[city_index:]:  # Added : to slice the list
                city_string = f"{city_dict['city']}, {city_dict['state']}"
                print(f"Searching for {industry} in {city_string}")
                
                # Check if we've hit the daily limit
                # if processed_count >= 3:
                if processed_count >= daily_limit:
                    print(f"Daily limit of {daily_limit} reached. Saving progress...")
                    save_progress(industry, city_dict['city'])
                    return  # Exit the script
                    # processed_count=0
                    # break
                scraper.search_places(industry, city_string)
                new_businesses = scraper.get_business_info(industry, city_dict['city'], city_dict['state'])
                processed_count += len(new_businesses)
                # processed_count += 1
                businesses1.extend(new_businesses)
                
                # Save progress after each city
                save_progress(industry, city_dict['city'])
                
                # if len(businesses1) <1:
                #     time.sleep(random.uniform(3,5))
                #     continue

                # Save current results
                if businesses1:
                    scraper.save_to_csv(new_businesses, f'business_data{industry}.csv')
                    scraper.save_to_csv1(businesses1, f'business_data1{industry}.csv')
            
            # Reset city_index when moving to a new industry
            city_index = 0
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        save_progress(industry, city_dict['city'])
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()

