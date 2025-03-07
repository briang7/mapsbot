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
import time,math,random,os,json

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

from PIL import Image
import requests
from io import BytesIO
import colorsys
import pyperclip

from webvista_utils import callClaude, create_image, process_response, click_obscured_element, insert_image, make_image, is_image_visible, get_all_child_text,reduce_aspect_ratio

# daily_limit=random.uniform(300, 500);

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

location_options = {
    'name': 'Shine Labs',
    'id': 'RdCifZygzj5TBCPitzpG',
    'pageBuilderId': 'kDIxKWtIrz5vlNAZG8I2',
    'industry': 'Car detailing',
    'description':'the best, hardworking, average joe\'s',
    'services':'Paint Protection Film, Dent Removal, Window Tinting, Wheel Restoration, Headlight Restoration, Detailing Services, Ceramic Coating'
}

color_options = [{'old':'#FFD70C','new':'#1910F0','name':'#1910F0'}]


class webvistaScraper:
    def __init__(self):
        self.driver = webdriver.Firefox(options=browserOptions(),service=Service(executable_path=GeckoDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 30)
        self.text_data = {}

    def loadAIResponse(self):
        # Load JSON from a file
        with open('ai_response.json') as file:
            data = json.load(file)
        return data    

    def load_text_elements(self):
        # Load JSON from a file
        with open('text_elements.json') as file:
            data = json.load(file)
        return data    
    def load_text_elements1(self):
        # Load JSON from a file
        with open('text_elements1.json') as file:
            data = json.load(file)
        return data    

    def find_nearest_parent_id(self, element):
        """Recursively search up the DOM tree for the nearest parent with an ID"""
        try:
            current = element
            max_levels = 10  # Prevent infinite loops
            level = 0
            
            while level < max_levels:
                element_id = current.get_attribute("id")
                if element_id:
                    return element_id
                
                # Move up to parent
                current = current.find_element(By.XPATH, "./..")
                level += 1
                
            return None  # No ID found within max levels
        except:
            return None

    def extract_faq_content(self, previewer):
        """Specifically extract FAQ questions and answers"""
        faq_data = []

        faq_element = previewer.find_element(By.CSS_SELECTOR, "div.hl-faq")

        questions = self.driver.execute_script("""
            return Array.from(arguments[0].querySelectorAll('.hl-faq-child-heading-text'))
                .map(el => el.textContent.trim());
        """, faq_element)
        
        answers = self.driver.execute_script("""
            return Array.from(arguments[0].querySelectorAll('.hl-faq-child-item-text'))
                .map(el => el.textContent.trim());
        """, faq_element)
        
        for q, a in zip(questions, answers):
            faq_data.append({
                "element_type": 'faq',
                "question": q,
                "answer": a
            })
        
        return faq_data

    def get_text_elements(self, previewer):
        text_data = {}
        processed_elements = set()

        def get_direct_text(element):
            """Get text that belongs directly to this element, excluding child element text"""
            try:
                # # Get all child elements' text
                children_text = ''
                for child in element.find_elements(By.XPATH, "./*"):
                    children_text += ('\n'+ child.text.strip())
                
                # Get element's full text
                full_text = element.text.strip()
                
                # If element has more text than just its children's text combined
                if full_text and full_text != children_text:
                    return full_text
                return ''
            except:
                return ''

        def process_element(element, section_id):
            """Recursively process elements down to the deepest level"""
            try:
                # First, process all children
                children = element.find_elements(By.XPATH, "./*")
                for child in children:
                    child_element_id = child.get_attribute("id")
                    if child_element_id and 'section-' in child_element_id:
                        section_id = child_element_id

                    process_element(child, section_id)

                # Then check if this element has its own text
                direct_text = get_direct_text(element)
                if direct_text:

                    if 'faq' in direct_text or 'Frequently Asked Questions' in direct_text:
                        return

                    element_type = element.tag_name
                    nearest_parent_id = self.find_nearest_parent_id(element)

                    if any(skip_id.lower() in nearest_parent_id for skip_id in ['previewer','section-','row-','col-','faq-']):
                        return

                    # Create unique identifier for this element's text and location
                    element_id = f"{nearest_parent_id}"
                    
                    if section_id and element_id not in processed_elements:
                        processed_elements.add(element_id)

                        if section_id not in text_data:
                            text_data[section_id]=[]

                        exists = any(obj["current_text"] == direct_text for obj in text_data[section_id])

                        if not exists:
                            text_data[section_id].append({  
                                # "element_type": element_type,
                                "current_text": direct_text,
                                "nearest_parent_id": nearest_parent_id,
                            })

            except Exception as e:
                print(f"Error processing element: {str(e)}")

        # Start processing from the top
        process_element(previewer, None)
        
        # Sort by depth and parent ID for better organization
        # text_data.sort(key=lambda x: (x['depth'], x['nearest_parent_id']))
        
        faqs = self.extract_faq_content(previewer)
        if 'faqs' not in text_data:
            text_data['faqs']=[]
        for faq in faqs:
            text_data['faqs'].append(faq)
        
        return text_data

    def analyze_with_ai(self, text_data):
        # api call for prompt for new image, then make new image
        starting='```json'

        
        ree=f'<xml>'        
        location = location_options
        if 'pageBuilderId' in location:
            del location['pageBuilderId']
        if 'id' in location:
            del location['id']

        ree=ree+'<location>'
        for key in location:
            ree=ree+f'<{key}>{location[key]}</{key}>'
        ree=ree+'</location></xml>'
        print(ree)
        json_string = json.dumps(text_data)
        prompt="given this xml, and this json: \n "+json_string+" \n update the text for a website template about the location from the xml. \n I need every item in the array in the final returned array. All text that should be changed to be changed.  This is for a website template.  All of these elements are already on the page.  I need to update the words.  Make the words robust. For example, if the given text should be a paragraph, give a decent sized paragraph.  Do not leave any items from original json array out.  Do not ask me any questions.  Just provide the updated JSON array.  Make it as long as you need."
        # prompt=f'given this xml, ' Break up the full answer into 3 responses. You will respond with the first part of the json. Do not close the array.  Then I will reply \'continue\". Then you will reply with the second part of the json. Do not close the array. Then I will reply \'continue\". Then you will reply with the final part of the json with the array closed.  return answer in same json format as original json.     Remember break it up into 3 responses.
        text_json = callClaude(ree,prompt,starting)
        print(text_json)
        rere = text_json
        index = rere.find('```')
        
        new_text_json=rere    
        # If the string is found, keep everything up to it
        if index != -1:
            new_text_json = rere[:index]
        
        return new_text_json  # For now, just returning the prompt for demonstration

 


    def start(self, location):
        self.driver.get(f"https://app.webvista.io/location/{location_options['id']}/page-builder/{location_options['pageBuilderId']}")

        time.sleep(random.uniform(20, 31))
        try:
            # First try: Wait for any potential iframes to load
            # funnelBuilderApp = self.wait.until(EC.presence_of_element_located((By.ID, "funnelBuilderApp")))
            # self.driver.switch_to.frame(funnelBuilderApp)

            iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe)
            
            # Now look for previewer
            previewer = self.wait.until(EC.presence_of_element_located((By.ID, "previewer")))
        except:
            print("Could not find previewer element")
            raise
    
        if previewer:
            print('previewer found - getting text elements')
            # Get all text elements and their context
            text_data = self.get_text_elements(previewer)
            # ... rest of your code
            print('text data - ', text_data)
            
            # # Save raw text data to JSON
            with open('text_elements.json', 'w', encoding='utf-8') as f:
                json.dump(text_data, f, indent=4)

            # self.driver.switch_to.default_content()
            time.sleep(random.uniform(2, 3))

            mobile_button = self.driver.find_element(By.ID, "pg-funnel-builder__btn--mobile")
            mobile_button.click()
            time.sleep(random.uniform(2, 3))
            
            
            if previewer:
                print('previewer found - getting text elements')
                # Get all text elements and their context
                text_data1 = self.get_text_elements(previewer)
                # ... rest of your code
                print('text data - ', text_data)

                desktop_button = self.driver.find_element(By.ID, "pg-funnel-builder__btn--desktop")
                desktop_button.click()
                # # Save raw text data to JSON
                with open('text_elements1.json', 'w', encoding='utf-8') as f:
                    json.dump(text_data1, f, indent=4)
                try:
                    # need to combine them into a new dict
                    text_data2 = {}
                    for section_id in text_data:
                        text_data2[section_id] = text_data[section_id]
                        for section_id1 in text_data1:

                            desktop = text_data[section_id]
                            mobile = text_data1[section_id1]
                            
                            matches = 0
                            total_checked = len(desktop)

                            for index, obj in enumerate(desktop):
                                for index1, obj1 in enumerate(mobile):
                                    print(obj)
                                    print(obj1)
                                    if 'current_text' in obj and 'current_text' in obj1 and obj['current_text'] == obj1['current_text']:
                                        matches += 1

                            if matches >= total_checked / 2:
                                print("At least half of the current_texts match up.")
                                for index, obj in enumerate(desktop):
                                    for index1, obj1 in enumerate(mobile):
                                        print(obj)
                                        print(obj1)
                                        if 'current_text' in obj and 'current_text' in obj1 and obj['current_text'] == obj1['current_text']:
                                            text_data2[section_id][index]['mobile_nearest_parent_id'] = obj1['nearest_parent_id']
                            else:
                                print("Less than half of the current_texts match up.")

                except Exception as e:
                    print(f"Error making text_data2: {str(e)}")
                with open('text_elements2.json', 'w', encoding='utf-8') as f:
                    json.dump(text_data2, f, indent=4)


            
        # text_data = self.load_text_elements()
        # text_data1 = self.load_text_elements1()
        
        # # Save raw text data to JSON

        text_data3 = [[],[]]
        # # # # Break up into 2 AI calls with all elements
        for index, key in enumerate(text_data):
            if index <= (len(text_data)/2):
                text_data3[0].append(text_data[key])
            else:
                text_data3[1].append(text_data[key])

        for index,array in enumerate(text_data3):
            if index == 0:
                ai_response = self.analyze_with_ai(array)
            else:
                ai_response1 = self.analyze_with_ai(array)


        # # # Save the prompt for reference
        with open('ai_response.json', 'w', encoding='utf-8') as f:
            f.write(ai_response)
        # # # Save the prompt for reference
        with open('ai_response1.json', 'w', encoding='utf-8') as f:
            f.write(ai_response1)

        # need to combine
        # ###########################################################################################################
        # ###########################################################################################################
        # ###########################################################################################################
        # ###########################################################################################################


        try:
            ai_json = json.loads(ai_response)
            print('ai_response json loaded', ai_json)
        except:
            print('ai_response json not loaded', ai_response)
            ai_ = ai_response
        

    def close(self):
        self.driver.quit()


def main():

    scraper = webvistaScraper()
    try:
        scraper.start('Shine Labs')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()


 


