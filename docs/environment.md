# 一键环境

优先用 GitHub Codespaces 或 VS Code 的 **Dev Containers: Reopen in Container**。`.devcontainer/Dockerfile` 安装 Node 22、Python、TeX、Biber、MakeIndex、Poppler 和 `@openai/codex@0.157.1`。容器用普通用户工作，不携带登录凭据。第一次启动自动执行 setup 和示例编译。容器配置机制见 [GitHub 官方说明](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)。

`bash start.sh` 优先使用已安装的本地工具；工具不全时用 Docker 构建同一个环境。它只准备环境和编译，不创建云服务或登录账号。Docker 命令模式结束后容器退出；需要完整编辑会话用 Dev Containers。容器基础镜像和 Debian 包使用维护中的版本标签，Codex CLI 固定版本；这是可重建的工具配置，并非字节级锁定的系统镜像。

本地 macOS 可用现有 MacTeX；Debian 可安装 Docker，或安装 Dockerfile 中列出的软件包。`make doctor` 检查缺少的命令和 TeX 文件。基本构建使用 pdfLaTeX；中文书把 `bookflow.json` 的 engine 改为 `xelatex`，main 的 class 改为 `ctexbook`，删除 preamble 中的 `fontenc/lmodern` 两行。容器已含中文字体与 ctex。保留 `book` 自有样式也可以，注意统一 theorem 和 bibliography 配置。

本地 agent 使用 `codex login`（沿用你自己的默认模型）；GitHub Actions 用 secret `OPENAI_API_KEY`，在临时容器内 `codex login --with-api-key`。登录会写用户的配置目录，不入 Git。CLI 调用参数来自实际 `codex exec --help`，结构化审校采用 `--output-schema`；可参考 [官方 CLI 文档](https://developers.openai.com/codex/cli/reference)。

默认 bibliography 后端是 BibTeX，便于兼容已有 TeX 安装；需要 Biber 时将 `bibliography_backend` 改为 `biber`，确保本机可执行相应版本。容器包含两者。修改后工作流自动清理旧后端的生成缓存，不降低 TeX 的文件写入限制。如果本机桌面配置的模型名不被独立 CLI 账号支持，可运行 `BOOKFLOW_CLI_DEFAULTS=1 make review`，仅对这次 CLI 使用其默认配置，保留登录且不改你的全局配置。

`scripts/setup.sh` 注册本仓库 `.githooks`，提交前同步目录并检查成稿分支规则。若已有自定义 hooks，先合并两个 hook；恢复默认可执行 `git config --unset core.hooksPath`。不要把新书放在另一个仓库内部并对外层仓库运行 setup。

生成的 PDF 和审阅片段都在 `build/`。LaTeX Workshop 自动构建默认关闭，因为 `make build` 需先更新生成的 TeX；使用 VS Code 的 **Book: build PDF** 任务。PDF 源对应关系以 `build/build-manifest.json` 为准。
