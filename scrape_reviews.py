import random
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
import pickle
import pandas as pd
from pynotifier import Notification

# NOTE: Turning on a VPN is recommended before running this script!
options = ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument("--disable-dev-shm-usage")
# Ad-blocker for speeding up load times. Another loading optimization is disabling images once the browser window opens.
options.add_argument('--load-extension=/Users/andrewyang/PycharmProjects/G2_Scraper/ublock_origin')
driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
driver.get('https://www.g2.com/')
# Save cookies to reduce amount of times captcha pops up
cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

with open('shuffled_product_links.pkl', 'rb') as f:
    product_links = pickle.load(f)

string_list = []
label_list = []
star_list = []

split_idx = 4  # Specifies what split to start at.
num_splits = 5  # Splits the total data into the specified amount of files
split_len = round(len(product_links) / num_splits)  # Amount of products in each split

for idx, product_link in enumerate(product_links[(split_len * split_idx + 1):]):
    for page in range(1, 101):
        driver.get('{}?page={}'.format(product_link, page))
        repeat = False
        while len(driver.find_elements(by=By.XPATH, value='/html/body[@id="t"]')):  # If encountered error page
            # print("Encountered error page")
            driver.refresh()
            if len(driver.find_elements(by=By.XPATH, value='/html/body[@id="t"]')):
                sleep(5)
            repeat = True
        if len(driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div[2]/div[1]/h1['
                                                       '@data-translate="challenge_headline"]')):
            counter = 40
            while len(driver.find_elements(by=By.XPATH, value='/html/body/div[1]/div[2]/div[1]/h1['
                                                              '@data-translate="challenge_headline"]')):
                if counter >= 40:  # Notify user after 2 minutes
                    counter = 0
                    Notification(title='G2 Scraper', description='Please Re-enter Captcha!').send()
                counter += 1  # Luckily, the captcha detection system is based on time rather than quantity,
                sleep(3)  # so you only need to do the captcha once every hour or so.
            print("saving cookies...")
            pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
        elif len(driver.find_elements(by=By.XPATH, value='/html/body/div/div[@id="cf-error-details"]')):
            counter = 40
            while len(driver.find_elements(by=By.XPATH, value='/html/body/div/div[@id="cf-error-details"]')):
                if counter >= 40:  # Notify user after 2 minutes
                    counter = 0
                    Notification(title='G2 Scraper', description='IP banned. Use a VPN to bypass!').send()
                counter += 1  # You will likely run into this problem once in scraping. Just switch ip
                sleep(3)  # with a VPN to bypass it.
        # get Xpath of the review frame
        test_path = \
            '//*[@id="reviews"]/div/div[@class="paper paper--white paper--box mb-2 position-relative border-bottom "]'
        js = "var q=document.documentElement.scrollTop=100000"
        driver.execute_script(js)
        review_list = driver.find_elements(by=By.XPATH, value=test_path)

        if len(review_list) == 0:
            print("{} ended early at page {}".format(product_link, page))
            sleep(1)
            break
        for review in review_list:
            my_review = review.find_elements(by=By.CLASS_NAME, value='formatted-text')
            my_label = review.find_element(by=By.XPATH, value='./div[1]/div[1]/div[2]/div[not(@alt)]')
            star = \
                review.find_element(by=By.XPATH, value='./div[1]/div[2]/div[1]/div[1]/div[1]').get_attribute(
                    'className').split('-')[-1]
            temp_string = ''
            # many <p> in one review, got to join them together
            for i in my_review:
                temp_string = temp_string + i.get_attribute('textContent')
            string_sublist = temp_string.replace('Review collected by and hosted on G2.com.',
                                                 ";")  # get the three Q&A in one review
            string_list.append(string_sublist)
            label_list.append(my_label.get_attribute('textContent'))
            star_list.append(star)
    # Save data in parts in case the program malfunctions halfway
    if idx and (idx % split_len == 0 or product_link == product_links[-1]):
        df = pd.DataFrame({'review': string_list, 'star': star_list, 'label': label_list})
        df.to_csv('review_data_part_{}.csv'.format(split_idx + int(round(idx / split_len))))
        print('Exported to review_data_part_{}.csv'.format(split_idx + int(round(idx / split_len))))
        string_list, label_list, star_list = ([] for i in range(3))
