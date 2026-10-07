# 审校记录

独立只读审校 agent 写入 JSON，格式见 `agents/review.schema.json`。报告绑定输入的 SHA-256，记录实际完成的检查范围。接受报告必须包含 statement、proof、dependencies、sources、second_pass，且没有 blocking 或 major 问题。

`source_sha256` 覆盖相关书稿、单一 bibliography、原问题与候选证明；书稿报告还覆盖实际整合的解答集合。相关内容变化自动作废旧结论。手动填写 approved 只是人为声明，不是可信的独立审校或形式验证。写作 agent 不得生成自己的批准报告。

同一个问题的当前报告在 `solution-<ID>.json`，整书报告在 `book.json`。Git 保存历史；不要篡改以前的验证范围。
