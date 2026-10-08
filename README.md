# 接口自动化测试框架

基于 **pytest + YAML** 的数据驱动接口自动化测试框架。用例与代码分离：新增一个接口的测试，只需要写 YAML，不用写 Python。

## 设计思路

传统写法的痛点是每个接口都要重写一遍请求代码和断言代码。这个框架把「怎么发请求」「怎么断言」「怎么提取参数」全部封装成公共方法，测试人员只需要在 YAML 里描述三件事：

1. 请求哪个接口、用什么方法、传什么参数
2. 期望的响应是什么
3. 要从响应里提取哪些字段供后续用例使用

维护成本从「改代码」降到「改配置」。

## 功能特性

| 能力 | 说明 |
|---|---|
| 多类型用例 | 单接口测试、业务场景串联（多接口依赖）、批量数据驱动 |
| 参数提取 | 支持 JSONPath 与正则表达式两种方式，提取结果供后续用例引用 |
| 断言模式 | `contains` / `eq` / `ne` / `rv` / `db` 五种，覆盖字符串包含、相等、不等、任意值、数据库校验 |
| 数据库支持 | MySQL / Redis / ClickHouse / MongoDB，可同时连接多类数据源 |
| 测试报告 | Allure 与 TMReport 两种风格，配置里切换 |
| 结果通知 | 钉钉机器人（支持加签）、邮件推送 |
| 可视化工具 | 内置 PyQt5 图形界面，可在界面上调试接口并一键生成 YAML 用例 |

## 技术栈

- **语言**：Python 3.8+
- **测试框架**：pytest
- **HTTP**：requests
- **数据处理**：PyYAML、jsonpath、pandas、openpyxl
- **数据库**：PyMySQL、SQLAlchemy、redis、clickhouse-sqlalchemy、pymongo
- **报告**：allure-pytest、pytest-tmreport
- **GUI 工具**：PyQt5

## 目录结构

```
pythonproject/
├── base/                       # 基础封装
│   ├── apiutil.py              # 请求发送工具
│   ├── apiutil_business.py     # 业务场景串联工具
│   ├── new_testcase_tools.py   # PyQt5 可视化用例生成工具
│   └── removefile.py           # 目录清理工具
├── common/                     # 公共方法
│   ├── assertions.py           # 五种断言模式的实现
│   ├── sendrequest.py          # 请求封装
│   ├── readyaml.py             # YAML 读取与用例数据解析
│   ├── debugtalk.py            # 用例中可调用的自定义函数
│   ├── connection.py           # 四类数据库连接
│   ├── handleExcel.py          # Excel 数据读取
│   ├── operationcsv.py         # CSV 数据读取
│   ├── operxml.py              # XML 数据读取
│   ├── recordlog.py            # 日志记录
│   ├── dingRobot.py            # 钉钉机器人通知
│   └── semail.py               # 邮件通知
├── conf/                       # 配置
│   ├── config.ini.example      # 配置模板（复制为 config.ini 后填写）
│   ├── operationConfig.py      # ini 文件读取封装
│   └── setting.py              # 全局常量与路径定义
├── data/                       # 测试数据
│   └── sql/                    # 数据库断言用到的 SQL（XML 格式）
├── testcase/                   # 测试用例
│   ├── Single interface/       # 单接口用例
│   ├── Business interface/     # 业务场景串联用例
│   └── ProductManager/         # 商品管理模块用例
├── conftest.py                 # pytest 全局钩子（会话级夹具、结果汇总）
├── environment.xml             # Allure 报告的环境信息
├── pytest.ini                  # pytest 配置
├── requirements.txt            # 依赖清单
└── run.py                      # 执行入口
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

使用国内镜像源会快很多：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 准备配置

```bash
cp conf/config.ini.example conf/config.ini
```

然后编辑 `conf/config.ini`，至少填好 `[api_envi]` 的 `host`（被测服务地址）。用到数据库断言时再填对应的数据库连接信息。

> `config.ini` 含有数据库密码，已被 `.gitignore` 忽略，不会提交到仓库。

### 3. 生成测试报告需要 Allure 命令行

Allure 报告依赖 `allure` 命令，需先安装 [Allure CommandLine](https://github.com/allure-framework/allure2/releases)（依赖 Java 环境），并配置到 PATH。

### 4. 执行

```bash
python run.py
```

执行完成后会自动在浏览器打开测试报告。

## 编写用例

用例写在 `testcase/` 下的 `.yaml` 文件里，`baseInfo` 和 `testCase` 两个关键字不可省略。

```yaml
- baseInfo:
    api_name: 用户登录
    url: /dar/user/login
    method: post
    header:
      Content-Type: application/x-www-form-urlencoded;charset=UTF-8
  testCase:
    - case_name: 用户名和密码正确登录验证
      data:
        user_name: test01
        passwd: xxx
      validation:
        - contains: { 'msg': '登录成功' }
        - eq: { 'error_code': 0 }
      extract:
        token: $.data.token
```

### 参数类型

| 场景 | 参数类型 | 对应 Content-Type |
|---|---|---|
| POST 表单提交 | `data` | `application/x-www-form-urlencoded` |
| POST JSON 提交 | `json` | `application/json` |
| GET URL 传参 | `params` | — |
| 文件上传 | `files` | `multipart/form-data` |

三者只能选一个，且要与 header 保持一致，否则服务端解析不到参数。

### 断言模式

| 写法 | 含义 |
|---|---|
| `contains: {'message': 'success'}` | 响应中包含该字段/字符串 |
| `eq: {'state': '已入网'}` | 字段值相等 |
| `ne: {'state': '已入网'}` | 字段值不相等 |
| `rv: {"data": 2}` | 断言响应中的任意值 |
| `db: select * from sys_user where login_name='test999'` | 直接写 SQL 校验数据库 |

> `contains` 必须写在其他断言前面，`eq` / `ne` 写在后面。

### 参数提取与依赖

```yaml
      extract:                     # 提取单个参数（后覆盖前）
        id: $.data                 # JSONPath 写法
        status: '"status":"(.*?)"'  # 正则写法
        num: '"data":(\d*)'         # 提取数字
      extract_list:                # 提取多个参数，以列表返回
        ids: $.result[*].id
```

提取结果存入 `extract.yaml`，后续用例用 `${get_extract_data(token)}` 引用。

### 用例中可调用的函数

格式为 `${函数名(参数)}`，具体实现见 `common/debugtalk.py`，可自行扩展：

```yaml
        startDate: ${start_time()}
        ruleIds: ["${get_extract_data_lst(forbiddenRule, -2)}"]
```

## 测试报告

`conf/config.ini` 的 `[REPORT_TYPE]` 决定报告类型：

- **allure**（推荐）：在 `run.py` 中通过 `--clean-alluredir` 清理上次的原始数据，同时把根目录的 `environment.xml` 复制进报告目录，使报告中显示运行环境信息。
- **tm**：生成单文件 HTML 报告，执行完自动用浏览器打开。

## 常见问题

**pytest.ini 里不能加中文注释**
`pytest.ini` 对编码敏感，加入中文注释可能导致解析报错。需要注释时用 `;` 开头，或干脆不写。

**报告里的环境信息丢了**
`--clean-alluredir` 会清空报告原始数据目录，`environment.xml` 因此放在项目根目录，执行时再复制进报告目录。

**第三方库版本冲突**
不同环境的 Python 版本与三方库版本可能不兼容。报错时按提示卸载有冲突的库再重新安装即可，建议配合虚拟环境使用。

**不想手写 YAML 用例**
运行 `base/new_testcase_tools.py`，在图形界面里填好接口信息，先点「接口调试」确认能通，再点「生成 yaml 文件」。

## 说明

本项目用于接口自动化测试的实践与学习，示例用例中的接口地址、账号密码均为测试环境数据。
