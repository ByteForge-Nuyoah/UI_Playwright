# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : conftest.py
# @Software: PyCharm
# @Desc: TODO: Description

import os
import pytest
from playwright.sync_api import Browser
from loguru import logger
from config.global_vars import GLOBAL_VARS
from config.path_config import AUTH_DIR
from utils.base_utils.request_control import RequestControl

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERFACE_DIR = os.path.join(PROJECT_DIR, "interfaces")


@pytest.fixture(scope="session", autouse=True)
def reset_login_times(browser: Browser, pytestconfig):
    """
    会话级前置：在所有 UI 用例执行前，通过接口完成一次超级管理员登录。

    设计意图：
    1. 通过 API 登录，比逐条用例走 UI 登录更稳定、更高效。
    2. 将登录成功后的会话信息保存到 .auth/clue_state.json，后续如果需要，
       可以通过 Playwright 的 storage_state 机制直接复用该登录态，跳过登录页面。
    3. 登录请求相关的账号、登录类型等参数统一从 GLOBAL_VARS 中读取，
       保证不同环境（test/live）下只需调整配置文件即可复用。
    """
    logger.info("\n-------------- Start: 开启测试前的操作 ----------------")
    print(f"DEBUG: testcases conftest reset_login_times - GLOBAL_VARS: {GLOBAL_VARS}")
    # 超级管理远账号
    users = {
        "user_name": GLOBAL_VARS['admin_user_name'],
        "password": GLOBAL_VARS['admin_user_password'],
        "login_type": GLOBAL_VARS['login_type'],
        "uuid": GLOBAL_VARS['uuid'],
        "sms_state": GLOBAL_VARS['sms_state'],
    }

    # 手动创建一个新的 APIRequest 上下文实例，用于发送纯 API 请求
    api_base_url = GLOBAL_VARS.get("host")
    api_request_context = browser.new_context(base_url=api_base_url).request

    # 发送登录请求，api_request_context 会自动存储登录态，
    # 下一个请求会自动带上 Cookie / Token 等信息
    logger.info("\n-------------- Start: 登录 ----------------")
    try:
        RequestControl(api_request_context=api_request_context).api_request_flow(
            api_file_path=os.path.join(INTERFACE_DIR, "clue_login.yml"), key="clue_login", global_var=users)
        
        # 保存登录态到本地文件，方便后续 UI 测试复用（如果需要）
        auth_path = os.path.join(AUTH_DIR, "clue_state.json")
        api_request_context.storage_state(path=auth_path)
        logger.info(f"登录态已保存至: {auth_path}")

    except Exception as e:
        import traceback
        logger.error(f"登录前置接口调用失败，已跳过，错误：{e}")
        logger.error(traceback.format_exc())
