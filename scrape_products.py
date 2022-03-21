from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
import pickle

options = ChromeOptions()
options.add_argument("--log-level=3")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options, headless=False, use_subprocess=True)
driver.get('https://www.g2.com/products/asana/reviews?page=2')

cookies = pickle.load(open("cookies.pkl", "rb"))
for cookie in cookies:
    driver.add_cookie(cookie)

# sleep(30)
# print("saving cookies...")
# pickle.dump(driver.get_cookies() , open("cookies.pkl", "wb"))

product_links = []

for page in range(1, 15):
    driver.get('https://www.g2.com/categories/project-management?order=popular&page={}'.format(page))
    # get Xpath of the product frame
    test_path = \
        '/html/body/div[1]/div/div/div[1]/div/div[4]/div[2]/div/div/div[1]/div[1]/div[2]' \
        '/div[@class="paper pt-half pb-0 my-1 x-ordered-events-initialized"]'
    js = "var q=document.documentElement.scrollTop=100000"
    driver.execute_script(js)
    product_list = driver.find_elements(by=By.XPATH, value=test_path)

    for product in product_list:
        product_link = product.find_element(by=By.XPATH, value="./div/div[1]/div/div/div[1]/a")
        product_links.append(product_link.get_attribute('href'))

print(product_links)
with open('product_links.pkl', 'wb') as fp:
    pickle.dump(product_links, fp)

