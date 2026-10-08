"""密钥防泄漏测试。

背景：这个框架早期版本把钉钉机器人的 access_token 直接写死在
`common/dingRobot.py` 里。一旦仓库公开，任何人拿到 token 就能往群里发消息。
现在改成「环境变量优先、conf/config.ini 兜底」，并把真实配置写进 .gitignore。

这里放两条守卫：
1. `get_dingtalk_conf` 的读取优先级正确；
2. 源码里不再出现任何硬编码凭据——防止以后有人手滑把 token 粘回代码里。
"""
import os
import re

import pytest

from common.dingRobot import generate_sign, get_dingtalk_conf
from conf.setting import DIR_BASE

# 钉钉 webhook 的 access_token 是长十六进制串，用它作为硬编码特征
HARDCODED_TOKEN = re.compile(r'access_token=[0-9a-fA-F]{20,}')

# 不参与扫描的目录
SKIP_DIRS = {'.git', '.idea', 'venv', '.venv', '__pycache__', 'report', 'logs',
             '.pytest_cache', '.workbuddy', '.claude'}

# 不参与扫描的文件（本地真实配置，本来就不该提交）
SKIP_FILES = {'config.ini', 'extract.yaml'}


def _iter_source_files():
    for root, dirs, files in os.walk(DIR_BASE):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name in SKIP_FILES:
                continue
            if not name.endswith(('.py', '.yaml', '.yml', '.ini', '.example', '.cfg')):
                continue
            yield os.path.join(root, name)


class TestDingtalkConfig:
    def test_env_vars_have_priority(self, monkeypatch):
        monkeypatch.setenv('DINGTALK_ACCESS_TOKEN', 'token-from-env')
        monkeypatch.setenv('DINGTALK_SECRET', 'secret-from-env')
        assert get_dingtalk_conf() == ('token-from-env', 'secret-from-env')

    def test_returns_two_strings_without_raising(self, monkeypatch):
        """没有任何配置时也不能抛异常，只返回空串。

        注意这里不断言具体值：本地 conf/config.ini 可能存在真实配置（该文件不提交），
        CI 环境则没有。只要保证调用不抛异常、返回两个字符串即可。
        """
        monkeypatch.delenv('DINGTALK_ACCESS_TOKEN', raising=False)
        monkeypatch.delenv('DINGTALK_SECRET', raising=False)
        access_token, secret = get_dingtalk_conf()
        assert isinstance(access_token, str)
        assert isinstance(secret, str)

    def test_generate_sign_returns_millisecond_timestamp_and_sign(self):
        timestamp, sign = generate_sign()
        assert timestamp.isdigit()
        assert len(timestamp) == 13
        assert sign


class TestNoHardcodedCredentials:
    def test_no_hardcoded_dingtalk_token_in_source(self):
        offenders = []
        for path in _iter_source_files():
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                if HARDCODED_TOKEN.search(f.read()):
                    offenders.append(os.path.relpath(path, DIR_BASE))
        assert not offenders, '以下文件疑似硬编码了钉钉 token，请改为读环境变量/配置：{}'.format(offenders)

    def test_real_config_files_are_gitignored(self):
        with open(os.path.join(DIR_BASE, '.gitignore'), 'r', encoding='utf-8') as f:
            content = f.read()
        for name in ('conf/config.ini', 'extract.yaml'):
            assert name in content, '{} 必须写进 .gitignore'.format(name)

    def test_example_config_has_no_real_token(self):
        path = os.path.join(DIR_BASE, 'conf', 'config.ini.example')
        if not os.path.exists(path):
            pytest.skip('config.ini.example 不存在')
        with open(path, 'r', encoding='utf-8') as f:
            assert not HARDCODED_TOKEN.search(f.read())
