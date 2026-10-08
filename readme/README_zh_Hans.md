# Seedance Dify 插件：手把手教程

生成一段短视频并取得完成后的文件。从获取 Key 开始，按下面步骤在 Dify 中看到第一次结果。截图来自 Dify CE 1.17.1 英文界面；新版本可能调整菜单位置。

[English](https://github.com/AceDataCloud/SeedanceDify/blob/main/README.md) · [当前模型和价格](https://platform.acedata.cloud/models)

## 1. 安装正确的插件

打开 [Seedance 官方市场页](https://marketplace.dify.ai/plugin/acedatacloud/seedance)，确认作者是 **acedatacloud**，点击 **Install（安装）**并选择你的 Dify 工作区。回到 Dify，进入 **Integrations（集成）→ Tools（工具）→ Tool Plugin（工具插件）**，找到 **Seedance**，卡片应显示 **From Marketplace**。

如果无法访问市场，请让 Dify 管理员检查安装权限和网络；插件需要能通过 HTTPS 连接 `api.acedata.cloud`。

![Installed plugin in Dify](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/01-installed.png)

## 2. 获取能调用该服务的 API Key

1. 登录 [Ace Data Cloud → 我的应用](https://platform.acedata.cloud/console/applications)。
2. 找到 **通用应用**。通用应用 Key 可用于账号有权使用的多个服务；服务专用 Key 仅限对应服务。本教程需要核对 **Seedance** 的调用权限、余额和当前价格。
3. 要用已有 Key，点击图中 **①复制**。要给 Dify 单独创建一个 Key，点击 **②管理密钥**，再点右上角 **创建**。

![复制已有Key或打开管理密钥](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/get-api-key-en.png)

4. 填名称，例如 `Dify tutorial`，按需设置用量、过期时间和 API 限制，点击 **创建**，再从列表或应用页复制 Key。如果启用了 **Allowed APIs / 允许的 API**，应同时包含本例所需的生成和任务查询接口：`/seedance/tasks`, `/seedance/videos`。

![创建独立的Dify凭据](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/create-api-key-en.png)

Dify 只粘贴复制出的 Token 字符串，不加 `Bearer `、引号或截图中的遮挡字符。不要用 `platform-...` 一类平台管理 Token 代替调用服务的 API Key。首次运行前确认服务权限和余额。

## 3. 在 Dify 中保存凭据

1. 进入 **Integrations → Tools → Tool Plugin → Seedance**。
2. 点击 **API Key Authorization Configuration（API Key 授权配置）**。如果已有凭据，先点 **1 Authorization**，再进入配置。
3. **Authorization Name（授权名称）**填写 `Ace Data Cloud`；**Ace Data Cloud Bearer Token** 填刚复制的 Key。
4. 选择谁可以使用该凭据，点 **Save（保存）**。不要把 Key 放进提示词或导出的工作流。

![Dify工具授权窗口](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/02-authorize.png)

## 4. 创建最小工作流并填参数

打开 **Studio（工作室）→ Create from Blank（从空白创建）→ Workflow（工作流）**，输入名称。点击节点旁的 **+** 添加 Tool，在本插件下选择准确的工具名称。按顺序拖动节点右侧连接点：

**Start → Seedance Generate Video（Seedance 生成视频） → Seedance Retrieve Task（查询任务） → Output**。

把生成节点重命名为 **Seedance**，查询节点命名为 **Retrieve completed task**，便于对照截图。首跑先用固定参数，Start 不用加输入。生成节点的 **Retry on Failure（失败重试）**保持关闭。

![节点连线总览](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/03-workflow.png)

选中生成/调用节点，按表填写；没有列出的可选参数先留空。

| Dify 字段 | 首跑值 |
|---|---|
| 模型 (`model`) | `doubao-seedance-2-0-mini-260615` |
| 时长（秒） (`duration`) | `4` |
| 分辨率 (`resolution`) | `480p` |
| 画面比例 (`ratio`) | `16:9` |
| 生成音频 (`generate_audio`) | `false` |

**提示词** (`prompt`):

```text
A teal paper cube slowly rotates on a cream studio background. Static camera, no text.
```

该文生视频示例直接使用 **Prompt**，**Content** 留空。如果改用原始 Content JSON，应清空提示词/参考图快捷字段；时长和帧数二选一。

![填写实际参数](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/03-configure.png)

## 5. 绑定同一个任务并等待结果

选中 **Seedance Retrieve Task**。在 **Task ID（任务 ID）**框点击变量选择器（或输入 `/`），选择 **Seedance → task_id**。必须选生成节点的输出变量，不能把变量名称作为普通文字输入。**Wait up to seconds（最长等待秒数）**填 `240`，本例 Trace ID 留空。

![选择生成节点的task_id变量](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/04-task-id.png)

选中 **Output**，点击 **+** 添加以下输出，并从 **Retrieve completed task** 节点选择对应变量：

| 输出名称 | 查询节点变量 | 类型 |
|---|---|---|
| status | status | String |
| success | success | Boolean |
| task_id | task_id | String |
| media_urls | media_urls | Array[String] |
| result | result | Object |

![输出变量映射](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/05-output.png)

点击 **Test Run → Start Run**。如果 240 秒内未生成完，返回 `status=pending` 是正常情况。**不要重跑整个工作流**，否则会再次提交生成。复制已有 task_id，另建 **Start → Seedance Retrieve Task → Output**，Task ID 填原来的值，等待填 0 或 240；只查询这个任务，直到 `status=succeeded` 且 `success=true`，再打开 `media_urls` 中的链接。Dify 流程绿色成功不等于服务任务已经完成。

## 6. 检查预期输出

完成后结果形态如下；示例 URL 只说明字段位置，要使用你自己返回的链接：

```json
{
  "status": "succeeded",
  "success": true,
  "media_urls": [
    "https://.../result.mp4"
  ]
}
```

![真实Dify成功结果](https://raw.githubusercontent.com/AceDataCloud/SeedanceDify/ba8338fa035907677c2613c2087d75c9bdb41bc2/_assets/tutorial/06-result.png)

实际运行示例；你的任务 ID 和链接会不同。

## 常见问题

| 现象 | 处理方法 |
|---|---|
| 授权失败、401/403 | 重新复制完整 API Token，去掉 `Bearer `；检查服务权限、余额、过期时间和允许的 API。 |
| 参数错误、400 | 核对示例中的模型、操作、分辨率和 JSON 格式，不要混用不同操作的字段。 |
| `pending` / 媒体列表为空 | 继续查原任务 ID，不重新生成。 |
| 429 限流 | 稍后再试并降低并发；不要打开付费生成的自动重试。 |
| 超时、5xx、任务失败 | 先看原任务与请求历史，再决定是否重提；联系支持只提供 task_id/trace_id，不提供 Key。 |
| 链接打不开 | 先确认任务最终成功，再检查 Dify 服务器/浏览器是否能访问返回的链接。 |

[下载可导入工作流](https://github.com/AceDataCloud/SeedanceDify/raw/refs/heads/main/docs/quickstart.dify.yml)。在 Studio 导入后配置自己的凭据；文件不含任何 Key。

## 隐私、费用与支持

插件免费，API 按当前服务价格计费。插件把所选输入与凭据发送至 `api.acedata.cloud`，凭据由 Dify 保存；详见[隐私说明](https://github.com/AceDataCloud/SeedanceDify/blob/main/PRIVACY.md)。只提交有权处理的内容。

[源码](https://github.com/AceDataCloud/SeedanceDify) · [问题反馈](https://github.com/AceDataCloud/SeedanceDify/issues) · dev@acedata.cloud · [高级功能](https://github.com/AceDataCloud/SeedanceDify/blob/main/CAPABILITIES.md)。开发、品牌来源和验证材料位于源码仓库，不影响以上首跑步骤。
