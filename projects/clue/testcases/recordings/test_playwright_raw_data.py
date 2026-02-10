# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_playwright_raw_data.py
# @Software: PyCharm
# @Desc: 录制脚本原样执行适配用例（不改动原始脚本逻辑）

import pytest
from playwright.sync_api import Page
from config.global_vars import GLOBAL_VARS
from pages.login_page import LoginPage
from pages.recorded.welcome_recorded_page import WelcomeRecordedPage


@pytest.mark.recordings
def test_recorded_example_adapter(page: Page):
    """
    录制脚本适配器用例（使用框架封装方法复现）
    设计目的：
    - 不修改原始录制文件；在适配器中通过 BasePage 封装方法复现同样的交互
    - 统一断言与等待策略，提升稳定性与复用性
    """
    # 前置：登录系统
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login_on_page_flow(
        login=GLOBAL_VARS["admin_user_name"],
        password=GLOBAL_VARS["admin_user_password"]
    )
    # 使用框架封装方法复现录制脚本交互
    welcome = WelcomeRecordedPage(page)
    welcome.open_welcome()
    welcome.interact_filters()
    welcome.assert_welcome()
