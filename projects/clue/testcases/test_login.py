# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : test_login.py
# @Software: PyCharm
# @Desc: TODO: Description

import pytest
import os
from loguru import logger
from playwright.sync_api import Page
from pages.login_page import LoginPage
from utils.files_utils.yaml_handle import YamlHandle


@pytest.mark.login
class TestLogin:
    """登录"""
    # 动态获取yaml数据文件路径
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "login_data.yaml")
    cases = YamlHandle(data_path).read_yaml

    @pytest.fixture(autouse=True)
    def setup_teardown_for_each(self, page: Page):
        logger.info("\n\n---------------Start: 开始测试-------------")
        self.login_page = LoginPage(page)
        self.login_page.navigate()
        yield
        # 清除登录cookies，避免影响其他登录用例
        page.context.clear_cookies()


    @pytest.mark.parametrize("case", cases["login_cases"], ids=lambda x: x["title"])
    def test_login_user(self, case):
        """
        网页登录：根据用例标题判断期望结果（成功或失败）
        - 标题包含“成功”：断言跳转到 /welcome
        - 标题包含“失败”：断言停留在 /user/login
        """
        login = case.get("login")
        password = case.get("password")
        # 登录页面，输入用户名及密码，点击【登录】按钮，提交登录表单
        self.login_page.login_on_page_flow(login=login, password=password)
        title = case.get("title", "")
        if "成功" in title:
            self.login_page.assert_url_contains(url="/welcome")
        else:
            self.login_page.assert_url_contains(url="/user/login")
