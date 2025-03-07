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




class ColorAnalyzer:
    def __init__(self, driver):
        self.driver = driver
        self.LUMINANCE_THRESHOLD = 0.5
        self.wait = WebDriverWait(self.driver, 30)
        self.analyzed_images = {}
        self.created=False
    def is_transparent(self, background_color):
        """Check if background is fully transparent"""
        if not background_color or background_color == 'transparent' or background_color == 'none':
            return True
            
        # Check rgba format
        if 'rgba' in background_color:
            alpha = float(re.findall(r'rgba\(.*?,.*?,.*?,(.+?)\)', background_color)[0])
            return alpha == 0
            
        return False

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        try:
            # Remove '#' if present
            hex_color = hex_color.lstrip('#')
            
            # Handle shorthand hex (e.g., #FFF)
            if len(hex_color) == 3:
                hex_color = ''.join(c + c for c in hex_color)
                
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return f"rgb({r}, {g}, {b})"
        except Exception as e:
            print(f"Error converting hex to RGB: {str(e)}")
            return None

    def rgb_to_hex(self, rgb_color):
        """Convert RGB color to hex"""
        try:
            # Extract RGB values using regex
            values = re.findall(r'\d+', rgb_color)
            if len(values) >= 3:
                r, g, b = map(int, values[:3])
                return f"#{r:02x}{g:02x}{b:02x}"
            return None
        except Exception as e:
            print(f"Error converting RGB to hex: {str(e)}")
            return None

    def is_color_similar(self, color1, threshold=20):
        """
        Check if two colors are similar within a threshold
        Colors can be hex or rgb/rgba
        threshold: 0-255, lower means colors need to be more similar
        """
        try:
            # Convert both colors to RGB tuples
            rgb1 = self.parse_color(color1)
            for color_option in color_options:
                old = self.hex_to_rgb(color_option['old'])
                print(rgb1)
                print(old)
                rgb2 = self.parse_color(old)
                print(rgb2)
                
                if not rgb1 or not rgb2:
                    return False
                    
                # Calculate difference for each channel
                r_diff = abs(rgb1[0] - rgb2[0])
                g_diff = abs(rgb1[1] - rgb2[1])
                b_diff = abs(rgb1[2] - rgb2[2])
                print(r_diff,g_diff,b_diff, threshold)
                
                # Return True if all channel differences are within threshold
                if r_diff <= threshold and g_diff <= threshold and b_diff <= threshold:
                    print('inside threshold')
                    color_option['rgb'] = self.hex_to_rgb(color_option['new'])
                    return color_option
            
        except Exception as e:
            print(f"Error comparing colors: {str(e)}")
            return False


    


    def get_element_background(self, element, check_children=False, check_first_child=True):
        """Get background color or image, checking all children first"""
        try:
            # Enhanced JavaScript to better handle background images
            bg_style = self.driver.execute_script("""
                function getBackground(el) {
                    const style = window.getComputedStyle(el);
                    
                    // Get background image and clean up the url
                    let bgImage = style.backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        // Remove url() wrapper and quotes
                        bgImage = bgImage.replace(/url\(['"]?(.*?)['"]?\)/g, '$1');
                    }
                    
                    // Check if image actually exists
                    const hasValidImage = bgImage && 
                                        bgImage !== 'none' && 
                                        !bgImage.includes('data:image/gif;base64') && // Exclude default transparent GIFs
                                        !bgImage.includes('about:blank');
                    
                    return {
                        backgroundColor: style.backgroundColor,
                        backgroundImage: hasValidImage ? bgImage : 'none',
                        isTransparent: style.backgroundColor === 'transparent' || 
                                     style.backgroundColor === 'rgba(0, 0, 0, 0)' ||
                                     style.backgroundColor === '',
                        // Additional debugging info
                        rawBackgroundImage: style.backgroundImage,
                        backgroundSize: style.backgroundSize,
                        backgroundRepeat: style.backgroundRepeat,
                        backgroundPosition: style.backgroundPosition
                    };
                }
                return getBackground(arguments[0]);
            """, element)

            # Debug logging
            element_id = element.get_attribute('id') or 'no-id'

            # Check for valid background
            has_valid_background = (
                not bg_style['isTransparent'] or 
                (bg_style['backgroundImage'] and 
                 bg_style['backgroundImage'] != 'none' and 
                 'data:image' not in bg_style['backgroundImage'])
            )

            if has_valid_background:
                print(f"Found valid background on {element_id}")
                print(f"Checking element {element_id}:")
                print(f"  Background Color: {bg_style['backgroundColor']}")
                print(f"  Background Image: {bg_style['backgroundImage']}")
                print(f"  Raw Background Image: {bg_style['rawBackgroundImage']}")
                print(f"  Background Size: {bg_style['backgroundSize']}")
                print(f"  Is Transparent: {bg_style['isTransparent']}")

                return {
                    'color': bg_style['backgroundColor'],
                    'image': bg_style['backgroundImage'],
                    'element': element,
                    'background_size': bg_style['backgroundSize'],
                    'background_repeat': bg_style['backgroundRepeat'],
                    'background_position': bg_style['backgroundPosition']
                }

            # Rest of your existing code for checking children and first child...

            

            # Check all children if requested
            if check_children:
                try:
                    # Get all child elements
                    children = element.find_elements(By.XPATH, ".//*")
                    for child in children:
                        class_name = child.get_attribute('class') or ''
                        if 'ui' not in class_name.lower() and 'ui-element' not in class_name.lower():
                            # Check each child (but don't check their children to avoid recursion)
                            child_bg = self.get_element_background(child, check_children=False, check_first_child=False)
                            if child_bg and (not self.is_transparent(child_bg['color']) or child_bg['image'] != 'none'):
                                return child_bg
                except Exception as e:
                    print(f"Error checking children: {str(e)}")

            # Check first child div if requested
            if check_first_child:
                try:
                    # Find all immediate div children
                    child_divs = element.find_elements(By.XPATH, "./div")
                    
                    # Find first div without ui classes
                    for child in child_divs:
                        class_name = child.get_attribute('class') or ''
                        if 'ui' not in class_name.lower() and 'ui-element' not in class_name.lower():
                            child_bg = self.get_element_background(child, check_children=False, check_first_child=False)
                            if child_bg and (not self.is_transparent(child_bg['color']) or child_bg['image'] != 'none'):
                                return child_bg
                            break  # Only check the first valid div
                except Exception as e:
                    print(f"Error checking first child: {str(e)}")
                    pass

            return None

        except Exception as e:
            print(f"Error getting background: {str(e)}")
            traceback.print_exc()  # Print full stack trace
            return None


    def find_effective_background(self, element):
        """Find effective background checking children first, then parents up to section-"""
        try:
            # Debug starting point
            print(f"\nStarting background search for element: {element.get_attribute('id') or 'no-id'}")

            # First check the element and all its children
            bg = self.get_element_background(element, check_children=True, check_first_child=False)
            if bg:
                print("bg['image'] - ",bg['image'])
            if bg and ((not self.is_transparent(bg['color'])) or bg['image'] != 'none'):
                print("Found background in element or children:")
                print(f"  Color: {bg['color']}")
                print(f"  Image: {bg['image']}")
                print(' **********************************')
                return bg

            # If no background found in children, start checking parents
            current_element = element
            while current_element:
                element_id = current_element.get_attribute('id') or 'no-id'
                print(f"\nChecking parent: {element_id}")

                if 'section-' in element_id:
                    print(f"Found section element: {element_id}")
                    bg = self.get_element_background(current_element, check_children=False, check_first_child=True)
                    if bg:
                        print("bg['image'] - ",bg['image'])
                    if bg and ((not self.is_transparent(bg['color'])) or bg['image'] != 'none'):
                        print("Found background in section:")
                        print(f"  Color: {bg['color']}")
                        print(f"  Image: {bg['image']}")
                        print(' **********************************')
                        return bg
                    else:
                        return None

                try:
                    current_element = current_element.find_element(By.XPATH, "./..")
                    bg = self.get_element_background(current_element, check_children=False, check_first_child=True)
                    if bg:
                        print("bg['image'] - ",bg['image'])
                    if bg and ((not self.is_transparent(bg['color'])) or bg['image'] != 'none'):
                        print("Found background in parent:")
                        print(f"  Color: {bg['color']}")
                        print(f"  Image: {bg['image']}")
                        print(' **********************************')
                        return bg
                except:
                    break

            print("No background found in element tree")
            return None

        except Exception as e:
            print(f"Error finding effective background: {str(e)}")
            traceback.print_exc()
            return None

    def get_relative_luminance(self, rgb):
            """Calculate relative luminance using WCAG formula"""
            r, g, b = [x/255 for x in rgb]  # Normalize to 0-1
            
            # Convert to sRGB
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055) ** 2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055) ** 2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055) ** 2.4
            
            # Calculate luminance
            return 0.2126 * r + 0.7152 * g + 0.0722 * b


    def parse_color(self, color):
        """Parse various color formats (rgb, rgba, hex) to RGB tuple"""
        try:
            if not color:
                return None
                
            # Handle rgb/rgba format
            if color.startswith(('rgb', 'rgba')):
                values = re.findall(r'\d+', color)
                return tuple(map(int, values[:3]))
                
            # Handle hex format
            elif color.startswith('#'):
                color = color.lstrip('#')
                if len(color) == 3:  # Handle shorthand hex
                    color = ''.join(c + c for c in color)
                return tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
                
            return None
        except:
            return None


    def is_color_dark(self, rgb):
        """Determine if a color is dark based on luminance"""
        luminance = self.get_relative_luminance(rgb)
        return luminance < self.LUMINANCE_THRESHOLD


    def analyze_background_image(self, bg_image_url, effective_bg):
        """Analyze background image dimensions, aspect ratio, and brightness"""
        try:

            text = get_all_child_text(self,effective_bg['element'])
            print('text - ',text)

            # Download and analyze image
            response = requests.get(bg_image_url)
            img = Image.open(BytesIO(response.content))
            
            
            
            new_url = insert_image(self,effective_bg,{},'background image')
            
            # made_image = make_image(self, effective_bg,'background image',location_options,img.size)


            # Resize image for color analysis
            img.thumbnail((100, 100))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Calculate average color
            pixels = list(img.getdata())
            avg_color = tuple(sum(color) // len(pixels) for color in zip(*pixels))
            print('original ','width ', original_width,'height ', original_height)
            print('aspect_ratio ','width ', reduced_width,'height ', reduced_height)
            return {
                'dimensions': {
                    'original': {
                        'width': original_width,
                        'height': original_height
                    },
                    'aspect_ratio': {
                        'width': reduced_width,
                        'height': reduced_height,
                        'string': f"{reduced_width}:{reduced_height}"
                    }
                },
                'rgb': avg_color,
                'is_dark': self.is_color_dark(avg_color),
                'luminance': self.get_relative_luminance(avg_color)
            }

        except Exception as e:
            print(f"Error analyzing background image: {str(e)}")
            return None


    

    def find_color_settings(self, sidebar):
        """Find all color settings in the sidebar"""
        try:
            # Find all color control groups
            color_controls = sidebar.find_elements(
                By.XPATH,
                "//div[contains(@class, 'hl_style-control')]"
            )
            
            print('color_controls length', len(color_controls))
            color_settings = {}
            
            for control in color_controls:
                try:
                    # Get the label text
                    label = control.find_element(By.CLASS_NAME, "col-form-label").text.strip()
                    print('label', label)
                    
                    # Find the color picker
                    color_picker = control.find_element(
                        By.CLASS_NAME, "color-pallet"
                    )
                    print('color_picker', color_picker)
                    
                    color_settings[label] = color_picker
                    
                except:
                    continue
                    
            return color_settings
            
        except Exception as e:
            print(f"Error finding color settings: {str(e)}")
            return {}

    def click_color_setting(self, color_settings, setting_name):
        """Click specific color setting"""
        try:
            if setting_name in color_settings:
                color_settings[setting_name].click()
                print('setting_name is in color_settings - ',setting_name)
                return True
            else:
                print('setting_name is not in color_settings')
            return False
        except Exception as e:
            print(f"Error clicking {setting_name}: {str(e)}")
            return False

    def enter_custom_color(self, color_name, hex_color):
        """
        Enter custom color details in the color picker form
        color_name: name/label for the custom color
        hex_color: hex color value
        """
        try:
            # Wait for the custom color form to be present
            self.wait.until(
                EC.presence_of_element_located((By.ID, "custom-color-form"))
            )
            
            # Find and fill the color name input
            name_input = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@class='bg-white mt-1 block w-full pl-3 pr-10 text-base border-gray-300 focus:outline-none focus:ring-curious-blue-500 focus:border-curring-curious-blue-500 sm:text-sm rounded-md hl_input']")
                )
            )
            name_input.clear()
            name_input.send_keys(color_name)
            
            # Find and fill the hex color input
            color_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "color-input"))
            )
            color_input.clear()
            color_input.send_keys(hex_color)

            time.sleep(1)

            # Click the "Add Color" button
            add_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Add Color')]")
                )
            )
            add_button.click()
            
            return True
            
        except Exception as e:
            print(f"Error adding custom color: {str(e)}")
            return False


    def select_color_in_picker(self, desired_color):
        """
        Select color in the open color picker
        desired_color: the title/name of the color to select
        Returns: True if color selected, 'custom' if custom option clicked, False if failed
        """
        try:
            time.sleep(1)  # Small wait for click to register
            # Wait for color picker to be present (might need to adjust selector based on your UI)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.color-border.row"))
            )
            
            # First try to find the color by title
            try:
                # Look for the color div with matching title
                color_div = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[@class='color-box' and @title='{desired_color}']")
                    )
                )
                
                # Click the color div
                self.driver.execute_script("arguments[0].click();", color_div)
                time.sleep(0.5)  # Small wait for click to register
                
                return True
                
            except Exception as color_error:
                print(f"Color not found: {str(color_error)}")
                
                # If color not found, look for custom color option
                try:
                    custom_option = self.wait.until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//span[contains(text(), \"Didn't find your color? Add custom one!\")]")
                        )
                    )
                    
                    # Click custom color option
                    self.driver.execute_script("arguments[0].click();", custom_option)
                    time.sleep(0.5)  # Small wait for click to register
                    
                    return "custom"
                    
                except Exception as custom_error:
                    print(f"Custom option not found: {str(custom_error)}")
                    return False
                    
        except Exception as e:
            print(f"Error in color picker: {str(e)}")
            return False
 
    def changeColor(self, effective_bg, colorObj, toChange):
        try:
           
            print('element clicked 1')
            effective_bg['element'].click()
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

            color_settings = self.find_color_settings(sidebar)

            print('color_settings', color_settings)

            for changeLabel in toChange:

                # Click background color
                if self.click_color_setting(color_settings, changeLabel):
                    print('inside click_color_setting - ', changeLabel)
                    time.sleep(1)
                    # Handle color picker...
                    # search for name of color tag if not then make it
                    # Try to select the color
                    result = self.select_color_in_picker(colorObj['name'])
                    print(result)
                    
                    
                    if result == "custom":
                        if self.enter_custom_color(colorObj['name'], colorObj['new']):
                            print(f"Successfully entered custom color {colorObj['name'], colorObj['new']}")
                            # close color picker
                            time.sleep(1)
                            self.click_color_setting(color_settings, changeLabel)
                            return True
                        else:
                            # close color picker
                            time.sleep(1)
                            self.click_color_setting(color_settings, changeLabel)
                            print(f"Failed to enter custom color {colorObj['name'], colorObj['new']}")
                            return False
                    elif result:
                        # close color picker
                        time.sleep(1)
                        self.click_color_setting(color_settings, changeLabel)
                        print(f"Successfully selected {colorObj['name']}")
                        return True

            
        except Exception as e:
            print(f"Error changing backgroundColor: {str(e)}")    



    



    def should_use_white_text(self, element):
        """Determine if white text should be used based on effective background"""
        if self.created:
            return False

        effective_bg = self.find_effective_background(element)
        
        if not effective_bg:
            return False  # Default to dark text
        

        # If background image exists, analyze it
        if effective_bg['image'] and effective_bg['image'] != 'none':

            #check if image has already been analyzed

            if effective_bg['image'] in self.analyzed_images:
                bg_image = self.analyzed_images[effective_bg['image']]
            else:
                bg_image = self.analyze_background_image(effective_bg['image'], effective_bg)
                self.analyzed_images[effective_bg['image']] = bg_image
                print('bg_image - ', bg_image)
            
            # similar = self.is_color_similar(effective_bg['color'])
            # print('similar - ', similar)


            if bg_image:
                print('bg_image is_dark - ', bg_image['is_dark'])
                return bg_image['is_dark']
                
        # If solid background color exists, analyze it
        if effective_bg['color'] and not self.is_transparent(effective_bg['color']):
            similar = self.is_color_similar(effective_bg['color'])
            print('similar - ', similar)
            # if similar:
                # # if similar then change colors to similar['new'] check if name is made for it if not make it
                # changed = self.changeColor(effective_bg, similar,["BACKGROUND COLOR"])

                # # if background changed need to update effective_bg['color']
                # if changed:
                #     effective_bg['color'] = similar['rgb']


            bg_color = self.parse_color(effective_bg['color'])
            print('bg_color - ', bg_color)
            if bg_color:
                dark = self.is_color_dark(bg_color)
                print('bg_color is dark - ', dark)
                # print('changing text color to - ', 'white' if dark else 'black')
                # self.changeColor({'element':element}, {'name':'White', 'new':'#fff'} if dark else {'name':'Black', 'new':'#000'},["COLOR","BOLD TEXT COLOR","ITALIC TEXT COLOR", "UNDERLINE TEXT COLOR","LINK TEXT COLOR","ICON COLOR", "SUB TEXT COLOR"])
                return 
                
        return False               
                    
            


class webvistaScraper:
    def __init__(self):
        self.driver = webdriver.Firefox(options=browserOptions(),service=Service(executable_path=GeckoDriverManager().install()))
        self.wait = WebDriverWait(self.driver, 30)
        self.text_data = []

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
        text_data = []
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

        def process_element(element, depth=0):
            """Recursively process elements down to the deepest level"""
            try:
                # First, process all children
                children = element.find_elements(By.XPATH, "./*")
                for child in children:
                    process_element(child, depth + 1)

                # Then check if this element has its own text
                direct_text = get_direct_text(element)
                if direct_text:
                    element_type = element.tag_name
                    nearest_parent_id = self.find_nearest_parent_id(element)

                    if any(skip_id.lower() in nearest_parent_id for skip_id in ['previewer','section-','row-','col-','faq-']):
                        return

                    # Create unique identifier for this element's text and location
                    element_id = f"{nearest_parent_id}"
                    
                    if element_id not in processed_elements:
                        processed_elements.add(element_id)
                        text_data.append({
                            "element_type": element_type,
                            "current_text": direct_text,
                            "nearest_parent_id": nearest_parent_id,
                            "depth": depth
                        })

            except Exception as e:
                print(f"Error processing element at depth {depth}: {str(e)}")

        # Start processing from the top
        process_element(previewer)
        
        # Sort by depth and parent ID for better organization
        text_data.sort(key=lambda x: (x['depth'], x['nearest_parent_id']))
        
        faqs = self.extract_faq_content(previewer)
        for faq in faqs:
            text_data.append(faq)
        
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

    def update_text_elements(self, text_data, old_result_dict):
        for item in text_data:

            if 'nearest_parent_id' not in item or any(skip_id.lower() in item['nearest_parent_id'] for skip_id in ['button','text-editor_imf_1','text-editor_imf_2','text-editor_imf_3','text-editor_imf_4']) or any(skip_id.lower() == item['current_text'] for skip_id in ['Instagram','LinkedIn','Facebook']):
                print('returning item - ',item)
                continue
            try:
                # Find and click the parent element
                parent = self.wait.until(
                    EC.element_to_be_clickable((By.ID, item['nearest_parent_id']))
                )
                print('parent found')
                # Click using JavaScript with extended events
                self.driver.execute_script("""
                   var element = arguments[0];
                   
                   // Click events
                   element.click();
                   element.dispatchEvent(new MouseEvent('click', {
                       'view': window,
                       'bubbles': true,
                       'cancelable': true
                   }));
                   
                   // Focus events
                   element.dispatchEvent(new FocusEvent('focus', {
                       'view': window,
                       'bubbles': true,
                       'cancelable': true
                   }));
                   
                   // MouseDown/MouseUp events
                   element.dispatchEvent(new MouseEvent('mousedown', {
                       'view': window,
                       'bubbles': true,
                       'cancelable': true
                   }));
                   element.dispatchEvent(new MouseEvent('mouseup', {
                       'view': window,
                       'bubbles': true,
                       'cancelable': true
                   }));
                """, parent)
                print('parent clicked')
                
                # Wait a bit after clicking
                time.sleep(random.uniform(1, 2))
                
                if 'nearest_parent_id' in item and item['nearest_parent_id'] in old_result_dict:
                    print(old_result_dict[item['nearest_parent_id']])
                    old_text = old_result_dict[item['nearest_parent_id']]['current_text']
                    print(old_text)
                else:
                    continue
                # Find the element with the current text
                # Try multiple strategies to find the text element
                text_element = None
                try:
                    # Try finding by exact text match
                    text_element = parent.find_element(
                        By.XPATH, f".//*[text()='{old_text}']"
                    )
                    print('1')
                except:
                    try:
                        # Try finding by contains text
                        text_element = parent.find_element(
                            By.XPATH, f".//*[contains(text(), '{old_text}')]"
                        )
                        print('2')
                    except:
                        try:
                            # Try finding by element type if specified
                            text_element = parent.find_elements(
                                By.XPATH, ".//*[text()[normalize-space() != '']]"
                            )
                            print('3')
                            # text_element = parent.find_element(By.XPATH, '//*[@contenteditable="true"]')
                            
                        except:
                            print(f"Could not find text element for {item}")
                            continue

                if text_element or isinstance(text_element, list):
                    if isinstance(text_element, list):
                        print('text_element is a list')
                        split = item['current_text'].split('\n')
                        print('split - ',split)
                        print('lens - ', len(split), len(text_element))

                        if len(split) <= len(text_element):
                            for index, text_element_item in enumerate(text_element):
                                # Extended JavaScript with all events
                                self.driver.execute_script("""
                                    function updateElementText(element, newText) {
                                        // First focus the element
                                        element.focus();
                                        element.dispatchEvent(new Event('focus', { bubbles: true }));
                                        
                                        // Handle different types of elements
                                        if (element.hasAttribute('contenteditable')) {
                                            element.innerHTML = newText;
                                        } else if (element.tagName.toLowerCase() === 'input' || 
                                                 element.tagName.toLowerCase() === 'textarea') {
                                            element.value = newText;
                                        } else {
                                            element.textContent = newText;
                                        }
                                        
                                        
                                        // Additional specific events
                                        element.dispatchEvent(new Event('input', { bubbles: true }));
                                        element.dispatchEvent(new Event('change', { bubbles: true }));
                                        element.dispatchEvent(new Event('blur', { bubbles: true }));
                                        
                                        // Trigger a custom event that some editors might use
                                        element.dispatchEvent(new CustomEvent('textChange', {
                                            bubbles: true,
                                            detail: { value: newText }
                                        }));
                                        
                                        // Remove focus
                                        element.blur();
                                    }
                                    
                                    updateElementText(arguments[0], arguments[1]);
                                """, text_element_item, split[index])
                        else:
                            # Extended JavaScript with all events
                            self.driver.execute_script("""
                                function updateElementText(element, newText) {
                                    // First focus the element
                                    element.focus();
                                    element.dispatchEvent(new Event('focus', { bubbles: true }));
                                    
                                    // Handle different types of elements
                                    if (element.hasAttribute('contenteditable')) {
                                        element.innerHTML = newText;
                                    } else if (element.tagName.toLowerCase() === 'input' || 
                                             element.tagName.toLowerCase() === 'textarea') {
                                        element.value = newText;
                                    } else {
                                        element.textContent = newText;
                                    }
                                    
                                    
                                    // Additional specific events
                                    element.dispatchEvent(new Event('input', { bubbles: true }));
                                    element.dispatchEvent(new Event('change', { bubbles: true }));
                                    element.dispatchEvent(new Event('blur', { bubbles: true }));
                                    
                                    // Trigger a custom event that some editors might use
                                    element.dispatchEvent(new CustomEvent('textChange', {
                                        bubbles: true,
                                        detail: { value: newText }
                                    }));
                                    
                                    // Remove focus
                                    element.blur();
                                }
                                
                                updateElementText(arguments[0], arguments[1]);
                            """, text_element[0], item['current_text'])
                    else:

                        # Extended JavaScript with all events
                        self.driver.execute_script("""
                            function updateElementText(element, newText) {
                                // First focus the element
                                element.focus();
                                element.dispatchEvent(new Event('focus', { bubbles: true }));
                                
                                // Handle different types of elements
                                if (element.hasAttribute('contenteditable')) {
                                    element.innerHTML = newText;
                                } else if (element.tagName.toLowerCase() === 'input' || 
                                         element.tagName.toLowerCase() === 'textarea') {
                                    element.value = newText;
                                } else {
                                    element.textContent = newText;
                                }
                                
                                
                                // Additional specific events
                                element.dispatchEvent(new Event('input', { bubbles: true }));
                                element.dispatchEvent(new Event('change', { bubbles: true }));
                                element.dispatchEvent(new Event('blur', { bubbles: true }));
                                
                                // Trigger a custom event that some editors might use
                                element.dispatchEvent(new CustomEvent('textChange', {
                                    bubbles: true,
                                    detail: { value: newText }
                                }));
                                
                                // Remove focus
                                element.blur();
                            }
                            
                            updateElementText(arguments[0], arguments[1]);
                        """, text_element, item['current_text'])

                else:
                    print('no text element found - ', text_element)

            except Exception as e:
                print(f"Error updating element {item}: {str(e)}")
                continue

    def update_faq_elements(self, text_data, old_result_dict):
        try:
            # Find and click the faq element
            faq = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hl-faq'))
            )
            time.sleep(random.uniform(1, 2))
            print('faq found')
            # Click using JavaScript with extended events
            self.driver.execute_script("""
               var element = arguments[0];
               
               // Click events
               element.click();
               element.dispatchEvent(new MouseEvent('click', {
                   'view': window,
                   'bubbles': true,
                   'cancelable': true
               }));
               
               // Focus events
               element.dispatchEvent(new FocusEvent('focus', {
                   'view': window,
                   'bubbles': true,
                   'cancelable': true
               }));
               
               // MouseDown/MouseUp events
               element.dispatchEvent(new MouseEvent('mousedown', {
                   'view': window,
                   'bubbles': true,
                   'cancelable': true
               }));
               element.dispatchEvent(new MouseEvent('mouseup', {
                   'view': window,
                   'bubbles': true,
                   'cancelable': true
               }));
            """, faq)
            print('faq clicked')
            time.sleep(random.uniform(1, 2))

            faqs = []
            for item in text_data:
                if 'element_type' in item and item['element_type'] == 'faq':
                    faqs.append(item)
    
            try:
                # Try finding by exact text match
                faq_children = faq.find_elements(
                    By.CSS_SELECTOR, "div.hl-faq-child"
                )
                time.sleep(random.uniform(.25, .52))

                for index1, faq_element in enumerate(faq_children):

                    # Try finding by exact text match
                    faq_child_heading = faq_element.find_element(
                        By.CSS_SELECTOR, "div.hl-faq-child-heading"
                    )
                    # Try finding by exact text match
                    faq_child_panel = faq_element.find_element(
                        By.CSS_SELECTOR, "div.hl-faq-child-panel"
                    )

                    faq_child_list = [faq_child_heading,faq_child_panel]

                    for index, faq_child in enumerate(faq_child_list):
                        # Try multiple strategies to find the text element
                        text_element = None
                        try:
                            # Try finding by exact text match
                            text_element = faq_child.find_element(
                                By.XPATH, ".//*[text()[normalize-space() != '']]"
                            )

                            if text_element:
                                if index == 0:
                                    q_or_a = 'question'
                                else: 
                                    q_or_a = 'answer'
                                print('found text element')

                                print('inserting text - ',faqs[index1][q_or_a])

                                self.driver.execute_script("""
                                   var element = arguments[0];
                                   
                                   // Click events
                                   element.click();
                                   element.dispatchEvent(new MouseEvent('click', {
                                       'view': window,
                                       'bubbles': true,
                                       'cancelable': true
                                   }));
                                   
                                   // Focus events
                                   element.dispatchEvent(new FocusEvent('focus', {
                                       'view': window,
                                       'bubbles': true,
                                       'cancelable': true
                                   }));
                                   
                                   // MouseDown/MouseUp events
                                   element.dispatchEvent(new MouseEvent('mousedown', {
                                       'view': window,
                                       'bubbles': true,
                                       'cancelable': true
                                   }));
                                   element.dispatchEvent(new MouseEvent('mouseup', {
                                       'view': window,
                                       'bubbles': true,
                                       'cancelable': true
                                   }));
                                """, faq_child)
                                print('faq child clicked')

                                time.sleep(random.uniform(1, 2))

                                # Extended JavaScript with all events
                                self.driver.execute_script("""
                                    function updateElementText(element, newText) {
                                        // First focus the element
                                        element.focus();
                                        element.dispatchEvent(new Event('focus', { bubbles: true }));
                                        
                                        // Handle different types of elements
                                        if (element.hasAttribute('contenteditable')) {
                                            element.innerHTML = newText;
                                        } else if (element.tagName.toLowerCase() === 'input' || 
                                                 element.tagName.toLowerCase() === 'textarea') {
                                            element.value = newText;
                                        } else {
                                            element.textContent = newText;
                                        }
                                        
                                        
                                        // Additional specific events
                                        element.dispatchEvent(new Event('input', { bubbles: true }));
                                        element.dispatchEvent(new Event('change', { bubbles: true }));
                                        element.dispatchEvent(new Event('blur', { bubbles: true }));
                                        
                                        // Trigger a custom event that some editors might use
                                        element.dispatchEvent(new CustomEvent('textChange', {
                                            bubbles: true,
                                            detail: { value: newText }
                                        }));
                                        
                                        // Remove focus
                                        element.blur();
                                    }
                                    
                                    updateElementText(arguments[0], arguments[1]);
                                """, text_element, faqs[index1][q_or_a])


                        except:
                            print(f"Could not find text element for {faqs[index]}")
                            continue
                        
            except:
                print('faq children not found')
        except:
            print('error updating faqs')

                   
                    
            # Wait a bit after clicking
            # time.sleep(random.uniform(1, 2))

            # # Find and click the sidebar element
            # sidebar = self.wait.until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hl-builder-settings-sidebar'))
            # )
            # print('sidebar found')
            
            #   


    # Usage example:
    def find_images(self, previewer):
        image_data = []
        try:
           
            image_elements = previewer.find_elements(By.TAG_NAME, "img")
            
            for image in image_elements:
                nearest_parent_id = self.find_nearest_parent_id(image)
                print(nearest_parent_id)
                nearest_parent = previewer.find_element(By.ID, nearest_parent_id)
                print('found nearest_parent')

                

                class_name = nearest_parent.get_attribute('class') or ''
                print('class_name ',class_name)
                if 'ui' in class_name.lower() and 'ui-element' in class_name.lower():
                    continue

                visible = is_image_visible(self,image)
                print('visible ',visible)
                if not visible:
                    continue

                data = {
                    "element": image,
                    "image": image.get_attribute('src'),
                    "nearest_parent_id": nearest_parent_id,
                    "alt": image.get_attribute('alt')
                }

                image_data.append(data)

                # new_url = insert_image(self,data,{},'image')
                text = ''
                current_element = nearest_parent
                while current_element: 
                    # go to parent
                    text = get_all_child_text(self,current_element)
                    if text and text != None:
                        break;
                    current_element = current_element.find_element(By.XPATH, "./..")
                    current_element_id = current_element.get_attribute('id')
                    if any(skip_id.lower() in nearest_parent_id for skip_id in ['previewer']):
                        break


                # Download and analyze image
                response = requests.get(data['image'])
                img = Image.open(BytesIO(response.content))
                    
                inserted_image = make_image(self, data,'image', location_options, text, img.size)


        except Exception as e:
            print(f"Error finding images: {str(e)}")
        
        return image_data

    def update_text_colors(self, elements, old_elements):
        analyzer = ColorAnalyzer(self.driver)
        for element1 in elements:
            if 'nearest_parent_id' not in element1:
                continue
            if analyzer.created:
                return

            try:
                element = self.driver.find_element(By.ID, element1['nearest_parent_id'])
                
                # Get effective background
                bg = analyzer.find_effective_background(element)
                
                if bg:
                    print(element1)
                    print(f"Found background on element: {bg['element'].get_attribute('id')}")
                    print(f"Background color: {bg['color']}")
                    print(f"Background image: {bg['image']}")
                    use_white = analyzer.should_use_white_text(element)
                    print('use_white - ', use_white)
                    
                    # # Update text color
                    # self.driver.execute_script(
                    #     f"arguments[0].style.color = '{('white' if use_white else 'black')}';",
                    #     element
                    # )
            
            except Exception as e:
                print(f"Error updating text colors: {str(e)}")



    def start(self, location):
        self.driver.get(f"https://app.webvista.io/location/{location_options['id']}/page-builder/{location_options['pageBuilderId']}")

        # time.sleep(random.uniform(30, 31))
        # try:
        #     # First try: Wait for any potential iframes to load
        #     # funnelBuilderApp = self.wait.until(EC.presence_of_element_located((By.ID, "funnelBuilderApp")))
        #     # self.driver.switch_to.frame(funnelBuilderApp)

        #     iframe = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        #     self.driver.switch_to.frame(iframe)
            
        #     # Now look for previewer
        #     previewer = self.wait.until(EC.presence_of_element_located((By.ID, "previewer")))
        # except:
        #     print("Could not find previewer element")
        #     raise

        # button = previewer.find_element(
        #     By.ID, 'button-xw9pCHhuB'
        # )
        # button.click()
        # time.sleep(random.uniform(1, 2))

        # # # Find and click the sidebar element
        # sidebar = self.wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.hl-builder-settings-sidebar'))
        # )
        # print('sidebar found')
    
        # if previewer:
        #     print('previewer found - getting text elements')
        #     # Get all text elements and their context
        #     text_data = self.get_text_elements(previewer)
        #     # ... rest of your code
        #     print('text data - ', text_data)

        
        # # Save raw text data to JSON
        # with open('text_elements.json', 'w', encoding='utf-8') as f:
        #     json.dump(text_data, f, indent=4)
            
        text_data = self.load_text_elements()

        # # # Make single AI call with all elements
        ai_response = self.analyze_with_ai(text_data)

        try:
            img_prompt = json.loads(new_text_json)
        except:
            print(new_text_json)
            img_prompt = new_text_json
        
        # # # Save the prompt for reference
        with open('ai_response.txt', 'w', encoding='utf-8') as f:
            f.write(ai_response)

        # self.find_images(previewer)


        # # Convert to dictionary with nearest_parent_id as keys
        # result_dict = {}
        # for item in text_data:
        #     if 'nearest_parent_id' in item:
        #         key = item['nearest_parent_id']
        #         if key not in result_dict:
        #             result_dict[key] = item
        # print(result_dict)
        # # take ai response and update text in website builder
        # ai_response = self.loadAIResponse()

        # Update the text elements
        # self.update_text_elements(ai_response, result_dict)
        # self.update_faq_elements(ai_response, result_dict)
        # self.update_text_colors(ai_response, result_dict)

        time.sleep(random.uniform(120, 121))

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


 


