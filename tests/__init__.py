"""框架自带单元测试。

这些用例只覆盖「不依赖被测系统」的纯逻辑部分：
DebugTalk 的加密 / 时间工具、YAML `+${}` 占位符替换、断言模式、配置读取、YAML 加载。

之所以这么划范围：真正的接口用例（testcase/ 下）必须连到 `[api_envi] host`
指向的测试环境和 MySQL / Redis 才能跑，CI 里没有这些依赖。
CI 里对 testcase/ 只做「收集阶段」校验，确保 YAML 全部合法、
用例能被正常发现，这部分由 .github/workflows/ci.yml 里的 collect job 负责。
"""
