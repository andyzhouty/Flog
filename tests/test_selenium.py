import logging
import os
import unittest
from selenium import webdriver

class UITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.client = None
        try:
            os.environ['MOZ_HEADLESS'] = '1'
            self.client = webdriver.Firefox()
        except:
            pass

        # 只有启动无界面浏览器后才运行这些测试
        if self.client:
            self.url_prefix = 'http://localhost:5000'
            logging.disable(logging.CRITICAL)
        else:
            self.skipTest('Web browser not available')

        try:
            self.client.get(self.url_prefix)
        except:
            self.skipTest('App not running')

    def tearDown(self) -> None:
        if self.client:
            self.client.quit()

    def register(self, name, email, password) -> None:
        self.client.get(self.url_prefix + '/auth/register/')
        self.client.find_element_by_name('username').send_keys(name)
        self.client.find_element_by_name('name').send_keys(name)
        self.client.find_element_by_name('email').send_keys(email)
        self.client.find_element_by_name('password').send_keys(password)
        self.client.find_element_by_name('password_again').send_keys(password)
        self.client.find_element_by_name('submit').click()

    def login(self, email=os.getenv('ADMIN_EMAIL'), password=os.getenv('ADMIN_PASSWORD')) -> None:
        self.client.get(self.url_prefix + '/auth/login/')
        self.client.find_element_by_name('username_or_email').send_keys(email)
        self.client.find_element_by_name('password').send_keys(password)
        self.client.find_element_by_name('submit').click()

    def test_ui_home_page(self):
        self.client.get(self.url_prefix)
        self.assertIn('Join Now!', self.client.page_source)
        self.client.find_element_by_link_text('Join Now!').click()
        self.assertEqual(self.client.current_url, self.url_prefix + '/auth/login/')

    def test_ui_admin_login_logout(self):
        name = os.getenv('ADMIN_NAME')
        self.login()
        self.client.get(self.url_prefix)
        self.assertIn(f"Administrator {name}", self.client.page_source)
        self.client.find_element_by_id('account').click()
        self.client.find_element_by_id('logout').click()

    def test_ui_change_theme(self):
        self.client.find_element_by_link_text('Theme').click()
        self.client.find_element_by_link_text('Lite').click()
        self.assertEqual(self.client.get_cookie('theme')['value'], 'lite')

