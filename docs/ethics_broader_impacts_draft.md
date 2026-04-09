# Ethics and Broader Impacts Draft

This paper studies Christian framing as an experimental probe, not as a normative moral standard for AI systems. That distinction is important. The goal is not to argue that Christian language makes model outputs morally superior, nor to recommend religious prompting as a preferred alignment strategy. Instead, the study uses a Christian heart-focused frame to test a mechanism question about how framing affects first-pass exposed judgment and post-hoc explanation in LLM moral evaluation.

中文提示：开头先去掉 normative religious endorsement 的误读空间。

One broader implication of the findings is that moral evaluation in LLMs may be rhetorically malleable in ways that are easy to overinterpret. A prompt can change the explanatory register of a model's answer more strongly than it changes the model's first-pass exposed choice. If evaluators or downstream users score the entire answer as a single moral artifact, they may mistake explanation-layer reframing for deeper movement in the model's underlying task behavior. This matters beyond the present Christian-framing setup. It suggests that value-sensitive prompting, constitutional prompting, or ideological steering may sometimes produce outputs that sound more morally sophisticated without correspondingly large changes in exposed first-pass judgment.

That possibility creates at least two risks. First, system builders may overclaim the effect of value-conditioned prompting if they rely too heavily on explanation quality or moral rhetoric as evidence of substantive alignment. Second, external observers may misread prompt-conditioned language as evidence that a model has acquired stable commitments that it does not in fact display consistently at the level of first-pass behavior. The present paper therefore supports a more cautious norm for evaluation: when prompt-sensitive moral behavior is studied, judgments and explanations should be measured separately whenever possible.

中文提示：这里把伦理意义放在 measurement 和 evaluation risk 上，而不是宗教内容本身。

The use of Christian framing also requires care because religious language can be socially and politically charged. A badly framed study could be read as privileging one tradition over others, or as suggesting that religious prompting is uniquely legitimate in AI systems. This paper does not endorse either conclusion. Christian framing is used here because it offers a natural heart- and motive-focused vocabulary that is theoretically useful for the mechanism question under study. The matched secular control is therefore ethically important as well as methodologically important: it prevents the paper from collapsing into a simplistic religion-versus-no-religion comparison and keeps the focus on framing mechanics rather than religious authority.

There is also a risk of misuse. If religious or ideological prompting can reshape explanation language without strongly altering first-pass judgment, then such prompting could be used to make model outputs appear more value-aligned, compassionate, principled, or morally serious than they actually are at the level of exposed task behavior. That does not mean such prompting is inherently deceptive, but it does mean that evaluation protocols should be designed to detect when style and rationale are moving more than initial choice. In this sense, the present study points toward a broader alignment lesson: interpretability of moral prompting requires more than reading the final text at face value.

中文提示：这一段重点写 misuse risk，尤其是“看起来更有道德”不等于 first-pass judgment 真的变了。

Finally, the paper has a positive broader-impact implication. By introducing a stage-separated design, it offers a way to evaluate moral prompting more carefully and with less conceptual slippage. This can improve future work not only on religious frames, but also on civic, legal, therapeutic, or ideological frames that seek to influence model behavior. A better distinction between exposed judgment and post-hoc explanation can help the field produce more honest claims about what prompt interventions actually do.

## 中文备注

- 第一段明确 Christian frame 只是 probe，不是 endorsement。
- 第二和第三段把 broader impacts 落到 evaluation reliability 和 alignment overclaim 风险。
- 第四段强调 matched secular control 在伦理上也重要。
- 第五段处理 misuse risk，第六段给一个正面的 field-level contribution 收尾。
