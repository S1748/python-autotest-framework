"""Allure 模块 / 用例编号生成器测试。

对应 `base/generateId.py`。这两个生成器给用例加 M01_ / C01_ 前缀，
目的是让 Allure 报告里的展示顺序和 pytest 的执行顺序一致
（Allure 默认按字符串排序，不补零的话 M10_ 会排在 M2_ 前面）。
"""
from base.generateId import generate_module_id, generate_testcase_id


class TestModuleId:
    def test_starts_from_m01(self):
        gen = generate_module_id()
        assert next(gen) == 'M01_'

    def test_zero_padded_to_two_digits(self):
        gen = generate_module_id()
        ids = [next(gen) for _ in range(9)]
        assert ids[0] == 'M01_'
        assert ids[8] == 'M09_'
        assert next(gen) == 'M10_'

    def test_lexicographic_order_matches_numeric_order(self):
        """补零的目的是让字典序等于数字序，否则 Allure 报告顺序会乱"""
        gen = generate_module_id()
        ids = [next(gen) for _ in range(12)]
        assert ids == sorted(ids)


class TestTestcaseId:
    def test_starts_from_c01(self):
        gen = generate_testcase_id()
        assert next(gen) == 'C01_'

    def test_zero_padded_to_two_digits(self):
        gen = generate_testcase_id()
        ids = [next(gen) for _ in range(10)]
        assert ids[9] == 'C10_'

    def test_lexicographic_order_matches_numeric_order(self):
        gen = generate_testcase_id()
        ids = [next(gen) for _ in range(15)]
        assert ids == sorted(ids)

    def test_two_generators_are_independent(self):
        a = generate_testcase_id()
        b = generate_testcase_id()
        assert next(a) == 'C01_'
        assert next(b) == 'C01_'
