# 书稿、问题与解答的工作流

书稿是唯一的问题陈述来源。`BookProblem` 的三个参数分别是稳定 ID、目录标题、原始 TeX 陈述。解析器按根文件的静态 `\input{...}` / `\include{...}` 读取所有章节，处理嵌套花括号和注释。输入路径均相对根 TeX 所在目录；条件编译的多个替代输入、宏计算路径、verbatim 中的伪输入以及重复 input 不在这个轻量解析器的支持范围。需要这些形式时，应先扩展解析器并增加测试；不要让它静默漏掉问题。

| 状态 | 含义 | 原问题会被替换吗 |
| --- | --- | --- |
| open | 没有候选解答 | 否 |
| candidate | 解答已保存，尚无有效审校 | 否 |
| needs_work / rejected | 此候选有缺口或不成立 | 否 |
| review_stale | 审校后相关输入发生变化 | 否 |
| partial | 已核实一个部分解答 | 否 |
| resolved | 完整解答当前有效并可纳入此分支 | 是 |
| verified_pending_revision | 成稿后已核实，等待提案分支纳入 | 否 |

候选元数据和完整证明保留在 `research/solutions/ID/`，审校报告保留在 `research/reviews/`。读写分工由命令实现：writer/editor 使用 workspace-write，reviewer 在新 CLI 会话中使用 read-only，结构化输出由 CLI 宿主保存。写作 agent 不准批准自己的结果。模板可以保存人工审校报告，但 approved 字段和 SHA-256 是一致性记录，不是身份认证或形式证明。

云端宿主或外部独立 reviewer 可用 `review-prepare` 导出固定输入的 prompt，再用 `review-record` 登记实际返回的 JSON；CLI 审校与此入口共用格式、范围、当前指纹和覆盖项验证。分工仍要求独立只读审校；导入命令不会自行检查 reviewer 的身份。详见 [Codex 云端说明](codex-cloud.md)。

审校通过必须完成陈述、证明、依赖、来源和第二遍通读。整书报告还要列明 PDF 布局是否实际检查；未能完成整书读取的 agent 应给出 needs_work 和下一章检查范围，而不是抽样后批准。大量书稿用 `research/editorial/revision-queue.json` 将连续的整章审阅拆成有限单元，在 STATUS 中记录实际范围；终审前核对全部输入是否覆盖。

长书的可执行入口是 `python3 scripts/bookflow.py agent review --unit book/chapters/01-foundations.tex --pages 4-12`。工作流先编译并渲染指定物理页，交给只读 agent 做格式检查。根文件、preamble、每个活跃递归输入都须有 current approved 的 chapter 报告；全书指纹一致才可合成终审，源文件改动使旧报告全部过期。60 页以上不直接运行无边界的整书审校；GitHub 短书审校步骤失败时保留已经完成的解答审校结果，长书使用逐单元流程。自动渲染页范围不能替你判断修改页是否齐全，审校必须明确实际覆盖范围。

源文件和 bibliography 指纹变化会令相关解答审批过期；已整合解答集合变化也会令整书终审过期。书稿需要重新审校时，旧 JSON 留在 Git 历史，不伪造一份“依然通过”记录。generated 文件在每次 sync/build 中重建；失效的旧解答会从 generated 目录移除。

指纹同时覆盖书中图像、样式与模板、构建配置和本机实际保留的参考资料/笔记。PDF 全文默认不公开提交，因此只在本机读取了这些资料的批准报告，若移到没有相同参考文件的环境，会保守地过期；不能用不同参考版本冒充同一审校输入。

完整解答在原问题的读者位置生成标准 proposition/theorem 及 proof，并保留 `prob:ID` 引用别名。该位置必须已经具备其所有证明依赖；审校 agent 必须检查这个阅读顺序。适合放到另一章的结果应由编辑 agent 在授权范围内重构章节、保留 ID、修复引用，再次审校。宏替换不自动修改其他章节的“此问题仍开放”等句子，这些全书调用检查属于编辑职责。

`make sync`、编译、提交 hook、默认分支 maintenance 构成自动同步入口；`make watch` 可显式开启本地即时同步。GitHub 自动审校只读来源，默认上传报告 artifact；只有使用者显式启用 PR 选项和对应权限后才提出维护 PR。自动化不会合并数学修改、重写作者内容或发布网站。完成书后 `make finish` 固定基线并切换 revision；新增的核实解答先处于 pending，只能在提案分支进入书稿。
