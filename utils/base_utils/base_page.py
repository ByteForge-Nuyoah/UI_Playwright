# -*- coding: utf-8 -*-
# @Version: Python 3.13
# @Author  : 会飞的🐟
# @File    : base_page.py
# @Software: PyCharm
# @Desc: Playwright UI自动化基础操作封装

import os
import re
from typing import Union, Pattern, Optional, Literal, AnyStr
import allure
from loguru import logger
from playwright.sync_api import Page
from playwright.sync_api import expect


class BasePage:
    """
    Playwright UI自动化基础操作封装
    """

    def __init__(self, page: Page):
        self.page = page
        self.context = self.page.context
        self.pages = self.context.pages

    # --------------------------------- 导航 ---------------------------------#
    """
     • goto(url, **kwargs)：导航到指定的URL
     • go_back()：后退到浏览器历史记录中的上一页
     • go_forward()：前进到浏览器历史记录中的下一页
     • reload(**kwargs)：重新加载当前页面
    """

    @allure.step("--> 访问页面，路由：{url}，超时时间： {timeout} 秒")
    def visit(self, url: str, timeout=5) -> None:
        """
        访问页面
        :param url: url
        :param timeout: 超时时间，默认是50000ms
        """
        logger.info(f"--> 访问页面，路由：{url}")
        self.page.goto(url, timeout=timeout * 1000)
        self.wait_for_load_state()

    @allure.step("--> 刷新页面，且状态为：{state}， 超时时间： {timeout} 秒")
    def refresh(self, timeout=5,
                state: Optional[Literal["domcontentloaded", "load", "networkidle"]] = 'networkidle') -> None:
        """
        刷新页面
        :param timeout: 超时时间，默认是50000ms
        :param state: Optional[Literal["domcontentloaded", "load", "networkidle"]] = 'networkidle'
        官方默认是默认为 load， 该方法默认是networkidle
        state:
        domcontentloaded - 等到加载DOMContentLoaded事件
        load - 等到加载load事件
        networkidle - 等到500 ms没有网络请求
        """
        logger.info(f"--> 刷新页面，且状态为：{state}， 超时时间： {timeout} 秒")
        self.page.reload(timeout=timeout * 1000, wait_until=state)

    # --------------------------------- 等待 ---------------------------------#
    @allure.step("--> 强制等待{timeout}秒")
    def wait(self, timeout=3):
        """
        强制等待，官方默认单位是毫秒，这里的timeout传参默认单位是秒
        """
        logger.info(f'--> 强制等待{timeout}秒')
        self.page.wait_for_timeout(timeout * 1000)

    @allure.step("--> 等待页面加载，且状态为：{state}, 超时{timeout}秒")
    def wait_for_load_state(self,
                            state: Optional[Literal["domcontentloaded", "load", "networkidle"]] = 'networkidle',
                            timeout=30):
        """
        在页面达到所需的加载状态时返回
        官方默认的timeout单位是毫秒，这里timeout传参默认是秒
        官方默认是默认为 load， 该方法默认是networkidle
        state:
        domcontentloaded - 等到加载DOMContentLoaded事件
        load - 等到加载load事件
        networkidle - 等到500 ms没有网络请求
        """
        logger.info(f'--> 等待页面加载，且状态为:{state}')
        self.page.wait_for_load_state(state, timeout=timeout * 1000)

    # --------------------------------- 页面操作和交互---------------------------------#
    @allure.step("--> 点击元素 | 元素定位：{locator}")
    def click(self, locator: str) -> None:
        """
        点击操作封装
        封装目的：
        1. 统一添加日志记录，方便调试
        2. 统一添加异常处理，捕获点击失败的情况
        3. 集成 Allure 步骤装饰器，使报告更清晰
        
        :param locator: 元素定位 (xpath, css, id 等)
        """
        try:
            logger.info(f"--> 点击元素 | 元素定位：{locator}")
            self.page.click(locator)
        except Exception as e:
            logger.error(f"--> 点击元素 | 元素定位：{locator}，报错：{e}")
            raise Exception(f"--> 点击元素 | 元素定位：{locator}，报错：{e}")

    @allure.step("--> checkbox勾选元素 | 元素定位： {locator}")
    def check(self, locator: str) -> None:
        """
        勾选checkbox
        注意：仅适用于 input[type=checkbox] 或 input[type=radio] 元素
        :param locator: 元素定位
        """
        logger.info(f"--> checkbox勾选元素 | 元素定位：{locator}")
        self.page.check(locator)

    @allure.step("--> checkbox取消勾选元素 | 元素定位： {locator}")
    def uncheck(self, locator: str) -> None:
        """
        取消勾选checkbox
        :param locator: 元素定位
        """
        logger.info(f"--> checkbox取消勾选元素 | 元素定位： {locator}")
        self.page.uncheck(locator)

    @allure.step("--> 鼠标悬浮在元素上，元素定位： {locator}")
    def hover(self, locator: str) -> None:
        """
        悬浮在某元素上
        场景：触发下拉菜单、显示提示信息等
        :param locator: 元素定位
        """
        logger.info(f"--> 鼠标悬浮在元素上，元素定位： {locator}")
        self.page.hover(locator)

    @allure.step("--> 聚焦定位元素，元素定位： {locator}")
    def focus(self, locator):
        """ 聚焦定位元素，通常用于触发输入框的 focus 事件 """
        logger.debug(f'--> 聚焦定位元素，元素定位： {locator}')
        self.page.focus(locator)

    @allure.step("--> 输入内容： {text} | 元素定位： {locator}")
    def input(self, locator: str, text: str) -> None:
        """
        输入内容封装 (fill)
        注意：fill 会直接填充内容，而不是模拟逐字输入 (不同于 type)
        适用于大多数表单输入场景，速度较快
        
        :param locator: 元素定位
        :param text: 输入的内容
        """
        try:
            logger.info(f"--> 输入内容： {text} | 元素定位： {locator}")
            self.page.fill(selector=locator, value=text)
        except Exception as e:
            logger.error(f"--> 输入内容： {text} | 元素定位： {locator}， 报错：{e}")
            raise Exception(f"--> 输入内容： {text} | 元素定位： {locator}， 报错：{e}")

    @allure.step("--> 键盘键入内容： {text} | 元素定位： {locator}")
    def type(self, locator: str, text: str) -> None:
        """
        模拟键盘输入 (type)
        一个字符一个字符的输入，模拟真实用户键盘操作
        场景：某些输入框绑定了 keypress/keyup 事件，必须用 type 才能触发
        
        :param locator: 元素定位
        :param text: 输入的内容
        """
        logger.info(f"--> 键盘键入内容： {text} | 元素定位： {locator}")
        self.page.type(selector=locator, text=text)

    @allure.step("--> 清除元素内容，元素定位： {locator}")
    def clear(self, locator: str):
        self.page.locator(locator).click()
        try:
            logger.info(f'--> 清除元素内容，元素定位： {locator}')
            self.page.locator(locator).clear()
        except Exception as e:
            logger.error(f'ERROR-->清除失败：{e}')

    @allure.step("--> 选择选项： {option} | 元素定位： {locator}")
    def select_option(self, locator: str, option: str) -> None:
        """
        选择option
        :param locator: 元素定位
        :param option: 选项内容
        """
        logger.info(f"--> 选择选项： {option} | 元素定位： {locator}")
        self.page.select_option(selector=locator, value=option)

    @allure.step("--> 上传文件： {file_path} | 元素定位： {locator}")
    def upload_file(self, locator: str, file_path: str) -> None:
        """
        上传文件
        :param locator: 元素定位
        :param file_path: 文件路径
        """
        if os.path.isfile(file_path):
            logger.info(f"--> 上传文件： {file_path} | 元素定位： {locator}")
            allure.attach.file(file_path, name=file_path)
            self.page.set_input_files(selector=locator, files=file_path)
            self.wait(timeout=1)
        else:
            logger.error(f"ERROR --> 上传文件失败，附件未找到，请检查{file_path}下是否存在该文件")
            raise ValueError(f"--> 上传文件失败，附件未找到，请检查{file_path}下是否存在该文件")



    @allure.step("--> 执行js脚本： {js}, 可选参数：{args}")
    def execute_js(self, js, *args) -> None:
        """
        执行javascript脚本
        :param js: javascript脚本
        """
        logger.info(f"--> 执行js脚本： {js}, 可选参数：{args}")
        self.page.evaluate(js, *args)

    @allure.step("--> 按{keyboard}键 | 元素定位： {locator}")
    def press(self, locator: str, keyboard: str) -> None:
        """
        :param locator: 元素定位
        :param keyboard: 键
        """
        logger.info(f"--> 按{keyboard}键 | 元素定位： {locator}")
        self.page.press(locator, keyboard)

    @allure.step("--> 截图， 全屏={full_page} | 元素定位： {locator}， 图片保存路径：{path}")
    def screenshot(self, path, full_page=True, locator=None):
        """截图功能，默认截取全屏，如果传入定位器表示截取元素"""
        if locator is not None:
            logger.info(f"--> 截图， 全屏={full_page} | 元素定位： {locator}， 图片保存路径：{path}")
            self.page.locator(locator).screenshot(path=path)
            return path
        logger.info(f"--> 截图， 全屏={full_page} | 元素定位： {locator}， 图片保存路径：{path}")
        self.page.screenshot(path=path, full_page=full_page)
        allure.attach.file(path, name=path)
        return path

    # --------------------------------- UI断言 ---------------------------------#
    @allure.step("--> 断言 | 验证元素包含文本：{text} | 元素定位：{locator}")
    def assert_text_contains(self, locator: str, text: str, timeout: int = 5000) -> None:
        """
        断言元素包含指定文本
        :param locator: 元素定位
        :param text: 期望包含的文本
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证元素包含文本：{text} | 元素定位：{locator}")
            expect(self.page.locator(locator)).to_contain_text(text, timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 元素 {locator} 未包含文本 {text}")
            raise e

    @allure.step("--> 断言 | 验证元素文本等于：{text} | 元素定位：{locator}")
    def assert_text_equals(self, locator: str, text: str, timeout: int = 5000) -> None:
        """
        断言元素文本完全等于指定文本
        :param locator: 元素定位
        :param text: 期望的文本
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证元素文本等于：{text} | 元素定位：{locator}")
            expect(self.page.locator(locator)).to_have_text(text, timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 元素 {locator} 文本不等于 {text}")
            raise e

    @allure.step("--> 断言 | 验证元素可见 | 元素定位：{locator}")
    def assert_element_visible(self, locator: str, timeout: int = 5000) -> None:
        """
        断言元素可见
        :param locator: 元素定位
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证元素可见 | 元素定位：{locator}")
            expect(self.page.locator(locator)).to_be_visible(timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 元素 {locator} 不可见")
            raise e

    @allure.step("--> 断言 | 验证元素不可见 | 元素定位：{locator}")
    def assert_element_hidden(self, locator: str, timeout: int = 5000) -> None:
        """
        断言元素不可见
        :param locator: 元素定位
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证元素不可见 | 元素定位：{locator}")
            expect(self.page.locator(locator)).to_be_hidden(timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 元素 {locator} 居然可见了")
            raise e

    @allure.step("--> 断言 | 验证页面URL包含：{url}")
    def assert_url_contains(self, url: str, timeout: int = 5000) -> None:
        """
        断言当前URL包含指定字符串
        :param url: 期望包含的URL片段
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证页面URL包含：{url}")
            expect(self.page).to_have_url(re.compile(url), timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 当前URL不包含 {url}")
            raise e

    @allure.step("--> 断言 | 验证页面标题包含：{title}")
    def assert_title_contains(self, title: str, timeout: int = 5000) -> None:
        """
        断言页面标题包含指定字符串
        :param title: 期望包含的标题片段
        :param timeout: 超时时间(ms)
        """
        try:
            logger.info(f"--> 断言 | 验证页面标题包含：{title}")
            expect(self.page).to_have_title(re.compile(title), timeout=timeout)
        except Exception as e:
            logger.error(f"断言失败 | 当前标题不包含 {title}")
            raise e

    # --------------------------------- 页面元素定位 ---------------------------------#

    @allure.step("--> 获取所有的元素 | 元素定位：{locator}")
    def get_all_elements(self, locator: str) -> Union[list, None]:
        """
        获取所有符合定位的元素
        :param locator: 元素定位
        :return: 元素/None
        """
        try:
            logger.info(f"--> 获取所有的元素 | 元素定位： {locator}")
            elems = self.page.query_selector_all(locator)
            allure.attach(str(elems), name="elems", attachment_type=allure.attachment_type.TEXT)
            logger.success(f"--> 获取到的元素：{elems}")
            return elems
        except Exception as e:
            logger.error(f"ERROR --> 获取所有的元素失败 | 元素定位： {locator}，报错信息：{e} ")
            raise e

    @allure.step("--> 获取元素文本值 | 元素定位： {locator}")
    def get_text(self, locator: str) -> Union[str, None]:

        """
        获取元素的文本内容
        :param locator: 元素定位
        :return: 文本值/None
        """
        try:
            logger.info(f"--> 获取元素文本值 | 元素定位： {locator}")
            text_value = self.page.locator(locator).text_content()
            logger.success(f"--> 获取到的文本值： {text_value}")
            allure.attach(text_value, name="text_value", attachment_type=allure.attachment_type.TEXT)
            return text_value
        except Exception as e:
            logger.error(f"ERROR --> 获取元素文本值 | 元素定位： {locator}，报错信息：{e} ")
            raise e

    @allure.step("--> 获取所有符合定位要求的元素的文本内容 | 元素定位： {locator}")
    def get_all_elements_text(self, locator) -> Union[list, None]:
        """
        获取所有符合定位要求的元素的文本内容
        :param locator: 元素定位
        :return: 文本值/None
        """
        try:
            logger.info(f"--> 获取所有符合定位要求的元素的文本内容 | 元素定位： {locator}")
            elements = self.get_all_elements(locator)
            elems_text = [element.text_content() for element in elements]
            logger.success(f"--> 获取所有符合定位要求的元素的文本内容：{elems_text}")
            allure.attach(str(elems_text), name="elems_text", attachment_type=allure.attachment_type.TEXT)
            return elems_text
        except Exception as e:
            logger.error(f"ERROR --> 获取所有符合定位要求的元素的文本内容 | 元素定位： {locator}，报错信息：{e} ")
            raise e

    @allure.step("--> 根据元素的属性获取对应属性值 | 元素定位： {locator}, 属性名称：{attr_name}")
    def get_element_attribute(self, locator: str, attr_name: str) -> Union[str, None]:
        """
        获取元素属性值
        :param locator: 元素定位
        :param attr_name: 属性名称
        :return: 元素属性值
        """
        try:
            logger.info(f"--> 根据元素的属性获取对应属性值 | 元素定位： {locator}, 属性名称：{attr_name}")
            attr_value = self.page.locator(locator).get_attribute(name=attr_name)
            logger.success(f"--> 获取到的属性值：{attr_value}")
            allure.attach(attr_value, name="attr_value", attachment_type=allure.attachment_type.TEXT)
            return attr_value
        except Exception as e:
            logger.error(f"--> 获取元素属性值 | 元素定位： {locator}，报错信息：{e} ")
            return None

    @allure.step("--> 获取元素的文本内容 | 元素定位： {locator}")
    def get_inner_text(self, locator: str) -> Union[str, None]:
        """
        获取元素的文本内容
        :param locator: 元素定位
        :return: 内部文本值
        """
        try:
            logger.info(f"--> 获取元素的文本内容 | 元素定位： {locator}")
            text_value = self.page.inner_text(selector=locator)
            logger.success(f"--> 获取到的元素文本内容：{text_value}")
            allure.attach(text_value, name="text_value", attachment_type=allure.attachment_type.TEXT)
            return text_value
        except Exception as e:
            logger.error(f"ERROR-->获取元素的文本内容 | 元素定位： {locator}，报错信息：{e} ")
            return None

    @allure.step("--> 获取元素的整个html源码内容 | 元素定位： {locator}")
    def get_inner_html(self, locator: str) -> Union[str, None]:
        """
        获取元素的整个html源码内容
        :param locator: 元素定位
        :return: html值
        """
        try:
            logger.info(f"--> 获取元素的整个html源码内容 | 元素定位： {locator}")
            html_value = self.page.inner_html(selector=locator)
            logger.success(f"--> 获取元素的整个html值：{html_value}")
            allure.attach(html_value, name="html_value", attachment_type=allure.attachment_type.TEXT)
            return html_value
        except Exception as e:
            logger.error(f"ERROR-->获取元素的整个html源码内容 | 元素定位： {locator}，报错信息：{e} ")
            return None

    @allure.step("获取当前页面的url")
    def get_page_url(self) -> AnyStr:
        """
        获取当前页面的url
        :return: url值
        """
        try:
            logger.info(f"--> 获取当前页面的url")
            url_value = self.page.url
            allure.attach(url_value, name="URL Value", attachment_type=allure.attachment_type.TEXT)
            logger.success(f"--> 获取到的url值：{url_value}")
            return url_value
        except Exception as e:
            logger.error(f"ERROR --> 获取当前页面的url，报错信息：{e} ")
            return None

    # --------------------------------- 断言（页面断言） ---------------------------------#
    """
    主要有四个断言方法
        • to_have_title 确保页面具有给定的标题 
        • not_to_have_title  确保页面不具有给定的标题 
        • to_have_url 确保页面导航到给定的URL
        • not_to_have_url 确保页面没有导航到给定的URL
    """

    # --------------------------------- 断言（常用的断言方法） ---------------------------------#
    """
    expect(locator).to_be_checked()	Checkbox is checked
    expect(locator).to_be_disabled()	Element is disabled
    expect(locator).to_be_editable()	Element is enabled
    expect(locator).to_be_empty()	Container is empty
    expect(locator).to_be_enabled()	Element is enabled
    expect(locator).to_be_focused()	Element is focused
    expect(locator).to_be_hidden()	Element is not visible
    expect(locator).to_be_visible()	Element is visible
    expect(locator).to_contain_text()	Element contains text
    expect(locator).to_have_attribute()	Element has a DOM attribute
    expect(locator).to_have_class()	Element has a class property
    expect(locator).to_have_count()	List has exact number of children
    expect(locator).to_have_css()	Element has CSS property
    expect(locator).to_have_id()	Element has an ID
    expect(locator).to_have_js_property()	Element has a JavaScript property
    expect(locator).to_have_text()	Element matches text
    expect(locator).to_have_value()	Input has a value
    expect(locator).to_have_values()	Select has options selected
    expect(page).to_have_title()	Page has a title
    expect(page).to_have_url()	Page has a URL
    expect(api_response).to_be_ok()	Response has an OK status
    """

    @allure.step("--> 断言 | 验证元素checkbox被选中 | 元素定位： {locator}")
    def is_checkbox_checked(self, locator: str) -> None:
        """
        断言：验证复选框是否被选中
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证元素checkbox被选中 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_checked()

    @allure.step("--> 断言 | 验证元素被禁用 | 元素定位： {locator}")
    def is_element_disabled(self, locator: str) -> None:
        """
        断言：验证元素是否被禁用
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证元素被禁用 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_disabled()

    @allure.step("--> 断言 | 验证输入框可编辑 | 元素定位： {locator}")
    def is_input_editable(self, locator: str, timeout=5) -> None:
        """
        断言：验证输入框是否可编辑
        :param locator: 元素定位
        :param timeout: 超时时间， 默认5000ms
        """
        logger.info(f"--> 断言 | 验证输入框可编辑 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_editable(timeout=timeout * 1000)

    @allure.step("--> 断言 | 验证容器为空 | 元素定位： {locator}")
    def is_container_empty(self, locator: str) -> None:
        """
        断言：验证容器是否为空
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证容器为空 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_empty()

    @allure.step("--> 断言 | 验证元素为启用状态 | 元素定位： {locator}")
    def is_element_enabled(self, locator: str) -> None:
        """
        断言：验证元素是否启用
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证元素为启用状态 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_enabled()

    @allure.step("--> 断言 | 验证元素获得焦点 | 元素定位： {locator}")
    def is_element_focused(self, locator: str) -> None:
        """
        断言：验证元素是否获得焦点
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证元素获得焦点 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_focused()

    @allure.step("--> 断言 | 验证元素被隐藏 | 元素定位： {locator}")
    def is_element_hidden(self, locator: str) -> None:
        """
        断言：验证元素是否隐藏
        :param locator: 元素定位
        """
        logger.info(f"--> 断言 | 验证元素被隐藏 | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_be_hidden()

    @allure.step("--> 断言 | 验证输入框具有值(预期)： {value} | 元素定位： {locator}")
    def is_input_have_value(self, locator: str, value: str, timeout=5) -> None:
        """
        断言：验证输入框是否具有指定的值
        :param locator: 元素定位
        :param value: 指定值
        :param timeout: 超时时间， 默认5000ms
        """
        logger.info(f"--> 断言 | 验证元素具有值(预期)： {value} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_value(value=value, timeout=timeout * 1000)

    @allure.step("--> 断言 | 验证输入框不具有值(预期)： {value} | 元素定位： {locator}")
    def is_input_not_have_value(self, locator: str, value: str, timeout=5) -> None:
        """
        断言：验证输入框是否具有指定的值
        :param locator: 元素定位
        :param value: 指定值
        :param timeout: 超时时间， 默认5000ms
        """
        logger.info(f"--> 断言 | 验证元素具有值(预期)： {value} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).not_to_have_value(value=value, timeout=timeout * 1000)

    @allure.step("--> 断言 | 验证元素具有： {text} | 元素定位： {locator}")
    def have_text(self, locator: str, text: str) -> None:
        """
        断言：验证元素是否具有指定的文本内容
        :param locator: 元素定位
        :param text: 文本内容
        """
        logger.info(f"--> 断言 | 验证元素具有： {text} | 元素定位： {locator}")
        expect(self.page.locator(locator)).to_have_text(text)

    @allure.step("--> 断言 | 验证元素包含： {text} | 元素定位： {locator}")
    def contain_text(self, locator: str, text: str) -> None:
        """
        断言：验证元素是否包含指定的文本
        :param locator: 元素定位
        :param text: 文本内容
        """
        logger.info(f"--> 断言 | 验证元素包含： {text} | 元素定位： {locator}")
        expect(self.page.locator(locator)).to_contain_text(text)

    @allure.step("---> 断言 | 验证元素具有类属性(预期)： {class_name} | 元素定位： {locator}")
    def is_element_have_class(self, locator: str, class_name: str) -> None:
        """
        断言：验证元素是否具有指定的类属性
        :param locator: 元素定位
        :param class_name: 预期类名称
        """
        logger.info(f"---> 断言 | 验证元素具有类属性(预期)： {class_name} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_class(class_name)

    @allure.step("--> 断言 | 验证元素具有属性(预期)： {attr_name} | 元素定位： {locator}")
    def is_element_have_attr(self, locator: str, attr_name: str) -> None:
        """
        断言：验证元素是否具有指定的属性
        :param locator: 元素定位
        :param attr_name: 预期元素属性名称
        """
        logger.info(f"--> 断言 | 验证元素具有属性(预期)： {attr_name} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_attribute(attr_name)

    @allure.step("---> 断言 | 验证元素具有指定个数(预期)： {elem_count} | 元素定位： {locator}")
    def is_element_count(self, locator: str, elem_count: int) -> None:
        """
        断言：验证元素个数是否与期望值相等
        :param locator: 元素定位
        :param elem_count: 预期元素个数
        """
        logger.info(f"---> 断言 | 验证元素具有指定个数(预期)： {elem_count} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_count(elem_count)

    @allure.step("---> 断言 | 验证元素具有CSS属性(预期)： {css_value} | 元素定位： {locator}")
    def is_element_have_css(self, locator: str, css_value: Union[str, Pattern[str]]) -> None:
        """
        断言：验证元素个数是否与期望值相等
        :param locator: 元素定位
        :param css_value: css属性，接收str以及正则表达式， 例如"button"， 或者"display", "flex"
        """
        logger.info(f"---> 断言 | 验证元素具有CSS属性(预期)： {css_value} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_css(css_value)

    @allure.step("---> 断言 | 验证元素具有ID(预期)： {id_name} | 元素定位： {locator}")
    def is_element_have_id(self, locator: str, id_name: str) -> None:
        """
        断言：验证元素是否具有指定的ID
        :param locator: 元素定位
        :param id_name: 元素id属性
        """
        logger.info(f"---> 断言 | 验证元素具有ID(预期)： {id_name} | 元素定位： {locator}")
        elem = self.page.locator(locator)
        expect(elem).to_have_css(id_name)

    @allure.step("---> 断言 | 验证元素具有JavaScript属性(预期)： {js_value} | 元素定位： {locator}")
    def is_element_have_js_property(self, locator: str, js_value: str) -> None:
        """
        断言：用于验证元素是否具有指定的JavaScript属性
        :param locator: 元素定位
        :param js_value: 元素id属性
        """
        logger.info(f"---> 断言 | 验证元素具有JavaScript属性(预期)： {js_value} | 元素定位： {locator}")
        expect(locator).to_have_js_property(js_value)

    # --------------------------------- 断言（自定义） ---------------------------------#
    @allure.step("--> 断言 | 验证元素的属性 {attr_name} 具有值(预期)： {value} | 元素定位： {locator}")
    def is_element_attr_have_value(self, locator: str, attr_name: str, value: str) -> None:
        """
        断言：验证元素的某个属性具有指定的值
        :param locator: 元素定位
        :param attr_name: 元素属性名称
        :param value: 文本内容
        """
        logger.info(f"--> 断言 | 验证元素的属性 {attr_name} 具有值(预期)： {value} | 元素定位： {locator}")
        actual_value = self.get_element_attribute(locator=locator, attr_name=attr_name)
        logger.info(f"--> 验证元素的属性 {attr_name} 实际值： {actual_value}")
        assert value == actual_value

    # --------------------------------- 断言（判断页面元素状态checkbox和radio） ---------------------------------#
    """
    page对象调用的判断方法, 传一个selector 定位参数
        • page.is_checked(selector: str) # checkbox or radio 是否选中
        • page.is_disabled(selector: str) # 元素是否可以点击或编辑
        • page.is_editable(selector: str) # 元素是否可以编辑
        • page.is_enabled(selector: str) # 是否可以操作
        • page.is_hidden(selector: str) # 是否隐藏
        • page.is_visible(selector: str) # 是否可见
        
    locator 对象调用的判断方法
        • locator.is_checked()
        • locator.is_disabled()
        • locator.is_editable()
        • locator.is_enabled()
        • locator.is_hidden()
        • locator.is_visible()
    元素句柄 的判断方法
        • element_handle.is_checked()
        • element_handle.is_disabled()
        • element_handle.is_editable()
        • element_handle.is_enabled()
        • element_handle.is_hidden()
        • element_handle.is_visible()
    """
