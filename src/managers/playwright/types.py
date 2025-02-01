from enum import Enum
from typing import TypedDict
from typing_extensions import NotRequired

from patchright.async_api import Page


class BaseProps(TypedDict):
    page: Page
    locator: str


class ClickProps(BaseProps):
    is_required: NotRequired[bool]
    max_attempts: NotRequired[int]
    wait_before_action: NotRequired[int]
    delay_to_wait_element: NotRequired[int]
    delay_between_attempts: NotRequired[int]
    show_attempt_log: NotRequired[bool]
    click_count: NotRequired[int]


class ClickByCordsProps(ClickProps):
    offset_x: NotRequired[int]
    offset_y: NotRequired[int]


class GetElementProps(BaseProps):
    is_required: NotRequired[bool]
    max_attempts: NotRequired[int]
    wait_before_action: NotRequired[int]
    delay_to_wait_element: NotRequired[int]
    delay_between_attempts: NotRequired[int]
    show_attempt_log: NotRequired[bool]


class GetElementAttributeProps(BaseProps):
    attribute: str


class ClickOnElementOptions(TypedDict):
    is_required: NotRequired[bool]
    max_attempts: NotRequired[int]
    wait_time: NotRequired[int]


class TypeInInputOptions(TypedDict):
    is_required: NotRequired[bool]
    wait_time: NotRequired[int]
    page: Page
    locator: str
    text: str
