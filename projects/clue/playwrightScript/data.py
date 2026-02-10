import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://clue-dev.spreadwin.cn/welcome")
    page.get_by_text("本周").first.click()
    page.get_by_text("本月").first.click()
    page.get_by_text("安装数").click()
    page.get_by_text("本周").nth(1).click()
    page.get_by_text("本月").nth(2).click()
    page.locator(".ant-picker.ant-picker-borderless > .ant-picker-input").click()
    page.get_by_text("1月", exact=True).click()
    page.get_by_role("button", name="一年").click()
    page.get_by_role("button", name="所有").click()
    page.locator("div").filter(has_text=re.compile(r"^线索跟进情况$")).first.click()
    page.get_by_role("tab", name="事故线索").click()
    page.get_by_title("钉钉集团").nth(1).click()
