# Codex 云端写书环境

本模板可以部署到当前 **Codex Cloud**。首次创建环境需要选择 GitHub 仓库、验证安装结果并点击 Publish；以后从 **Work in → Cloud** 选择已发布环境即可开始。当前官方流程没有在仓库中声明一个自动绑定账号并发布环境的按钮，不能把 Codespaces 按钮当作 Codex Cloud 部署入口。操作依据：[OpenAI 云端环境说明](https://learn.chatgpt.com/docs/environments/cloud-environments)。

## 首次配置

先用 **Use this template** 创建自己的书稿仓库。直接选择 `MingchenXia/math-book-template` 也可以试用，但新的书应保存到自己的仓库。

在 Codex 桌面或网页版新任务中选择 **Work in → Cloud → Select environment → Create environment**；也可从 **Settings → Codex Cloud → Environments** 创建。选择刚建立的 GitHub 仓库。尚未连接 GitHub 时，按界面完成连接并选择仓库。

点击 **Get started** 后，把下面这段发给环境配置 agent：

```text
请为选定的 math-book-template 衍生仓库配置数学写书环境。
从该仓库的 checkout 根目录运行 bash scripts/setup-codex-cloud.sh。
把经过实际测试的这条命令记录为 Install script；多个仓库时先 cd 到这个仓库。
安装使用仓库 .devcontainer/tex-packages.txt 中的 Debian/Ubuntu 软件包，
需要 Package managers 网络访问以下载官方系统包。
云端已有 Codex agent，不要求嵌套 CLI 登录，也不要求 OPENAI_API_KEY。
Start skill 按 docs/codex-cloud-start.md 设置，从本任务的仓库根目录检查环境并构建书稿。
验证 make doctor、make test、make sync、make check、make build，
确认 build/pdf/main.pdf 存在并报告物理页数。
只准备环境，保留示例候选的未审校状态，不产生虚构审校报告。
展示安装、测试和构建结果及需要保存的配置，供我检查并发布。
```

环境配置中的 **Allow Codex to access internet → Package managers** 覆盖这里的 Debian/Ubuntu 软件源。需要查论文时再添加所需网站；能访问网站不代表已经取得论文全文。查看安装报告并保存配置，点击 **Publish**；出现 **Environment published** 后即可开始写书任务。这些是 [当前官方创建、网络与发布步骤](https://learn.chatgpt.com/docs/environments/cloud-environments#create-and-publish-an-environment)。

安装脚本可以重复执行，已安装的软件包不会重新下载。它直接在云端机器安装 TeX、BibTeX/Biber、中文字体、Python 和 Poppler，随后配置 hooks、同步目录、运行测试和编译；无需 Docker。与 Codespaces 使用同一份系统包清单。`--verify-only` 只检查已准备的机器，不安装软件。安装失败时在环境配置对话中处理错误，再重试；安装成功不等于数学已经审校。

## 云端写作与独立审校

在新云端任务中直接让 Codex 依据 `AGENTS.md` 和 `agents/edit.md` 推进指定章节，再运行 `make sync && make check && make build`。云端宿主 agent 的账号不会自动成为嵌套 `codex exec` 的凭据；`make edit` 和 `make review` 仍是另行登录的 CLI 入口。云端使用下面的导出/登记入口，可复用宿主 agent，省去额外 CLI/API 配置。

给一个候选解答生成固定输入的审校任务：

```sh
python3 scripts/bookflow.py review-prepare solution-review --problem OP-001
```

整书或逐章审校：

```sh
python3 scripts/bookflow.py review-prepare review
python3 scripts/bookflow.py review-prepare review --unit book/chapters/01-foundations.tex --pages 4
```

命令输出 `build/review-packets/<指纹>/assignment.json` 和 `prompt.md` 的路径。书稿审校会先编译并生成 PDF 页图片。把 prompt 交给**独立、只读的 reviewer**；如果当前云端支持子 agent，可由写作任务委派新的只读 reviewer。否则用另一独立审校任务，检出同一分支与版本并重新生成 assignment。不能让写作 agent 自行填写 approved。需要审校任务访问的参考全文也必须在那个环境中可读。

独立 reviewer 按 `agents/review.schema.json` 返回 JSON；由宿主将实际返回内容原样保存到本仓库内，例如 `build/cloud-review.json`。登记时使用生成命令实际输出的 assignment 路径：

```sh
python3 scripts/bookflow.py review-record \
  --assignment build/review-packets/<指纹>/assignment.json \
  --report build/cloud-review.json
make build
```

登记会检查报告格式、范围、当前输入指纹与第二遍通读等覆盖项。旧版本或不完整批准会被拒绝；needs_work/rejected 保留问题，完整且有效的解答才自动进入书稿。JSON 和指纹是范围与一致性记录，不认证 reviewer 身份，也不替代数学审校。若工具不能查看 PDF，reviewer 必须明确记录缺失的布局检查，不能据此声称已完成终审。

开放问题目录、独立解答文件夹、参考文献目录和成稿后 `revision/*` 提案流程在云端保持相同。GitHub Actions 的自动 AI 审校仍是另一条执行路径；选择 Codex Cloud 不会给 Actions 自动提供 API key。

## 保存和更新

重要源文件通过 Git 提交并提出 PR；环境快照不代替 Git。当前云端新任务使用已发布环境的准备状态，已有任务保留自己的文件和工具，仓库刷新不会自动重跑安装。修改工具依赖后，从 **Settings → Codex Cloud → Environments → Edit** 请求重新安装、测试、保存并 **Republish**，再用新任务验证。详见 [官方环境状态说明](https://learn.chatgpt.com/docs/environments/cloud-environments#reuse-and-update-saved-state)。

本机个人 skills 不会自动同步到云端；模板的 `AGENTS.md`、`agents/` 与工作流脚本都保存在仓库，不需要私有 skill。不要把本机登录文件、API key 或未经许可分发的参考全文提交到公开书稿仓库。

如果账号中只有 **Codex Cloud (Legacy)** 的 Setup script 配置，可以使用同一条安装命令，但请按 [legacy 环境文档](https://learn.chatgpt.com/docs/environments/cloud-environment) 配置；它主要保留 Code Review 与 GitHub/Linear 集成，不应与当前 Cloud 环境的 Install script / Start skill 混用。
