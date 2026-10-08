"""DebugTalk 工具方法测试。

DebugTalk 是 YAML 里 `${func(args)}` 实际调用的目标类，
这里校验加密、时间戳、日期边界等纯函数行为。
"""
import base64
import datetime
import hashlib

from common.debugtalk import DebugTalk


class TestEncryption:
    def setup_method(self):
        self.dt = DebugTalk()

    def test_md5_matches_hashlib(self):
        assert self.dt.md5_encryption('admin123') == hashlib.md5(b'admin123').hexdigest()

    def test_md5_is_stable_for_same_input(self):
        assert self.dt.md5_encryption('abc') == self.dt.md5_encryption('abc')

    def test_md5_differs_for_different_input(self):
        assert self.dt.md5_encryption('abc') != self.dt.md5_encryption('abd')

    def test_sha1_matches_hashlib(self):
        assert self.dt.sha1_encryption('admin123') == hashlib.sha1(b'admin123').hexdigest()

    def test_base64_encryption(self):
        assert self.dt.base64_encryption('abc') == base64.b64encode(b'abc')


class TestTimestamp:
    def setup_method(self):
        self.dt = DebugTalk()

    def test_second_timestamp_is_10_digits(self):
        assert len(str(self.dt.timestamp())) == 10

    def test_millisecond_timestamp_is_13_digits(self):
        assert len(str(self.dt.timestamp_thirteen())) == 13

    def test_millisecond_is_second_times_1000(self):
        assert self.dt.timestamp_thirteen() == self.dt.timestamp() * 1000

    def test_today_zero_stamp_is_before_today_end_stamp(self):
        assert self.dt.today_zero_stamp() < self.dt.today_end_stamp()

    def test_specified_end_tamp_after_specified_zero_tamp(self):
        assert self.dt.specified_zero_tamp(0) < self.dt.specified_end_tamp(0)


class TestDateBounds:
    def setup_method(self):
        self.dt = DebugTalk()

    def test_start_time_is_yesterday(self):
        value = datetime.datetime.strptime(self.dt.start_time(), '%Y-%m-%d %H:%M:%S')
        delta = datetime.datetime.now() - value
        # 允许 3 秒误差，避免用例恰好跨秒执行时抖动
        assert datetime.timedelta(days=1, seconds=-3) < delta < datetime.timedelta(days=1, seconds=3)

    def test_month_start_is_first_day(self):
        assert self.dt.month_start_time().endswith('-01')

    def test_month_end_matches_calendar(self):
        now = datetime.datetime.now()
        last_day = datetime.date(now.year, now.month, 1)
        # 推到下个月 1 号再退一天，即本月最后一天
        next_month = (last_day + datetime.timedelta(days=32)).replace(day=1)
        expect = (next_month - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        assert self.dt.month_end_time() == expect
