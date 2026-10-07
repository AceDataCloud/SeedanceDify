# Seedance

**Author:** acedatacloud

**Type:** tool provider plugin

**API:** `https://api.acedata.cloud/seedance/videos`

## 工具

| 工具 ID | 功能 | 参数 |
|---|---|---|
| `seedance_generate_video` | Seedance 生成视频 | `prompt`, `model`, `first_frame_url`, `resolution`, `ratio`, `duration`, `generate_audio` |
| `seedance_task_retrieve` | Seedance 查询任务 | `task_id`, `wait_seconds` |

输出包含 `status`、`task_id`、`media_urls`、`result`，以及旧插件约定的 `success`、`trace_id`、`data`。`success` 仅在结果完成时为 true；失败会抛出工具错误。

凭据字段为 `acedata_bearer_token`，粘贴 Token 时不需要 `Bearer ` 前缀。

通过 Ace Data Cloud 使用文生视频和首帧图生视频。插件免费安装，API 使用需要自己的账户与额度。

## 配置

1. 登录 [控制台](https://platform.acedata.cloud/console/applications)，开通服务并检查[当前价格](https://platform.acedata.cloud/models)。创建有该服务权限的 API Key。
2. 官方上架后，从 Dify Marketplace 安装；审核中的源码或插件包不等于官方已收录。开发验证可以在隔离工作区使用官方远程调试。
3. 在 **Integrations → Tools（集成 → 工具）** 或旧版插件页面填写 Key。验证凭据只查询任务，不生成付费媒体。
4. 工作流连接**开始 → 生成工具 → 输出**。填写提示词或文本、模型和选项，关闭生成步骤自动重试。
5. 保存返回的 `task_id`，传给 **Retrieve or wait for task**。等待秒数为 0 时只查询一次，120–240 时进行有限等待。`pending` 表示未完成；继续查询同一 ID，不要重发生成。
6. `status=succeeded` 后，通过 `media_urls` 获取媒体链接。用输出节点或 Chatflow 回答节点返回链接；任务失败会产生工具错误。

## 范围与计费

本版支持文生视频和首帧图生视频及任务查询。编辑图片时填写公开 HTTPS 图片地址；Seedance 本版只支持文本或首帧输入；Fish 本版不含声音克隆；Suno 的时长是目标值，中间预览不视作完成结果。

到[用量页](https://platform.acedata.cloud/console/usages)按 Key 和时间核对实际扣减。Credits 的 USD 换算使用当前套餐价格与额度。异步受理、任务成功、文件可读取及扣费应分别验证。

连接超时 10 秒，读取超时 60 秒，单次任务等待不超过 240 秒。网络不确定时先查请求历史，不盲目重发。本插件不自动重试付费请求或更换模型。

## 隐私与支持

Key、提示词、歌词/文本及所选参考媒体 URL 通过 HTTPS 发给 `api.acedata.cloud`。插件不下载任意 URL、不执行代码或额外持久化内容，Dify 管理凭据与运行历史。只使用有权处理的素材，详见 [隐私政策](../PRIVACY.md)。

源码：https://github.com/AceDataCloud/SeedanceDify

支持：dev@acedata.cloud

## 与旧 Dify 插件的对应

本仓库沿用旧插件的服务图标、工具命名、Bearer Token 配置、中英文说明和代码组织方式。运行范围以上方工具表为准；这是独立的官方市场投稿，不是旧 19 插件发布链的恢复。
