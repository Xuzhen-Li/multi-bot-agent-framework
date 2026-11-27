# 多 bot / 多模型分工：做法摘要

英文全文和出处见 [../PRACTICE.md](../PRACTICE.md)、[../OUTSOURCING.md](../OUTSOURCING.md)、[../REVIEW_LOOP.md](../REVIEW_LOOP.md)、[../ROLES.md](../ROLES.md)。

1. 能一个 agent 做完就不拆。要拆，先确认各部分不改同一处，并把完整任务说明和已做的决定一起交给每个 worker（Cognition，2025）。
2. 拆开适合「广度」任务，例如分方向查文献、一个仓库一个 worker；代价是 token 多。Anthropic 报告多 agent 约是聊天的 15 倍 token。
3. 难题先让推理强的模型出计划，再让便宜快的模型照计划改文件（aider 的 architect / editor 模式，R1 + Sonnet 64.0%）。
4. 外包给别的模型：DeepSeek（`deepseek-v4-pro`、`deepseek-flash`，思考强度 low / high / max）和 Gemini（OpenAI 兼容地址，`reasoning_effort`）都走 OpenAI 格式，用 `scripts/ask_model.py` 一个脚本就能调。模型名和价格会变，开跑前看官方页面，并把模型名写进日志。
5. 写的和审的不是同一个 bot，最好也不是同一家模型：模型会偏爱自己写的东西（Panickssery 等，2024）。两份稿子比较时，换一下顺序再审一次。
6. 复核分阻塞项（必改，挡合并）和建议项。同一个问题退回三次还没过，就停下来问主人。
7. 润色放在复核全部 PASS 之后；润色稿要和复核过的稿逐项比对数字、命令、路径。
