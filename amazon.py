from splinter.browser import Browser
from splinter.driver.webdriver.chrome import Options
from parameters import paras
from user_agent import generate_user_agent
import logging
import pymysql
import time
import random
import string


class Amazon(object):
    def __init__(self, keyword):
        self.url = "https://www.amazon.com"
        self.name = "".join(random.sample(string.ascii_letters + string.digits, 6))
        self.email = "".join(random.sample(string.ascii_letters + string.digits, 16)) + "@163.com"
        self.password = "".join(random.sample(string.ascii_letters + string.digits, 8))
        self.keyword = keyword
        self.chrome_options = Options()
        logging.basicConfig(filename='amazon.log', level=logging.DEBUG)
        self.conn = pymysql.connect(host='192.168.0.211', port=6033, user='third', password='third', db='amazon')
        self.cs = self.conn.cursor()
        self.cs.execute('select id,ip,port from register_proxy_ips where is_alived = 1 order by id desc limit 1')
        self.proxy_ip = self.cs.fetchone()
        self.cs.execute('update register_proxy_ips set is_alived = 0 where id = %s' % self.proxy_ip[0])
        self.conn.commit()
        logging.debug(self.proxy_ip)
        # self.chrome_options.add_argument('--proxy-server=http://{host}:{port}'.format(host=self.proxy_ip[1], port=self.proxy_ip[2]))
        self.browser = Browser('chrome', user_agent=generate_user_agent(device_type='desktop'))

    def run(self):
        self.acess()
        self.search_kw()
        i = 1
        while i < 7:
            ad_list = self.browser.find_by_xpath('//li[contains(@class, "AdHolder")]')
            if ad_list:
                ad_list[0].find_by_tag('h2').click()
                break
            else:
                time.sleep(300)
                self.search_kw()
                i += 1
        if i > 6:
            self.browser.quit()
        self.register()
        self.add_pay_method()
        self.add_address()
        self.buy_goods()
        self.add_list()

    def acess(self):
        self.browser.visit(self.url)
        logging.error("代理IP失效，请求不成功")

    def search_kw(self):
        self.browser.find_by_xpath('//input[@id="twotabsearchtextbox"]').first.fill(self.keyword)
        self.browser.find_by_xpath('//input[@value="Go"]').click()
        draggble = self.browser.find_by_xpath('//*[@id="searchTemplate"]')
        target = self.browser.find_by_xpath('//*[@id="footer"]')
        draggble.drag_and_drop(target)
        # time.sleep(random.randint(1, 6))

    def register(self):
        self.browser.find_by_xpath('//*[@id="nav-link-accountList"]').click()
        self.browser.find_by_xpath('//*[@id="createAccountSubmit"]').click()
        self.browser.find_by_xpath('//input[@id="ap_customer_name"]').first.fill(self.name)
        self.browser.find_by_xpath('//input[@id="ap_email"]').first.fill(self.email)
        self.browser.find_by_xpath('//input[@id="ap_password"]').first.fill(self.password)
        self.browser.find_by_xpath('//input[@id="ap_password_check"]').first.fill(self.password)
        self.browser.find_by_xpath('//input[@class="a-button-input"]').click()

    def add_pay_method(self):
        self.browser.find_by_xpath('//*[@id="nav-link-accountList"]').click()
        self.browser.find_by_xpath('//*[@id="a-page"]/div[3]/div/div[2]/div[2]/a/div').click()
        self.browser.fill('ppw-accountHolderName', paras['card_name'])
        self.browser.fill('addCreditCardNumber', paras['card_num'])
        self.browser.execute_script('document.getElementsByName("ppw-expirationDate_month")[0].style.display="block"')
        self.browser.execute_script('document.getElementsByName("ppw-expirationDate_year")[0].style.display="block"')
        self.browser.find_by_text('04').click()
        self.browser.find_by_text('2019').click()
        self.browser.find_by_name('ppw-widgetEvent:AddCreditCardEvent').click()

    def add_address(self):
        self.browser.fill('ppw-fullName', paras['fullname'])
        self.browser.fill('ppw-line1', paras['line'])
        self.browser.fill('ppw-city', paras['city'])
        self.browser.fill('ppw-stateOrRegion', paras['stateOrRegion'])
        self.browser.fill('ppw-postalCode', paras['postalCode'])
        self.browser.fill('ppw-phoneNumber', paras['phoneNumber'])
        self.browser.find_by_name('ppw-widgetEvent:AddAddressEvent').click()

    def buy_goods(self):
        self.browser.find_by_xpath('//*[@id="nav-recently-viewed"]').click()
        self.browser.find_by_xpath('//*[@id="asin_list"]/div[1]/div/a/div[1]/span/div').click()
        try:
            self.browser.find_by_xpath('//*[@id="add-to-cart-button"]').click()  # add cart
            self.browser.find_by_xpath('//*[@id="smartShelfAddToCartNative"]').click()
        except Exception as e:
            logging.error(e)
        try:
            time.sleep(5)
            self.browser.is_element_present_by_xpath('//i[@class="a-icon a-icon-close"]', wait_time=30)
            self.browser.find_by_xpath('//i[@class="a-icon a-icon-close"]').click()
        except Exception:
            pass
        try:
            self.browser.find_by_xpath('//a[@id="hlb-view-cart-announce"]').click()  # enter cart
        except Exception:
            pass
        self.browser.execute_script('document.getElementsByName("quantity")[0].style.display="block"')
        self.browser.find_by_value('10').click()
        self.browser.find_by_name('quantityBox').clear()
        self.browser.fill('quantityBox', 999)
        self.browser.find_by_xpath('//span[@id="a-autoid-1"]').click()
        self.browser.find_by_xpath('//div[@class="sc-proceed-to-checkout"]').click()
        self.browser.find_by_xpath('//*[@id="address-book-entry-0"]/div[2]/span/a').click()
        self.browser.find_by_xpath('//*[@id="shippingOptionFormId"]/div[3]/div/div/span[1]').click()
        self.browser.find_by_xpath('//*[@id="order-summary-container"]/div/div/div').click()
        try:
            self.browser.find_by_xpath('//a[contains(@class, "prime-nothanks-button")]').click()
        except Exception:
            pass
        self.browser.find_by_xpath('//span[contains(@class, "place-order-button-link")]').click()

    def add_list(self):
        self.browser.find_by_xpath('//*[@id="nav-recently-viewed"]').click()
        self.browser.find_by_xpath('//*[@id="asin_list"]/div[1]/div/a/div[1]/span/div').click()
        self.browser.find_by_xpath('//input[@title="Add to List"]').click()
        if self.browser.is_element_present_by_text('Add to your list', wait_time=10):
            self.browser.find_by_xpath('//*[@id="WLHUC_result"]/form/div[2]/span[3]/span').click()
            self.browser.find_by_xpath('//i[@class="a-icon a-icon-close"]').click()
        time.sleep(2)
        self.browser.quit()


if __name__ == '__main__':
    # while True:
    amazon = Amazon('pearls')
    amazon.run()