import os
# import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import anthropic
import subprocess
import json
import itertools
import random
import sys, requests,time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import colorsys


load_dotenv()
client = anthropic.Anthropic(
    api_key=os.getenv('ANTHROPIC_API_KEY'),
)

MIDKEY = os.getenv('MIDKEY')
MIDURL = os.getenv('MIDURL')


def callClaude(ree,prompt,starting):
    response = client.messages.create(
        # model="claude-3-sonnet-20240229",
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        temperature=0.8,
        messages=[
            {"role": "user", "content": ree+" \n\n "+prompt},
            {"role":"assistant", "content":starting}        
        ]
    )
    print("response")
    print(response)
    content = response.content[0].text
    print("\n content")
    print(content)
    messages = [
            {"role": "user", "content": ree+prompt},
            {"role":"assistant", "content":content}        
        ]
    x=0
    while response.stop_reason == 'max_tokens' and x<5:
        messages.append({"role":"user", "content":"continue"})
        print("\n messages")
        print(messages)
        response = client.messages.create(
            # model="claude-3-sonnet-20240229",
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            temperature=0.8,
            # system="Respond only in js or jsx code.",
            messages=messages
        )
        print(response)

        # handle non finished objects

        if content[-1] !='}' and response.content[0].text[0] == '{':
            last_index = my_string.rfind('}')
            if last_index != -1:
                content = content[:last_index]
                content+=','

        content+=response.content[0].text
        messages.append({"role":"assistant", "content":content})
        x+=1
    print("\n content")
    print(content)
    return content



def create_image(data):
    url = MIDURL
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {MIDKEY}',
    }

    config = {
        'method': 'post',
        'url': url,
        'headers': headers,
        'json': data,
    }

    print(config)

    response = requests.post(url, headers=headers, json=data)
    # Wait for the response and parse it
    if response.status_code == 200:
        response_data = response.json()
        return response_data
    else:
        print(f"Error: {response.status_code}")
        return None



def wait_to_finish(response):
    print('res  :  ', response)
    x = 0

    while response['data']['status'] != 'completed' and response['data']['status'] != 'failed' and x < 30:
        x += 1
        try:
            print(response['data']['id'], x)
            url = f"{MIDURL}{response['data']['id']}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {MIDKEY}',
            }

            response1 = requests.get(url, headers=headers)
            response = response1.json()
            print(response)
        except Exception as err:
            print('err  :  ', err)
        time.sleep(random.randint(3, 8))

    return response['data']



def process_response(response, obj):
    if 'data' in response:
        time.sleep(random.randint(3, 8))
        finished = wait_to_finish(response)
        print('finished - ', finished)
        if finished is not None and 'status' in finished and finished['status'] == 'completed':
            obj['gridFinished'] = True
            obj['buttonMessageId'] = finished['id']
            
            grid_img_url = finished['url']
            item11 = grid_img_url.split('http://')
            item21 = item11[1].split(':8055')
            the_real_deal1 = 'http://127.0.0.1:8055' + item21[1]
            obj['gridImgUrl'] = the_real_deal1
            obj['upscaledUrls'] = []
            upscaled_urls = finished.get('upscaled_urls', [])
            for item in upscaled_urls:
                item1 = item.split('http://')
                item2 = item1[1].split(':8055')
                the_real_deal = 'http://127.0.0.1:8055' + item2[1]
                obj['upscaledUrls'].append(the_real_deal)

        return obj


def click_obscured_element(self, element):
    """Try different methods to click an obscured element"""
    try:
        # Method 2: Scroll into view and then JavaScript click
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)  # Wait for scroll
        self.driver.execute_script("arguments[0].click();", element)
        return True
    except Exception as e2:
        print(f"Scroll and click failed: {str(e2)}")
        try:
            # Method 3: Action chains
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click().perform()
            return True
        except Exception as e3:
            print(f"Action chains failed: {str(e3)}")
            try:
                # Method 4: Remove obscuring element temporarily
                self.driver.execute_script("""
                    var element = arguments[0];
                    var observer = new MutationObserver(function(mutations) {
                        element.click();
                        observer.disconnect();
                    });
                    observer.observe(document.body, { childList: true, subtree: true });
                    var obscuringElement = document.elementFromPoint(arguments[1], arguments[2]);
                    if(obscuringElement) {
                        var originalDisplay = obscuringElement.style.display;
                        obscuringElement.style.display = 'none';
                        element.click();
                        setTimeout(function() {
                            obscuringElement.style.display = originalDisplay;
                        }, 100);
                    }
                """, element, 608, 588)  # Use the coordinates from your error message
                return True
            except Exception as e4:
                print(f"All click methods failed: {str(e4)}")
                return False


def make_image(self, effective_bg, image_type, location_options, text, size):
    try:

        # Get original dimensions
        original_width, original_height = size
        
        reduced_width, reduced_height = reduce_aspect_ratio(original_width, original_height)

        # api call for prompt for new image, then make new image
        starting='```json'

        splits = text.split('\n')
        ree=f'<xml>'
        ree=ree+f'<previous_alt_text>{effective_bg["alt"]}</previous_alt_text>'
        ree=ree+'<text>'
        for split in splits:
            ree=ree+f'<line>{split}</line>'
        ree=ree+'</text>'
        
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

        prompt="given this xml, create a short prompt for a "+image_type+" for a website for given location.  The image prompt should be relative to the given text, and alt text of the image it is replacing if in xml.  \n Do not ask me any questions. Just provide the JSON. Return answer in the following json format: \{\"prompt\":\"short prompt for new image\"\}"
        # prompt=f'given this xml, update the text for a website template about {location}  \n return answer in same json format as original json.  I need every item in the array in the final returned array. All text that should be changed to be changed.  This is for a website template.  All of these elements are already on the page.  I need to update the words.  Do not leave any items from original json array out.  Do not ask me any questions.  Just provide the updated JSON array.'
        image_prompt = callClaude(ree,prompt,starting)
        print(image_prompt)
        rere = image_prompt
        index = rere.find('```')
        
        new_image_prompt=rere    
        # If the string is found, keep everything up to it
        if index != -1:
            new_image_prompt = rere[:index]

        img_prompt = json.loads(new_image_prompt)

        try:
            # make new image
            data = {
                'prompt': ((img_prompt['prompt'] if 'prompt' in img_prompt else new_image_prompt)+ '--ar '+str(reduced_width)+':'+str(reduced_height) +' --profile q9492vp')
            }
            response = create_image(data)
            print('response ', response)
            obj = process_response(response,{})
            print("obj ",obj)

            if 'upscaledUrls' in obj:
                # insert image into page builder
                new_url = insert_image(self, effective_bg,obj,image_type)

                if new_url:
                    response = requests.get(new_url)
                    img = Image.open(BytesIO(response.content))


        except Exception as e:
            print(f"Error creating image: {str(e)}")

    except Exception as e:
        print(f"Error making image: {str(e)}")


def insert_image(self, effective_bg, obj, image_type):
    try:
       
        print('element clicked 1', effective_bg['nearest_parent_id'])
        parent_element = self.driver.find_element(By.ID, effective_bg['nearest_parent_id'])

        click_obscured_element(self, effective_bg['element'] if image_type == 'background image' else parent_element)
        print('element clicked 2')

        time.sleep(random.uniform(1, 2))

        # Wait a bit after clicking
        # time.sleep(random.uniform(1, 2))
        try:

            # # Find and click the sidebar element
            sidebar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hl-builder-settings-sidebar'))
            )
            print('sidebar found')

        except Exception as e:
            print(f"Error finding sidebar: {str(e)}")

        try:
            
            # Get the label text
            bgImage = sidebar.find_element(By.ID, "bgImage")
            print('bgImage', bgImage)
            # # Find the color picker
            if image_type == 'background image':
                # get parent of bg and then search for button
                parent = bgImage.find_element(By.XPATH, "./..")
                
                bg_button = parent.find_element(
                    By.CSS_SELECTOR, "div.n-input-group-label"
                )
            else:
                parent = bgImage.find_element(By.XPATH, "./..")
                parent1 = parent.find_element(By.XPATH, "./..")

                bg_button = parent1.find_element(
                    By.TAG_NAME, "button"
                )                

            bg_button.click()

            # Switch back to the default content
            self.driver.switch_to.default_content()

            time.sleep(random.uniform(3,5))
            file_container = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.n-card__content div.hl-modal-content div.modal-media-contain div'))
            )

            file_input = file_container.find_element(By.CSS_SELECTOR, "input[type='file']")

            file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')  # Adjust this XPath if necessary
            for upscaledUrl in obj['upscaledUrls']:
                split = upscaledUrl.split('/')
                mountLoc = "\\\\wsl.localhost\\docker-desktop\\mnt\\docker-desktop-disk\\data\\docker\\volumes\\imagineapi_api\\_data\\"
                id1 = split[len(split)-1]

                file_path = mountLoc+id1
                file_input.send_keys(file_path)
                print('uploading')
                time.sleep(random.uniform(1.5,2))

            time.sleep(random.uniform(10,15))

            # still need to pick random.randint(0,3)
            drag_select = file_container.find_element(
                By.CSS_SELECTOR, "div.drag-select"
            )
            children = drag_select.find_elements(By.XPATH, ".//*")
            # print('children - ',children)
            randy = random.randint(0,3)
            print('randy - ',randy)
            # Create an instance of ActionChains
            actions = ActionChains(self.driver)
            # Perform the double-click action
            toClick = children[randy]
            # toClick = children[randy]
            print('toClick',toClick)
            actions.double_click(toClick).perform()
            print('toClick was clicked')

            # copy link to clipboard

            time.sleep(random.uniform(2,3))

            print('switching to iframe')
            # Switch to the iframe
            iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
            self.driver.switch_to.frame(iframe)
            print('switched to iframe')
            time.sleep(random.uniform(1,2))


            sidebar = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hl-builder-settings-sidebar'))
            )

            if image_type == 'background image':
                # Get the label text
                bgImage = sidebar.find_element(By.ID, "bgImage")
                bg_input = bgImage.find_element(
                    By.CSS_SELECTOR, "input.n-input__input-el"
                )
                print('bg_input', bg_input.get_attribute("value").strip())
            else:
                bg_input = sidebar.find_element(By.ID, "bgImage")


            sidebar.click()

            return bg_input.get_attribute("value").strip()
            
        except Exception as e:
            print(f"Error finding bg_input: {str(e)}")
            return None
    except Exception as e:
        print(f"Error changing image: {str(e)}")
        return None


def is_image_visible(self, image_element):
    """Check if image is visible using multiple methods"""
    try:
        # Method 1: Check if element is displayed and has size
        if not image_element.is_displayed():
            return False
            
        # Method 2: Check dimensions
        size = image_element.size
        if size['height'] == 0 or size['width'] == 0:
            return False
            
        # Method 3: Check visibility using JavaScript
        is_visible = self.driver.execute_script("""
            var elem = arguments[0];
            return !!(
                elem.offsetWidth || 
                elem.offsetHeight || 
                elem.getClientRects().length
            ) &&
            window.getComputedStyle(elem).visibility !== 'hidden' &&
            window.getComputedStyle(elem).display !== 'none';
        """, image_element)
        
        return is_visible
        
    except Exception as e:
        print(f"Error checking image visibility: {str(e)}")
        return False


def get_all_child_text(self, element):
    """
    Recursively get all text from an element, its siblings, and all their children
    Returns a single string with text separated by newlines
    """
    try:
        text_list = []
        
        # Helper function to process an element and its children
        def process_element(el):
            # Get direct text of element
            direct_text = el.text.strip() if el.text else ''
            if direct_text:
                text_list.append(direct_text)
            
            # Get text from children
            children = el.find_elements(By.XPATH, ".//*")
            for child in children:
                try:
                    class_name = child.get_attribute('class') or ''
                    if 'ui' not in class_name.lower() and 'ui-element' not in class_name.lower():
                        child_text = child.text.strip() if child.text else ''
                        if child_text:
                            splits = child_text.split('\n')
                            for split in splits:
                                text_list.append(split.trim())
                except:
                    continue

        # Process the original element and its children
        process_element(element)

        if len(text_list) <=0:
            # Get and process siblings
            try:
                # Get parent first
                parent = element.find_element(By.XPATH, "./..")
                
                # Get all siblings (including the original element)
                siblings = parent.find_elements(By.XPATH, "./*")
                
                # Process each sibling (except the original element)
                for sibling in siblings:
                    try:
                        if sibling != element:  # Skip the original element
                            class_name = sibling.get_attribute('class') or ''
                            if 'ui' not in class_name.lower() and 'ui-element' not in class_name.lower():
                                process_element(sibling)
                    except:
                        continue
                        
            except Exception as sibling_error:
                print(f"Error processing siblings: {str(sibling_error)}")
            
        # Remove duplicates while preserving order
        seen = set()
        unique_text = []
        for text in text_list:
            if text not in seen:
                seen.add(text)
                unique_text.append(text)
                
        if len(unique_text) >0:
            # Join all text with newlines
            return '\n'.join(unique_text)
        else:
            return None
            
    except Exception as e:
        print(f"Error getting text: {str(e)}")
        return ""

# Calculate reduced aspect ratio
def reduce_aspect_ratio(width, height):
    """Reduce aspect ratio to lowest terms"""
    def gcd(a, b):
        """Calculate Greatest Common Divisor"""
        while b:
            a, b = b, a % b
        return a
    
    divisor = gcd(width, height)
    return width // divisor, height // divisor