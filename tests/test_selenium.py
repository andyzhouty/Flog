import logging
import os
import threading
from sealog.utils import slugify
import unittest
from selenium import webdriver
from sealog import create_app
from sealog.extensions import db
from sealog.models import Role, User
from sealog import fakes as fake

class SeleniumTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.client = None
        try:
            os.environ['MOZ_HEADLESS'] = '1'
            self.client = webdriver.Firefox()
        except:
            pass

        # 只有启动无界面浏览器后才运行这些测试
        if self.client:
            # 创建应用
            self.url_prefix = 'http://localhost:5000'
            logging.disable(logging.CRITICAL)

    def tearDown(self) -> None:
        if self.client:
            self.client.quit()

    def test_home_page(self):
        self.client.get(self.url_prefix)
        self.assertIn('Join Now!', self.client.page_source)
