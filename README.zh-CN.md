# 电影评分与奥斯卡认可度分析

整合 **IMDb、烂番茄和奥斯卡** 数据，研究 2016–2025 年电影的观众评分、热度、影评评分和奖项认可之间的关系。原项目是 **CPSC 368 Group 1 小组课程项目**，分别使用 Oracle 和 MongoDB 实现。

[English README](README.md) · [完整中文复盘](docs/PROJECT_WALKTHROUGH.zh-CN.md) · [GitHub 上传指南](docs/GITHUB.zh-CN.md)

## 项目实际做了什么

1. 准备三份清洗后的数据：10,147 部 IMDb 电影、494 条奥斯卡电影记录、1,107 条烂番茄记录。
2. 通过 IMDb ID 关联奥斯卡，通过片名和年份关联烂番茄。
3. 在 Oracle 中创建三张表，执行连接查询并绘图。
4. 在 MongoDB 中将评分、类型和奥斯卡标记嵌入电影文档，用聚合管道完成相同研究问题。
5. 单独尝试四轮匹配，把烂番茄的匹配数从 787 提高到 802。
6. 对比两种数据库；最终报告基于本项目的结构化分析需求选择 Oracle，没有进行性能基准测试。

## 已复现的主要结果

| 指标 | 结果 |
| --- | --- |
| IMDb 与烂番茄观众评分的 Pearson 相关系数 | 0.7172，样本 787 部 |
| IMDb 票数与烂番茄影评评分的 Pearson 相关系数 | 0.1425，样本 787 部 |
| 能关联到电影样本的奥斯卡记录 | 348 条，另 146 条未关联 |
| 有奥斯卡记录 / 无匹配记录的 IMDb 平均分 | 7.319 / 6.132 |
| 四轮匹配的累计匹配数 | 787 → 798 → 800 → 802 |
| 最终未匹配 / 待人工复核候选 | 305 行 / 5 个候选，候选包含在未匹配行中 |

这是描述性分析，不能据此声称奥斯卡“导致”更高评分，也没有完成显著性检验。奥斯卡文件没有保留获奖标记，而且只到 2024 年；“无匹配记录”不等于从未获得奥斯卡认可。影评评分衡量的是评分表现，不能直接称为影评人的参与程度。

## 怎样运行

在项目目录内使用 Python 3.11：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/reproduce.py
.venv\Scripts\python.exe scripts/run_matching.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

默认运行不需要学校账号或数据库服务器。新的本地入口使用内存 SQLite 执行原来的三个 SELECT 查询，生成图表、结果表和 MongoDB 文档文件。原来的 Oracle 与 MongoDB 技术路线见 [数据库运行指南](docs/DATABASE_SETUP.md)。

## 如何阅读这个项目

- 想回忆整个过程：看 [中文复盘](docs/PROJECT_WALKTHROUGH.zh-CN.md)。
- 想了解每一列及关联损失：看 [数据说明](docs/DATA.md)。
- 想展示数据库设计：看 [结构图与设计说明](docs/ARCHITECTURE.md)。
- 想看最终作品：看 [原报告](reports/original/final-report.pdf)、[原演示稿](reports/original/presentation.pdf) 和 `reports/figures/`。
- 想知道哪些是这次补的：看 [整理变更说明](docs/REORGANIZATION.md)。

原始大数据文件和最早的清洗脚本没有保留下来，因此可复现流程从现有清洗 CSV 开始。历史报告保持原样，新版说明单独记录修正。小组成员姓名及个人分工无法从现有文件确认，本仓库不会把集体成果改写成个人独立完成。
