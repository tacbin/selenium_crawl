# This is a sample Python script.

# Press Alt+Shift+X to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import time

from selenium import webdriver

# Press the green button in the gutter to run the script.
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

if __name__ == '__main__':
    # 使用 fire_fox 的 WebDriver
    fire_fox_options = Options()
    # fire_fox_options.add_argument('--headless')
    browser = webdriver.Firefox(options=fire_fox_options)
    browser.get('https://www.zhipin.com/job_detail/?query=运营主管&city=101280600&source=8')
    time.sleep(2)

    # 用js获取页面的宽高，如果有其他需要用js的部分也可以用这个方法
    width = browser.execute_script("return document.documentElement.scrollWidth")
    height = browser.execute_script("return document.documentElement.scrollHeight")
    # 获取页面宽度及其宽度
    print(width, height)
    # 将浏览器的宽高设置成刚刚获取的宽高
    browser.set_window_size(width, height)
    print(browser.page_source)
    elements = browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')

    current_url = browser.current_url
    i = 0
    while len(elements) > 0:
        browser.get_screenshot_as_file(str(i) + '123.png')
        elements[0].click()
        if current_url == browser.current_url:
            break
        current_url = browser.current_url
        print(browser.page_source)
        elements = browser.find_elements(By.XPATH, '//div[@class="page"]/a[@ka="page-next"]')
        time.sleep(2)
        i += 1
    # 關閉瀏覽器
    browser.close()
