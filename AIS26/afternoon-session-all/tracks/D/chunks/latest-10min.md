# LiveTR 1620-1630

- Source: live-translation-track-d.md
- Window: 2026-08-19 16:20-16:30 KST
- Messages: 8

- 2026-08-19T07:20:04.379Z [en->ko] 계속 가세요.
  Original: So here are some examples of taking a naive approach. An unconstrained frontier model actually has a lot of risks.



- 2026-08-19T07:20:10.043Z [en->ko] 그리고 우리가 발견한 가장 강력한 모델들조차도.
  Original: And even the strongest models we found, without the guardrails, fail in three pretty dangerous ways.



- 2026-08-19T07:20:22.293Z [en->ko] 첫 번째는 많은 주장이라는 것이다
  Original: So the first is that many claims these models make carry no source, right? So they just say something like, "Neoadjuvant cisplatin is a preferred approach. New immunotherapies show strong results," but we don't know where that came from.



- 2026-08-19T07:20:33.117Z [en->ko] 우리가 가지고 있는 많은 선택지들.
  Original: Many, many of the options that we see, you know, kind of have that issue. The second is hallucination of sources. So you can see that the snippet here shows an NIH source, but that's actually



- 2026-08-19T07:20:45.039Z [en->ko] 사실 완전히 가짜 인용입니다.
  Original: It's actually a completely fake citation, right? So it looks reasonable, but it's actually completely fake. And then the last one is that it might actually hallucinate evidence. So the 27% number is actually not real.



- 2026-08-19T07:20:52.605Z [en->ko] 어디선가 온 그거.
  Original: It doesn't really have enough context to be useful, so that's pretty dangerous.



- 2026-08-19T07:21:01.910Z [en->ko] 그리고 우리가 그 문제들을 어떻게 발견했는지.
  Original: And how we found those issues was through LLM-as-a-Judge scoring. So we essentially use other LLMs to keep the main LLM in check.



- 2026-08-19T07:21:17.815Z [en->ko] 그리고 우리는 이것을 여러 번 했습니다.
  Original: And we did this multiple times to make sure that we were able to catch these issues. And it's sort of a way to iterate and just make sure that your core LLM is kind of doing the right thing. We'll have another slide in this as well.

