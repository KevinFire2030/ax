# LiveTR 1610-1620

- Source: live-translation-track-b.md
- Window: 2026-08-19 16:10-16:20 KST
- Messages: 70

- 2026-08-19T07:10:13.409Z [ko] 여러분 모두 푹 쉬고 돌아오셨을까요?



- 2026-08-19T07:10:19.202Z [ko] 장시간 열정적으로 집중하며 함께해 주셔서 감사드립니다.



- 2026-08-19T07:10:23.739Z [ko] 그럼 저희 곧바로 다음 세션으로 이어가 보겠습니다.



- 2026-08-19T07:10:37.775Z [ko] 이번에는 NVIDIA의 플랫폼 아키텍트인 Michael Albada님께서 ‘AI 에이전트를 넘어 AI 엔지니어로: 실전 투입 가능한 멀티 에이전트 시스템 만들기’를 주제로 강연해 주시겠습니다.



- 2026-08-19T07:10:43.665Z [en->ko] 너희 모두 마이클을 보니?
  Original: Are you also Michael? Okay, now let's welcome our speaker with a warm round of applause.



- 2026-08-19T07:10:48.563Z [ko->] 큰 박스 부탁드리겠습니다.
  Original: 큰 박수 부탁드리겠습니다.



- 2026-08-19T07:10:58.579Z [en->ko] 안녕하세요, 여러분.
  Original: Good afternoon, everyone. It is such a joy, a privilege, and an honor to be joining you here today.



- 2026-08-19T07:11:07.589Z [en->ko] 이것은 제가 한국에 온 두 번째입니다.
  Original: This is my second time in Korea, and every time, I'm just so inspired by the diligence, resilience, conscientiousness, and creativity.



- 2026-08-19T07:11:10.282Z [en->ko] 이 나라의, 그래서 여기 있는 것이 정말 좋다.
  Original: So it's great to be here.



- 2026-08-19T07:11:17.683Z [en->ko] 오늘 발표하게 되어 매우 기쁩니다.
  Original: And I'm very happy to be presenting today on "From Experiment to Production: Principles for Building Enterprise AI Agents."



- 2026-08-19T07:11:28.981Z [en->ko] 우리는 오늘 ~에 대한 멋진 강연들을 들었습니다
  Original: We've heard some great talks today about interactive video agents, security operations data, and I'm really going to be focusing on enterprise agents.



- 2026-08-19T07:11:31.589Z [en->ko] 지금부터 가장 큰 가치를 제공하기 위해.
  Original: And how to deliver the most value from them.



- 2026-08-19T07:11:36.280Z [en->ko] 잠깐 자기소개를 하자면, 저는 플랫폼입니다.
  Original: So, for a little bit of background, I'm a platform architect at NVIDIA.



- 2026-08-19T07:11:47.538Z [en->ko] 특히 칩 설계를 위한 AI에 관해서.
  Original: Particularly on AI for chip design focused on GPUs, I'm primarily focused on improving performance, efficiency, and reliability of the next generation of Feynman chips from NVIDIA.



- 2026-08-19T07:11:55.847Z [en->ko] 나는 ~의 저자입니다
  Original: I am the author of Building Applications with AI Agents, published by O'Reilly.



- 2026-08-19T07:12:00.237Z [en->ko] 번역되었다고 기쁘게 말할 수 있는
  Original: which I'm happy to say was translated and released in January by Hanbit Media here in Korea.



- 2026-08-19T07:12:14.466Z [en->ko] 그 이전에 한국에서는.
  Original: Prior to that, I spent two and a half years at Microsoft, where I worked in the cybersecurity division, training large language models to automate incident detection, vulnerability detection, and automated remediation.



- 2026-08-19T07:12:22.668Z [en->ko] 그리고 그 이전에 나는 4년을 보냈다.
  Original: And prior to that, I spent four years at Uber AI working on spatiotemporal forecasting, map predictions, and fraud detection.



- 2026-08-19T07:12:27.780Z [en->ko] 저는 파트타임 머신러닝입니다.
  Original: I am a part-time machine learning researcher. I have 50 citations.



- 2026-08-19T07:12:33.350Z [en->ko] 음, 10개의 특허이고 나는 바라
  Original: 10 patents, and I hold degrees from Stanford, Cambridge, and Georgia Tech.



- 2026-08-19T07:12:37.484Z [en->ko] 그러니까 내 시간을 위해서.
  Original: So for my talk today,



- 2026-08-19T07:12:40.363Z [en->ko] 세 개의 질문에 답할 예정입니다.
  Original: I'm going to answer three questions.



- 2026-08-19T07:12:44.722Z [en->ko] 우리가 어디에 있지요? 어디로 갈 거예요?
  Original: Where are we? Where are we going? And what can you do about it?



- 2026-08-19T07:12:53.958Z [en->ko] 제 강연의 전반부는 다룰 것입니다.
  Original: The first half of my talk will cover the current context, and the second half will focus on what you can do about it, structured around six principles.



- 2026-08-19T07:12:59.213Z [en->ko] 디자인하는 방법을 위해.
  Original: for how to design, measure, and deploy your production enterprise agents.



- 2026-08-19T07:13:12.262Z [en->ko] 그러면 시작합니다.
  Original: So to begin, model performance has improved dramatically staggeringly so for those of us who have been working in this field for some time.



- 2026-08-19T07:13:21.594Z [en->ko] 우리가 머리까지 감싸기조차 어려운 방식들
  Original: ways that are hard for us to even wrap our heads around. The model competition is absolutely fierce, and we have seen incredible leaps in performance.



- 2026-08-19T07:13:30.848Z [en->ko] 그리고 이걸 가로질러 바라보고 있다
  Original: And just looking across this one particular chart, you can see just how fierce the competition is.



- 2026-08-19T07:13:39.822Z [en->ko] 누가 꼭대기를 차지하나요
  Original: Whoever takes the top spot faces competition and regularly gets leapfrogged.



- 2026-08-19T07:13:46.613Z [en->ko] 매우 높은 끝에서. 그리고 당신은 심지어 볼 수도 있어요
  Original: And you can even see further down, there's a whole long tail of additional competitors who pursuing after them.



- 2026-08-19T07:13:59.702Z [en->ko] 그들을 쫓아가다.
  Original: One of the biggest shifts we've also seen is, just within the last year, a dramatic increase in the duration of tasks.



- 2026-08-19T07:14:03.938Z [en->ko] 프런티어 위에 구축된 에이전트를 사용하십시오.
  Original: These agents, built on top of frontier models, are capable of carrying out.



- 2026-08-19T07:14:15.801Z [en->ko] 그리 오래되지 않았어요. 아마도
  Original: It was not that long ago, perhaps a year ago, that we were stuck with prompts and responses. We were stuck with agents that could handle 30-second, one-minute, five-minute tasks.



- 2026-08-19T07:14:23.558Z [en->ko] 우리는 점점 더 보고 있다.
  Original: We are increasingly seeing agents that can carry out projects lasting multiple hours or even multiple days.



- 2026-08-19T07:14:26.049Z [en->ko] 그리고 계속해서 진전을 이루다.
  Original: and continuing to make progress.



- 2026-08-19T07:14:31.136Z [en->ko] 이것은 거대한 도약이다
  Original: This is an enormous leap that has really only happened in the last few months.



- 2026-08-19T07:14:41.658Z [en->ko] 그리고 근본적으로 어떻게 변하고 있다
  Original: and is fundamentally changing how we are capable of structuring work and I think it has huge implications for how we build, manage, and operate agents within the enterprise.



- 2026-08-19T07:14:48.970Z [en->ko] 그것도 중요합니다.
  Original: It's also important to remember that open-weight models are just behind this.



- 2026-08-19T07:14:53.520Z [en->ko] 그것은 생각하기가 어렵다.
  Original: And this is hard to think about. Training these models is so expensive.



- 2026-08-19T07:14:56.844Z [en->ko] 이것은 엄청난 자본 집약적입니다.
  Original: This is an incredibly capital-intensive enterprise.



- 2026-08-19T07:15:02.899Z [en->ko] 그들은 그렇게 생각할 것이다
  Original: One would think that the intelligence would be concentrated in just a small number of labs.



- 2026-08-19T07:15:09.138Z [en->ko] 하지만 우리가 실제로 보고 있는 것은
  Original: But what we're actually seeing is companies releasing incredibly capable open-weight models.



- 2026-08-19T07:15:12.837Z [en->ko] 이것들을 다운로드할 수 있고, 실행할 수도 있습니다.
  Original: You can download these and you can run them on your servers completely private.



- 2026-08-19T07:15:16.881Z [en->ko] 완전히 사적인.
  Original: This is putting incredible



- 2026-08-19T07:15:23.916Z [en->ko] 개척지에 가해지는 비용 압박.
  Original: cost pressure on the frontier labs, but it's very good for anyone who wants to use these models.



- 2026-08-19T07:15:28.798Z [en->ko] 건축하기에 더 좋은 시간이었다.
  Original: It's never been a better time to build and to ship.



- 2026-08-19T07:15:38.928Z [en->ko] 그리고 그건 단지 한 순간만을 의미하는 것이 아니다.
  Original: And that's not just one moment in time. You can see that these open-weight models are continuing to chase the true frontier.



- 2026-08-19T07:15:45.048Z [en->ko] 그리고 성능 차이.
  Original: And the difference in performance at any point in time has remained relatively small.



- 2026-08-19T07:15:52.062Z [en->ko] 그리고 복귀 시간.
  Original: And the duration back, you have to go to hit previous frontier performance is measured in months.



- 2026-08-19T07:16:01.556Z [en->ko] 은 개월 수로 측정됩니다.
  Original: You'll even see a similar distribution across model size.



- 2026-08-19T07:16:09.606Z [en->ko] 그래서 여기 꼭대기에.
  Original: So here in the top right, you can see that you get the best performance with the largest models.



- 2026-08-19T07:16:15.384Z [en->ko] 3조 개의 매개변수를 밀어내다.
  Original: pushing three trillion parameters, and I'm sure that number will continue to go up over time.



- 2026-08-19T07:16:25.815Z [en->ko] 하지만 당신은 볼 수 있어요
  Original: But you can see that even at 300 billion parameters, you get near-frontier performance.



- 2026-08-19T07:16:36.215Z [en->ko] 다음 전체 모델 반.
  Original: The next whole class of models, from 30 billion to 300 billion parameters, is very feasible for us to serve at a reasonable cost.



- 2026-08-19T07:16:41.855Z [en->ko] 이것은 ~의 일종의 지능이다
  Original: This is a type of intelligence that was unthinkable years ago.



- 2026-08-19T07:16:46.329Z [en->ko] 그리고 이제 이것은 안에 포장됩니다
  Original: And now this is packed into a very, very small number of parameters.



- 2026-08-19T07:16:53.956Z [en->ko] 이것이 의미하는 것은,
  Original: What this means is that intelligence is being concentrated in these parameters at a very high rate.



- 2026-08-19T07:16:58.070Z [en->ko] 지능의 가격이 하락하고 있다
  Original: The price of intelligence is falling, and it is approaching zero.



- 2026-08-19T07:17:06.886Z [en->ko] 그리고 당신은 놀라운 것을 가지고 있어요
  Original: And you have an incredible set of different models to choose from, enabling incredibly high levels of intelligence at low amounts of cost.



- 2026-08-19T07:17:14.561Z [en->ko] 낮은 비용으로.
  Original: I'll also note that there are many bad models that are far



- 2026-08-19T07:17:17.566Z [en->ko] 그 효율적 프런티어 아래에.
  Original: It is far below that efficient frontier.



- 2026-08-19T07:17:24.612Z [en->ko] 무엇을 선택할 때 사려 깊어지도록 돕다
  Original: To be thoughtful in choosing which model is going to give you the best performance for your set of criteria.



- 2026-08-19T07:17:32.382Z [en->ko] 그리고 이 차트에서 보듯이 우리는 또한
  Original: And you can see on this chart that we're also getting better at a technique called distillation.



- 2026-08-19T07:17:39.641Z [en->ko] 모델 증류.
  Original: Model distillation allows you to take a very large, very expensive model.



- 2026-08-19T07:17:46.361Z [en->ko] 그리고 훈련을 방출한다.
  Original: and emit training data from it that can be used to train a smaller model.



- 2026-08-19T07:17:51.581Z [en->ko] 이것을 통해 더 작게 만들 수 있습니다
  Original: This allows you to get small models that are almost as capable.



- 2026-08-19T07:17:54.367Z [en->ko] 더 큰 교사 모델로서.
  Original: as the larger teacher model.



- 2026-08-19T07:18:08.216Z [en->ko] 그리고 당신은 볼 수 있다
  Original: And you can see the distillation process results in models that, at much, much smaller form factors, are starting to approach that true frontier level of performance.



- 2026-08-19T07:18:12.519Z [en->ko] 우리가 전반에 걸쳐 지능으로 보고 있는 것은 무엇인가요
  Original: What we're looking at is intelligence across the full set of form factors.



- 2026-08-19T07:18:17.912Z [en->] 그리고 우리는 기대할 수 있다.
  Original: and we can expect that entire Pareto frontier to improve over time.

