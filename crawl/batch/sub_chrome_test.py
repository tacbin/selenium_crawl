import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument('user-data-dir=C:\\selenium\\ChromeProfile')
chrome_driver = "E:\python-workspace\selenium_crawl\chromedriver.exe"
driver = webdriver.Chrome(chrome_driver, chrome_options=chrome_options)

#Print website title to make sure its connected properly
driver.get('https://google.com')
print(driver.title)

search_bar = driver.find_element_by_name('q')
search_bar.send_keys('test')

time.sleep(100)