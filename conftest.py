# -*- coding: utf-8 -*-
import time

import pytest

from common.readyaml import ReadYamlData
from base.removefile import remove_file
from common.dingRobot import send_dd_msg
from conf.setting import dd_msg

import warnings

yfd = ReadYamlData()


@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)

    yfd.clear_yaml_data()
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


# 会话开始时间，由 pytest_sessionstart 钩子写入。
# 不用 terminalreporter._sessionstarttime，该属性是 pytest 私有实现，
# 在 pytest 8 起已更名为 _session_start 且类型变为 timing.Instant，
# 直接参与减法会抛 TypeError，导致摘要钩子整体失败。
_SESSION_START = time.time()


def pytest_sessionstart(session):
    """记录本次会话开始时间，用于统计执行总时长"""
    global _SESSION_START
    _SESSION_START = time.time()


def generate_test_summary(terminalreporter):
    """生成测试结果摘要字符串"""
    stats = terminalreporter.stats
    total = getattr(terminalreporter, '_numcollected', None)
    if total is None:
        total = sum(len(v) for v in stats.values())
    passed = len(stats.get('passed', []))
    failed = len(stats.get('failed', []))
    error = len(stats.get('error', []))
    skipped = len(stats.get('skipped', []))
    duration = round(time.time() - _SESSION_START, 2)

    summary = f"""
    自动化测试结果，通知如下，请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if dd_msg:
        send_dd_msg(summary)
