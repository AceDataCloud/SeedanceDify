# Seedance Dify 插件

在 Dify 中使用 Ace Data Cloud 的 Seedance API。插件免费，API 需要自己的账号和服务权限，并按当前价格扣费。

## 安装与授权

1. 在 [Ace Data Cloud](https://platform.acedata.cloud/console/applications) 开通服务并创建 API Token；使用前核对[当前模型与价格](https://platform.acedata.cloud/models)。
2. 官方审核并上架后，可从 Dify Marketplace 安装。审核期间可以在测试环境使用 Dify 官方的包安装或远程调试流程。PR 已提交不表示市场已发布，也不表示默认预装。
3. 在 Dify 的插件或工具页填写 Bearer Token（`acedata_bearer_token`）。凭据检查不会生成内容。授权使用只读任务查询。

## 工具与工作流

| Tool | API |
|---|---|
| `seedance_generate_video` | `POST /seedance/videos` |
| `seedance_task_retrieve` | `POST /seedance/tasks` |
| `seedance_tasks_retrieve_batch` | `POST /seedance/tasks` |

完整 MCP 对照、参数别名和适用范围见 [CAPABILITIES.md](../CAPABILITIES.md)。复杂参数填写 JSON，示例见 [contract-examples.json](https://github.com/AceDataCloud/SeedanceDify/blob/main/tests/contract-examples.json)；其中 example.org 链接须替换成自己的可访问媒体。

生成工作流连接 **开始 → 生成工具 → 查询任务 → 输出**。提交返回 `pending` 时，保存 `task_id`，并使用同一 ID 查询。`wait_seconds=0` 查询一次，1–240 表示最多等待相应秒数。仍在运行时继续查询原任务，不重新提交生成。请关闭生成节点的自动重试。

输出包含 `status`、`success`、`task_id`、`trace_id`、`media_urls`、`data` 和 `result`。只有任务最终完成才返回成功；预览链接不算完成。批量查询分别保留每个任务的状态。同步操作直接返回结果。删除或归档需要设置 `confirm=true`。插件不会执行模型返回的工具调用。

本版补充了当前服务接口的参数和操作；不同 MCP 函数可能合并为操作选项或结构化输入。图片接口固定返回 URL，流式接口使用 Dify 可处理的完整响应及异步任务查询。每个高级操作和模型是否已真实验证，以测试证据记录为准。

## Logo、隐私与费用

浅色和深色图标复用系统中已有的官方服务资产，未经重绘；来源和 SHA256 见 [branding-source.json](https://github.com/AceDataCloud/SeedanceDify/blob/main/tests/branding-source.json)。

插件仅直接连接 `api.acedata.cloud`，把用户选择的文本、参数、参考媒体 URL 和任务 ID 发给 API，并向 Dify 返回结果。只提交已获授权的媒体。音色和自定义模型创建涉及对应的训练或克隆处理，须先核对素材权限和价格。详见 [隐私说明](../PRIVACY.md)。

使用记录以 Ace Data Cloud 的账单为准，单位为 Credits；USD = Credits × 当前套餐价格 / 额度。生成超时后先检查请求历史，避免重复扣费。插件没有自动付费重试或模型替换。

## 源码与验证

- 源码：https://github.com/AceDataCloud/SeedanceDify
- 问题反馈：https://github.com/AceDataCloud/SeedanceDify/issues
- 联系：dev@acedata.cloud

需要 Python 3.12。运行 `python -m pytest tests -q`、`ruff check .`、`ruff format --check .` 和 `dify plugin package .`。真实 Dify 截图与结果、未覆盖项见 tests 目录；单元测试通过不等于所有模型真实调用通过，市场上架和安装另行验收。
