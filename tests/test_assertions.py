"""断言模式测试。

对应 `common/assertions.py`，覆盖框架支持的五种断言：
contains / eq / ne / rv / db（db 需要连数据库，这里不覆盖）。
返回值为 0 表示通过，非 0 表示该条断言不通过。
"""
import pytest

from common.assertions import Assertions

RESPONSE = {
    'error_code': '0000',
    'msg': '登录成功',
    'result': {'userId': '2104664816080587359', 'isAdmin': False},
}


class TestContainsAssert:
    def setup_method(self):
        self.a = Assertions()

    def test_status_code_pass(self):
        assert self.a.contains_assert({'status_code': 200}, RESPONSE, 200) == 0

    def test_status_code_fail(self):
        assert self.a.contains_assert({'status_code': 500}, RESPONSE, 200) == 1

    def test_string_contains_pass(self):
        assert self.a.contains_assert({'error_code': '0000'}, RESPONSE, 200) == 0

    def test_string_contains_fail(self):
        assert self.a.contains_assert({'error_code': '9999'}, RESPONSE, 200) == 1

    def test_nested_field_contains_pass(self):
        assert self.a.contains_assert({'userId': '2104664816080587359'}, RESPONSE, 200) == 0


class TestEqualAssert:
    def setup_method(self):
        self.a = Assertions()

    def test_equal_pass(self):
        assert self.a.equal_assert({'msg': '登录成功'}, RESPONSE) == 0

    def test_equal_fail(self):
        assert self.a.equal_assert({'msg': '登录失败'}, RESPONSE) == 1

    def test_non_dict_raises_type_error(self):
        with pytest.raises(TypeError):
            self.a.equal_assert(['msg'], RESPONSE)


class TestNotEqualAssert:
    def setup_method(self):
        self.a = Assertions()

    def test_not_equal_pass(self):
        assert self.a.not_equal_assert({'msg': '登录失败'}, RESPONSE) == 0

    def test_not_equal_fail(self):
        assert self.a.not_equal_assert({'msg': '登录成功'}, RESPONSE) == 1


class TestResponseAnyAssert:
    def setup_method(self):
        self.a = Assertions()

    def test_top_level_field_pass(self):
        assert self.a.assert_response_any(RESPONSE, {'msg': '登录成功'}) == 0

    def test_top_level_field_fail(self):
        assert self.a.assert_response_any(RESPONSE, {'msg': '登录失败'}) == 1

    def test_missing_key_pass_because_not_checked(self):
        """期望字段在实际响应里不存在时，当前实现直接判定通过。

        调用方式为 assert_response_any(actual_results, expected_results)，
        内部只做 `if exp_key in actual_results` 判断，不存在时不会累加失败标记。
        写 YAML 时字段名写错不会被发现，需要注意。
        """
        assert self.a.assert_response_any(RESPONSE, {'no_such_key': 'x'}) == 0


class TestAssertResultDispatcher:
    def setup_method(self):
        self.a = Assertions()

    def test_all_assertions_pass(self):
        validation = [
            {'contains': {'status_code': 200}},
            {'contains': {'error_code': '0000'}},
            {'eq': {'msg': '登录成功'}},
            {'ne': {'msg': '登录失败'}},
            {'rv': {'msg': '登录成功'}},
        ]
        # 全部通过时不应抛异常
        self.a.assert_result(validation, RESPONSE, 200)

    def test_any_assertion_fail_raises(self):
        validation = [
            {'contains': {'status_code': 200}},
            {'eq': {'msg': '登录失败'}},
        ]
        with pytest.raises(AssertionError):
            self.a.assert_result(validation, RESPONSE, 200)

    def test_unsupported_mode_silently_passes(self):
        """断言模式写错时，当前实现只打一条 error 日志，用例仍然判定通过。

        `assert_result` 里 else 分支只调用 `logs.error("不支持此种断言方式")`，
        不累加 all_flag，最后 all_flag 仍为 0 -> assert True。
        也就是说 YAML 里把 contains 写成 contians，这条断言等于没写。
        这是框架目前比较危险的一处，改进方向是 else 分支直接累加失败标记。
        """
        self.a.assert_result([{'unknown_mode': {'msg': 'x'}}], RESPONSE, 200)
