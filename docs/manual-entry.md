# 手动添加开放问题和解答

| 我要做什么 | 明确入口 | 会修改什么 |
| --- | --- | --- |
| 查看 open problem list | [当前问题目录](../research/open-problems.md) | 只读，每条有稳定 ID、状态、书稿位置和解答入口 |
| 新增一个开放问题 | `problem-add`，或把 [问题模板](templates/problem.tex) 加到活跃章节 | 章节的 `BookProblem` 与自动目录 |
| 手动提交已写好的完整/部分解答 | `solution-import`，或上传 [解答模板](templates/solution.tex) 和 [元数据模板](templates/solution.json) | `research/solutions/<ID>/`，等待独立审校 |
| 把通过审校的解答纳入书稿 | 独立 `solution-review` / `review-prepare`，登记实际报告后 `make build` | 自动目录与原问题位置的生成正文 |

可以直接把问题或解答交给 Codex，让它按这里的命令录入。录入是保存你提供的数学内容；不能把“我认为已解决”自动改成审校批准。

## 新增开放问题

1. 查看 [问题目录](../research/open-problems.md)，选择未使用过的稳定 ID。已经解决的 ID 也不能复用。
2. 把完整问题陈述保存为仓库内的 TeX 文本，例如 `work/statement.tex`，写明假设、结论和适用范围；文件只放陈述和所需公式，不带 `BookProblem`、document 或章节命令。
3. 从仓库根目录运行（替换示例 ID、标题、文件和目标章节）：

```sh
python3 scripts/bookflow.py problem-add \
  --id OP-003 \
  --chapter book/chapters/02-questions.tex \
  --title '新的问题标题' \
  --statement-file work/statement.tex
make check
make build
```

命令把 `BookProblem` 加到目标活跃章节末尾，并同步问题目录。它拒绝重复 ID、非活跃章节、根文件、路径越界和不平衡花括号。新增后检查读者位置；若应出现在某定义或结果后，可以将整个宏移到该章节的适当位置，再 `make sync && make check && make build`。命令不替你确认问题是否在文献中仍开放。

**仅用 GitHub 网页编辑**：打开对应 `book/chapters/*.tex`，把 [问题模板](templates/problem.tex) 的 ID、标题和陈述替换后加入适当位置。提出 PR 后，要求 Codex 或本地执行 `make sync`，把生成的 `research/open-problems.md/json` 一并提交；Actions artifact 中的目录不会自动写回仓库。不要直接改生成的 open problem list。

## 手动提交已经写好的解答

先找到问题的稳定 ID，并保留章节里原来的 `BookProblem`。将你写好的结果与完整证明保存为仓库内文件，例如 `work/answer.tex`。文件使用 `proposition/theorem/lemma/corollary` 和 `proof` 环境，不带整个 LaTeX document；格式可参考 [解答模板](templates/solution.tex)。

```sh
python3 scripts/bookflow.py solution-import \
  --problem OP-002 \
  --file work/answer.tex \
  --scope full \
  --dependency def:compactness
make check
make build
```

`--scope full` 表示你提交的是整个问题的解答；只解出一个特例或部分结论，使用 `--scope partial`。内文依赖可重复写 `--dependency label`，参考文献可重复写 `--reference bib-key`；文献条目仍统一存入 `references/references.bib`。登记这些字符串不代表已经核实其内容。

命令创建 `research/solutions/OP-002/solution.tex` 与 `solution.json`，同步目录，不生成 approved 报告。新解答成为 candidate；不会因上传成功就标记 resolved。文件夹已存在时默认拒绝覆盖：可直接修改该目录的文件，或显式添加 `--replace` 导入替代版本；先通过 Git 保存要保留的旧稿。旧审校报告保留，相关输入变化会使它过期。

**仅用 GitHub 网页上传**：用 **Add file → Create new file** 创建 `research/solutions/<ID>/solution.json`，按 [元数据模板](templates/solution.json) 设置正确 ID、scope、依赖和文献；再在同一目录上传/创建 `solution.tex`，使用自己的完整结果与证明。更新已有解答时编辑已有目录。将两份文件和同步后的问题目录提交到一个 PR；不要手填 review JSON，不要修改 `book/generated/`。独立审校报告已有且对当前输入仍有效时，工作流继续认可该报告；手动上传本身不产生新的审批。

## 审校、纳入书稿和提交

有已登录 CLI 时：

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-002
make build
make review
```

在 Codex Cloud 使用宿主 reviewer 时：

```sh
python3 scripts/bookflow.py review-prepare solution-review --problem OP-002
# 将输出的 prompt 交给独立、只读 reviewer，保存它实际返回的 JSON。
python3 scripts/bookflow.py review-record \
  --assignment build/review-packets/<命令输出的指纹>/assignment.json \
  --report build/cloud-review.json
make build
```

云端独立审校和整书检查见 [云端说明](codex-cloud.md)。完整解答通过当前输入的独立审校后，`make sync/build` 在原问题位置自动纳入结果和证明，并把状态改为 resolved；部分解答保留未解决状态。仍须检查其他章节中“尚未解决”等旧说法、受影响推论和阅读顺序，检查 PDF，再完成相应书稿审校。

在 `CHANGELOG.md` 记录实际修改与检查，更新 `research/STATUS.md`，把目标章节（若有修改）、`research/solutions/<ID>/`、实际审校报告（若已完成）和 `research/open-problems.md/json` 一并提交。**未审校候选也可以先保存到仓库**，但不能声称已被本书核实。`work/` 输入文件与 `build/` 产物无需提交。

成稿后的 `phase=revision` 中，先运行 `python3 scripts/bookflow.py revision-start <提案名称>`，再添加问题或解答。新增完整解答只在 `revision/*` 提案分支纳入书稿；作者检查当前修改处 PDF 并明确批准后才合并。参见 [完整改书流程](revision.md)。
