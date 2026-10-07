# 开放问题的解答

[手动提交完整或部分解答](../../docs/manual-entry.md#手动提交已经写好的解答) · [查看问题目录](../open-problems.md) · [元数据模板](../../docs/templates/solution.json) · [结果与证明模板](../../docs/templates/solution.tex)

已经在外部写好的解答，可以从仓库根目录用 `python3 scripts/bookflow.py solution-import --problem OP-002 --file work/answer.tex --scope full` 录入，也可在 GitHub 网页直接创建对应 ID 的两个文件。录入不会创建审校批准；完整步骤、更新既有解答、提交 PR 和成稿后的分支规则见上方手动入口。

每个稳定 ID 一个文件夹，例如 `OP-001/`，保留 `solution.json` 和完整的 `solution.tex`。后者使用本书的 `proposition/theorem/lemma/corollary` 与 `proof` 环境。仅允许自包含 TeX；新增问题放回章节。

元数据 `scope` 为 `full` 或 `partial`，`dependencies` 写内文标签，`references` 写单一 bibliography 中的 key。保存解答后执行：

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-001
make build
make review
```

完整解答经过独立审校，且指纹与当前输入一致后，`make sync` 在原问题位置自动纳入证明并保留 `prob:OP-001` 引用别名。部分解答不会替换原问题；编辑 agent 应在作者授权范围内手工整理已证特殊情形和精确剩余问题，并重新审校。不得直接修改 `book/generated/`。

一条候选被否定不等于问题已被反证解决；真正的反例解答也须完整陈述、证明、审校，并以 full 范围记录。问题的 ID 永不复用。
