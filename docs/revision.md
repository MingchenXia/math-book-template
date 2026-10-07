# 成稿后的改书流程

此流程根据 [SGPT 的 AGENTS.md](https://github.com/MingchenXia/SGPT/blob/main/AGENTS.md) 组织：数学内容必须做成可审核的分支和 PR，作者审批与 agent 审校分开。SGPT 的个人主页目标和已有书稿样式不写死进通用模板。

1. **完成基线。** 整书通过当前完整审校后运行 `make finish`。命令再次构建 PDF，保存源/PDF 指纹、已解决问题集合和逐章 revision queue，phase 改为 revision。更新 STATUS 与 CHANGELOG，将基线提交到 main。这个动作表示开始成稿修订流程，不证明本书所有问题已解决。
2. **开始提案。** 先保留当前修改，同步 main：`git pull --ff-only`。运行 `python3 scripts/bookflow.py revision-start fix-estimate`。命令要求工作树干净、位于 main，创建 `revision/fix-estimate`，不会复制未提交更改或强制重置分支。
3. **完整修改。** 修改定义、假设、结论、证明、例子或计算前，恢复其依赖链。检查被调用的前置结果和所有后续调用。只记录实际改动；读过但保留的正确段落不是“修正”。在 `revision-queue.json` 将该单元从 pending 改为 editing、reviewed，再到 author_pending，notes 写实际读取范围和报告。每章含递归输入、前后过渡、图和来源。写作/编辑 agent 可运行 `make edit`。
4. **复核与 PDF。** `make review` 会构建当前书稿并开始独立只读审校。修复实质问题后再审校。然后运行 `python3 scripts/bookflow.py revision-prepare --base main --pages 12-15,29 --summary "实际修正内容"`。pages 是 PDF 的物理页号，须包含每个改动处及足够上下文。命令保留完整 PDF，提取改动页，生成 diff、待作者审批的提案记录和 PR 正文。检查片段覆盖是否完整，必要时附 before PDF；自动提取不能判断你是否漏选了修改页。若基线另有自己的版式，保留该模板和实际所需的 TeX engine。
5. **提出 PR。** 审阅 diff 和文件列表，提交全部源修改、实际 CHANGELOG 和提案记录。`build/` 中的 PDF 不入源提交。推送提案分支后使用正文文件建立 PR：

   ```sh
   git add book bookflow.json research references/references.bib CHANGELOG.md
   git diff --cached
   git commit -m "Explain the substantive correction"
   git push -u origin revision/fix-estimate
   gh pr create --base main --head revision/fix-estimate --title "Explain the substantive correction" --body-file build/revision/fix-estimate-pr.md
   ```

   在 Codex 对话中附上 PR 和可以点击的 PDF 片段；通过 Codex 工具创建 PR 后必须调用 attach_artifact。其他合作者可下载此 PR 的 `Book checks` artifact 查看对应完整 PDF；其 build manifest 绑定当前源。提供影响章节、简短说明和不确定点。上传 PDF 到 PR 时确认对应当前提案，而非旧编译。
6. **等待作者批准该版本。** 作者须明确同意当前 PR 和 PDF；把批准的版本/源指纹与证据记录在 PR 对话或受控发布记录。禁止因为 agent approved、CI 成功、作者未回复或旧提案已批准而直接合并。审批后发生实质变化，重新提供 PDF 并重新取得批准。单纯修订队列更新不能替代批准。
7. **合并与发布。** 批准后按作者当前授权合并 PR，同步 main，确认已合并 source fingerprint 对应批准版本，再构建和检查 PDF。此模板仅提供 CI PDF artifact，没有自动主页发布；使用者应先指定出版目标和版本命名，再在已授权范围内发布。作者要求暂不发布时保留本地/CI PDF。网站部署完成须单独核实。
8. **清理与继续。** 确认 PR merged，远程提案分支已删除（可启用 GitHub 自动删除）；本地切到同步 main，检查无未合并工作后 `git branch -d revision/fix-estimate`，禁止用 `-D` 丢弃未合并工作。更新 queue 为 completed 和 STATUS 中的下一单元。不要将完成一章误报为整书修订完成。

提交 hook 会阻止成稿阶段在非 revision 分支提交 book/solutions/references 源文件。它是协作提示，可被绕过；应结合 main 分支保护、必需 PR 和作者 code review 使用。自动目录/审校 PR 不具有数学提案的合并授权。
