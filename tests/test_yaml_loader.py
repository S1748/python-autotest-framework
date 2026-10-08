"""YAML 测试数据加载测试。

对应 `common/readyaml.py` 的 `get_testcase_yaml` 与 `ReadYamlData`。
重点校验 `testcase/` 下所有 YAML 都能被正常解析——这是 CI 里
「用例收集」那一关的兜底，避免有人改坏 YAML 后整个模块 0 用例却没人发现。
"""
import os
import tempfile

from common.readyaml import ReadYamlData, get_testcase_yaml
from conf.setting import DIR_BASE

TESTCASE_DIR = os.path.join(DIR_BASE, 'testcase')


class TestGetTestcaseYaml:
    def test_single_api_file_returns_base_info_and_case_pairs(self):
        file = os.path.join(TESTCASE_DIR, 'product_manager', 'getProductList.yaml')
        cases = get_testcase_yaml(file)
        assert len(cases) == 1
        base_info, test_case = cases[0]
        assert base_info['api_name'] == '商品列表'
        assert base_info['method'] == 'Get'
        assert base_info['url'].startswith('/')
        assert 'case_name' in test_case

    def test_multi_case_file_returns_raw_list(self):
        """顶层有多个元素时直接返回原始列表（业务场景用例走这个分支）"""
        file = os.path.join(TESTCASE_DIR, 'business_scenario', 'BusinessScenario.yml')
        cases = get_testcase_yaml(file)
        assert isinstance(cases, list)
        assert len(cases) >= 2
        assert 'baseInfo' in cases[0]

    def test_missing_file_returns_none(self):
        assert get_testcase_yaml(os.path.join(TESTCASE_DIR, 'not_exist.yaml')) is None

    def test_all_testcase_yaml_are_loadable(self):
        """遍历 testcase 目录，所有 YAML 都必须能解析出内容"""
        found = []
        for root, _, files in os.walk(TESTCASE_DIR):
            for name in files:
                if name.endswith(('.yaml', '.yml')):
                    path = os.path.join(root, name)
                    data = get_testcase_yaml(path)
                    assert data, '{} 解析结果为空，请检查 YAML 语法'.format(name)
                    found.append(name)
        assert len(found) >= 12, 'testcase 目录下的 YAML 数量异常：{}'.format(found)

    def test_every_case_has_required_keys(self):
        """每个单接口用例必须带 baseInfo(api_name/url/method) 和 case_name"""
        for root, _, files in os.walk(TESTCASE_DIR):
            for name in files:
                if not name.endswith(('.yaml', '.yml')):
                    continue
                cases = get_testcase_yaml(os.path.join(root, name))
                if not cases or not isinstance(cases[0], (list, tuple)):
                    continue
                for base_info, test_case in cases:
                    assert 'api_name' in base_info, '{} 缺少 api_name'.format(name)
                    assert 'url' in base_info, '{} 缺少 url'.format(name)
                    assert 'method' in base_info, '{} 缺少 method'.format(name)
                    assert 'case_name' in test_case, '{} 缺少 case_name'.format(name)


class TestReadYamlData:
    def test_get_yaml_data_reads_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'sample.yaml')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('api_name: 商品列表\npage: 1\n')
            data = ReadYamlData(path).get_yaml_data
            assert data == {'api_name': '商品列表', 'page': 1}

    def test_get_yaml_data_reads_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'sample.yaml')
            with open(path, 'w', encoding='utf-8') as f:
                f.write('- a\n- b\n- c\n')
            assert ReadYamlData(path).get_yaml_data == ['a', 'b', 'c']

    def test_extract_yaml_path_is_under_project_root(self):
        """extract.yaml 必须落在仓库根目录，且已被 .gitignore 忽略"""
        from conf.setting import FILE_PATH
        assert os.path.dirname(FILE_PATH['EXTRACT']) == DIR_BASE

        gitignore = os.path.join(DIR_BASE, '.gitignore')
        with open(gitignore, 'r', encoding='utf-8') as f:
            content = f.read()
        assert 'extract.yaml' in content, 'extract.yaml 必须写进 .gitignore，避免把运行时 token 提交上去'
