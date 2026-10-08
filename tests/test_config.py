"""配置读取测试。

对应 `conf/operationConfig.py`。核心是校验两件事：
1. 正常的 section/option 读取没问题；
2. 仓库里提供的 `config.ini.example` 模板本身是可解析的，
   并且不含任何真实凭据——别人 clone 下来照着填就能用。
"""
import os
import re
import tempfile

from conf.operationConfig import OperationConfig
from conf.setting import DIR_BASE

EXAMPLE_INI = os.path.join(DIR_BASE, 'conf', 'config.ini.example')

# 真实凭据的特征：钉钉 webhook 的 access_token 是长十六进制串
REAL_TOKEN = re.compile(r'[0-9a-fA-F]{20,}')


def _write_ini(content):
    tmp = tempfile.TemporaryDirectory()
    path = os.path.join(tmp.name, 'config.ini')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return tmp, path


class TestOperationConfig:
    def test_read_section_value(self):
        tmp, path = _write_ini('[api_envi]\nhost = http://127.0.0.1:8080\n')
        try:
            assert OperationConfig(path).get_section_for_data('api_envi', 'host') == 'http://127.0.0.1:8080'
        finally:
            tmp.cleanup()

    def test_read_mysql_section(self):
        tmp, path = _write_ini('[MYSQL]\nhost = 127.0.0.1\nport = 3306\n')
        try:
            conf = OperationConfig(path)
            assert conf.get_section_mysql('host') == '127.0.0.1'
            assert conf.get_section_mysql('port') == '3306'
        finally:
            tmp.cleanup()

    def test_get_item_value_returns_all_options(self):
        tmp, path = _write_ini('[REDIS]\nhost = 127.0.0.1\nport = 6379\ndb = 0\n')
        try:
            assert OperationConfig(path).get_item_value('REDIS') == {
                'host': '127.0.0.1', 'port': '6379', 'db': '0'
            }
        finally:
            tmp.cleanup()

    def test_missing_section_returns_empty_string(self):
        """section 不存在时返回空串而不是抛异常，调用方要自己判断空值"""
        tmp, path = _write_ini('[api_envi]\nhost = x\n')
        try:
            assert OperationConfig(path).get_section_for_data('NOT_EXIST', 'key') == ''
        finally:
            tmp.cleanup()

    def test_missing_option_returns_empty_string(self):
        tmp, path = _write_ini('[api_envi]\nhost = x\n')
        try:
            assert OperationConfig(path).get_section_for_data('api_envi', 'not_exist') == ''
        finally:
            tmp.cleanup()


class TestConfigTemplate:
    def test_example_config_exists(self):
        assert os.path.isfile(EXAMPLE_INI), 'conf/config.ini.example 模板缺失'

    def test_example_config_is_parseable(self):
        conf = OperationConfig(EXAMPLE_INI)
        assert conf.get_section_for_data('api_envi', 'host')

    def test_example_config_has_all_required_sections(self):
        conf = OperationConfig(EXAMPLE_INI)
        for section in ('api_envi', 'MYSQL', 'REDIS', 'CLICKHOUSE', 'MongoDB', 'EMAIL', 'SSH', 'REPORT_TYPE'):
            assert conf.get_item_value(section), '模板缺少 section: {}'.format(section)

    def test_example_config_uses_placeholder_not_real_credentials(self):
        with open(EXAMPLE_INI, 'r', encoding='utf-8') as f:
            content = f.read()
        for line in content.splitlines():
            if '=' not in line or line.strip().startswith(';'):
                continue
            value = line.split('=', 1)[1].strip()
            assert not REAL_TOKEN.fullmatch(value), \
                '模板里「{}」像是真实凭据，模板必须留空或用占位值'.format(line.strip())

    def test_real_config_is_gitignored(self):
        """真实配置 conf/config.ini 绝不能提交到仓库"""
        gitignore = os.path.join(DIR_BASE, '.gitignore')
        with open(gitignore, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'config.ini' in content
