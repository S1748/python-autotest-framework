"""YAML `${func(args)}` 占位符替换测试。

对应 `base/apiutil.py` 的 `RequestBase.replace_load`。
这里只覆盖不依赖接口返回值的替换场景（加密、时间戳这类纯函数）。
涉及 `get_extract_data` 的场景需要先有接口把值写进 extract.yaml，属于集成测试范畴。
"""
import hashlib
import re

from base.apiutil import RequestBase


class TestReplaceLoad:
    def setup_method(self):
        self.req = RequestBase()

    def test_no_placeholder_returns_original_string(self):
        assert self.req.replace_load('/coupApply/cms/goodsList') == '/coupApply/cms/goodsList'

    def test_single_placeholder_in_string(self):
        result = self.req.replace_load('${md5_encryption(abc)}')
        assert result == hashlib.md5(b'abc').hexdigest()

    def test_placeholder_inside_dict_is_restored_to_dict(self):
        result = self.req.replace_load({'passwd': '${md5_encryption(abc)}', 'user_name': 'test01'})
        assert isinstance(result, dict)
        assert result['user_name'] == 'test01'
        assert result['passwd'] == hashlib.md5(b'abc').hexdigest()

    def test_placeholder_without_args(self):
        result = self.req.replace_load({'ts': '${timestamp()}'})
        assert re.fullmatch(r'\d{10}', result['ts'])

    def test_placeholder_inside_nested_structure(self):
        result = self.req.replace_load({'outer': {'inner': '${md5_encryption(abc)}'}})
        assert result['outer']['inner'] == hashlib.md5(b'abc').hexdigest()

    def test_same_placeholder_is_replaced_once_for_all_occurrences(self):
        """同一个占位符出现多次时，会被 str.replace 一次性全部替换为同一个值。

        这是当前实现的既定行为（`replace_load` 内部用 `str.replace` 做全局替换）。
        如果需要两个位置取到不同的值，应改用 `get_extract_data(key, 1)` /
        `get_extract_data(key, 2)` 这种带序号的写法分别取值。
        """
        result = self.req.replace_load({'a': '${timestamp()}', 'b': '${timestamp()}'})
        assert result['a'] == result['b']
