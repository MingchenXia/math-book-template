# Math book template

一个可复用的数学写书仓库：章节式 LaTeX、自动问题目录、独立解答文件夹、证明审校、已解决问题自动进入书稿，以及成稿后的作者审阅修订流程。

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MingchenXia/math-book-template)

## 一键开始

**Codex 云端**：支持当前 **Work in → Cloud** 环境。首次选择仓库，把 [云端配置提示词](docs/codex-cloud.md) 发给配置 agent；它运行 `bash scripts/setup-codex-cloud.sh` 安装并验证。查看报告并点击 Publish 后，新任务直接选择该环境。云端宿主 agent 不需额外 CLI/API 登录，独立审校使用模板的 `review-prepare` / `review-record` 入口。首次的账号连接和环境发布仍须在 Codex 界面完成。

**GitHub Codespaces**：

点击 **Use this template → Create a new repository** 为你的书建立仓库，然后 **Code → Codespaces → Create codespace**。环境会自动安装 TeX、Biber、Python、PDF 工具和固定版本 Codex CLI，并编译示例书。也可以点击上方按钮直接试用模板。首次构建容器需要下载 TeX，耗时取决于网络。

本地有 TeX/Codex 或 Docker 时，一条命令准备环境并生成 PDF：

```sh
bash start.sh
```

编辑 `bookflow.json` 中的书名、作者，按 `PLAN.md` 确定读者和范围，替换 `book/chapters/` 的示例。PDF 在 `build/pdf/main.pdf`。示例的两个问题都是初等的演示任务，并非文献开放问题。

在本地或 Codespaces 登录自己的 Codex 账号后即可运行专用 CLI agent（云端宿主流程见 [云端说明](docs/codex-cloud.md)）：

```sh
codex login
make edit       # 写作/编辑：推进当前章节，处理审校建议
make review     # 独立只读审校：数学、写作、引用、格式、第二遍通读
```

长书可逐章运行 `python3 scripts/bookflow.py agent review --unit book/chapters/01-foundations.tex --pages 4`。pages 用编译 PDF 的物理页号，必须覆盖该单元；根文件与 preamble 也须审校全局结构、bibliography 和 index。全部活跃输入的报告在同一当前书稿指纹下通过后，汇总检查才允许进入成稿阶段；不能以抽样代替终审。

工具与登录方式见 [环境说明](docs/environment.md)。模板不需要作者机器上的私有 skill、参考文献库或验证器。

## 日常写书

```text
book/chapters/            书的章节与前言
research/open-problems.* 自动汇总的问题目录
research/solutions/      每个问题的完整或部分解答
research/reviews/        独立审校报告与输入指纹
research/editorial/      整书修订队列、基线、提案记录
references/papers/       参考文献全文（默认不公开提交）
references/notes/        阅读笔记、精确版本与定理定位
references/references.bib 整书唯一 bibliography
agents/                  写作、编辑、书稿审校、解答审校职责
```

在章节里写：

```tex
\BookProblem{OP-003}{目录标题}{精确的问题陈述，包含假设和适用范围。}
```

`make sync` 自动生成 [问题目录](research/open-problems.md)。目录表示本书的证明边界；“文献中仍开放”需要另外查证。日常编译、提交 hook 和 GitHub maintenance 都会同步；需要编辑时实时更新，可显式运行 `make watch`。

解答放在 `research/solutions/OP-003/`，格式见 [解答说明](research/solutions/README.md)。然后：

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-003
make build
make review
```

通过独立审校的完整解答自动替换书中原问题并保留引用标签；部分解答保留未解决状态。证明或相关输入改动后，指纹检查会令旧审批失效。生成的 TeX 不入 Git，任何机器都由相同源文件重建。自动替换之外的旧说法、推论和依赖由编辑 agent 逐一检查。

## 自动检查与审校

每次 push/PR 自动测试工作流、构建同一容器环境并编译 PDF，在 Actions 的 `book-<commit>` artifact 中保留 PDF、源文件指纹和问题清单。

`Book maintenance` 在默认分支的书稿/解答改动后自动更新问题目录，将结果保留为 Actions artifact。若为仓库配置 Actions secret **OPENAI_API_KEY**，它还会分别审校新解答和短书；没有 secret 时明确跳过 AI，仍执行目录同步。AI API 使用需要你自己的可用账号。需要自动提出维护 PR 时，另行设置仓库 variable **ENABLE_MAINTENANCE_PRS=true**，并自行启用 GitHub Actions 创建 PR 的仓库权限；此选项默认关闭，本模板不会批准或自动合并 PR。

启用 PR 选项后，由默认 `GITHUB_TOKEN` 创建的 PR 通常不会自动触发新工作流。请在合并维护 PR 前，手动运行 `Book checks` 并选择 `automation/book-maintenance` 分支，检查相同版本的 PDF。没有变化时不会创建 PR。没有预设 cron，也不会将书稿部署到个人主页。

## 成稿后的改书

采用 [SGPT 的改书流程](https://github.com/MingchenXia/SGPT/blob/main/AGENTS.md)：独立分支、实际修改记录、证明与依赖复核、修改处 PDF、提案 PR，以及作者明确批准该版本后才合并或出版。

整书完成且通过当前完整审校后：

```sh
make finish
git add bookflow.json research CHANGELOG.md
git commit -m "Record the completed-book baseline"
python3 scripts/bookflow.py revision-start fix-estimate
# 在 revision/fix-estimate 修改，更新 CHANGELOG.md，处理修订队列
make review
python3 scripts/bookflow.py revision-prepare --base main --pages 5-8 --summary "修正某估计的依赖条件，并检查受影响推论"
```

`--pages` 是 PDF 物理页号；应涵盖全部修改处和足够上下文。命令生成完整 PDF、修改处 PDF、diff 和 PR 正文。由作者审核当前 PDF 后再合并；agent 审校不会替代作者的批准。后续 PR、重新批准、发布和合并后分支清理见 [完整改书流程](docs/revision.md)。模板不预设出版网站，使用时再确定发布目标。

## 验证与设计来源

```sh
make test
make sync
make check
make build
```

Python 工作流只用标准库。测试覆盖未审校/已审校/部分解答、过期审校、路径与输入图错误，以及成稿后分支边界；编译另行检查 TeX/Biber。检查能验证流程和构建，数学审校仍须按实际读到的范围记录。

写书阶段参考 [non-kahler-pluripotential-theory](https://github.com/MingchenXia/non-kahler-pluripotential-theory) 的书稿、蓝图、问题目录与审计分工；成稿修订参考 [SGPT](https://github.com/MingchenXia/SGPT)。本仓库的代码和示例独立编写，没有复制原仓库的私有书稿、论文或研究档案。见 [工作流细节](docs/workflow.md) 和 [模板验证记录](docs/validation.md)。
