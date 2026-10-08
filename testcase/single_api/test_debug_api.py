import allure
import pytest

from common.readyaml import get_testcase_yaml
from base.apiutil import RequestBase
from base.generateId import m_id, c_id


@allure.feature(next(m_id) + '用户管理模块（单接口）')
class TestUserManager:

    # 场景，allure报告的目录结构
    @allure.story(next(c_id) + "新增用户")
    # 测试用例执行顺序设置
    @pytest.mark.run(order=1)
    # 参数化，yaml数据驱动
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/addUser.yaml"))
    def test_add_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "修改用户")
    @pytest.mark.run(order=2)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/updateUser.yaml"))
    def test_update_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "删除用户")
    @pytest.mark.run(order=3)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/deleteUser.yaml"))
    def test_delete_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "查询用户")
    @pytest.mark.run(order=4)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/queryUser.yaml"))
    def test_query_user(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    # ========== 下面是从 PDF 文档里新增的接口用例 ==========

    @allure.story(next(c_id) + "获取商品列表")
    @pytest.mark.run(order=5)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/goodsList.yaml"))
    def test_get_goods_list(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "获取商品详情")
    @pytest.mark.run(order=6)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/productDetail.yaml"))
    def test_get_product_detail(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)

    @allure.story(next(c_id) + "校验商品库存")
    @pytest.mark.run(order=7)
    @pytest.mark.parametrize('base_info,testcase', get_testcase_yaml("./testcase/single_api/shoppingInventory.yaml"))
    def test_shopping_inventory(self, base_info, testcase):
        allure.dynamic.title(testcase['case_name'])
        RequestBase().specification_yaml(base_info, testcase)
