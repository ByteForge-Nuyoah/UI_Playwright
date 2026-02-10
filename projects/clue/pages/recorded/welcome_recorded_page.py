# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : welcome_recorded_page.py
# @Software: PyCharm
# @Desc: 使用框架封装方法复现录制脚本的欢迎页交互

from utils.base_utils.base_page import BasePage


class WelcomeRecordedPage(BasePage):
    def open_welcome(self):
        """
        打开欢迎页
        """
        self.visit("/welcome")
        self.wait_for_load_state()

    def interact_filters(self):
        """
        执行录制脚本中的筛选交互：本周→本月→安装数→日期选择（1月）→一年→所有→切换到“线索跟进情况”→“事故线索”
        """
        self.click("text=本周")
        self.click("text=本月")
        self.click("text=安装数")
        self.click(".ant-picker.ant-picker-borderless > .ant-picker-input")
        self.wait(1)
        # 1月在某些视图下可能不存在或不可见，失败时跳过该步骤
        try:
            self.click('text="1月"')
        except Exception:
            pass
        self.click('role=button[name="一年"]')
        self.click('role=button[name="所有"]')
        self.click("text=线索跟进情况")
        self.click('role=tab[name="事故线索"]')

    def assert_welcome(self):
        """
        断言当前仍在欢迎页
        """
        self.wait(1)
        self.assert_url_contains("/welcome")
