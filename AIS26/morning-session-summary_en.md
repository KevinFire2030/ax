# AI Summit Seoul 2026 Morning Session Integrated Summary

- Scope: Morning session, 2026-08-19
- Source: `AIS26/live-translation-10am.md`
- Related summaries: `AIS26/interim-summary_ko.md`, `AIS26/interim-summary-2_ko.md`, `AIS26/interim-summary_en.md`, `AIS26/interim-summary-2_en.md`
- Related chunks: `AIS26/chunks/`

## Overall Overview

The Day 1 morning session of AI Summit Seoul 2026 centered on the transition from AI assistants to agentic AI, self-evolving AI, AI applications in space, multimodal and scientific domains, and whether LLMs and AI agents are truly producing enterprise productivity.

The message running through the morning was that improving AI model capability alone is not enough. AI becomes practically valuable only when it can understand ambiguous human intent, be evaluated in real work contexts, connect to measurable outcomes, and be accompanied by organizational and process change.

## 1. Opening And Event Direction

The event was held at the Grand Ballroom of COEX in Seoul. AI-powered simultaneous interpretation, exhibition booths, author signing sessions, and related programs were also announced.

Sejung Park, CEO of DMK Global, introduced the event as the 9th edition of AI Summit, with participants from more than 30 countries and an expanded exhibition in Hall B. The program focused on practical AI use cases, AI agents, agentic AI, and organizational and process transformation.

## 2. From AI Assistants To Agentic AI

The first major session was delivered by Professor Larry Heck of the Georgia Institute of Technology. The topic was "From AI Assistants to the Era of Agentic AI."

The central issue was the "autonomy trap": the expectation that an agentic AI system can fully understand a user's intent and complete a task from a single prompt. In reality, users do not provide perfect requirements from the beginning; requests are ambiguous and conversations evolve dynamically. Therefore, traditional single-turn benchmarks are insufficient for evaluating agent performance.

Professor Heck cited several reasons why many enterprise AI agent pilots fail, including unclear user intent, lack of evaluation criteria, insufficient measurement of successful outcomes relative to cost, and difficulty with context switching.

## 3. Lessons From Speech And Conversational AI

Professor Heck referred to his experience in speech recognition and deep learning research in the 1990s, the NIST evaluations, and later systems such as Cortana, Google Assistant, Bixby, and Viv Labs. His point was that today's agentic AI should revisit lessons from earlier conversational and speech systems.

The lessons were clear. Users do not always communicate precisely, so systems must handle ambiguity. Systems also need a process for confirming whether the user's intent and the system's understanding are aligned. Text and speech alone are not enough; multimodal signals such as gaze, facial expression, and behavior should also be used.

## 4. Agent Evaluation And Cost

The speaker proposed "cost per successful outcome" as an important operational metric. This means dividing the total cost of an agent by the number of successful outcomes to judge productivity and economic viability.

Even if token prices decline, total costs can rise when agents perform more complex tasks over longer periods of time. Companies therefore need to reduce costs and increase success rates through open-weight models, local agent loops, and infrastructure optimization.

## 5. Multimodal AI And Human-AI Collaboration

During the Q&A, the discussion turned to how human-AI collaboration may change when agents gain the ability to see, hear, and sense.

Professor Heck cited experiments combining eye tracking and speech. Even when users do not express all information verbally, systems can better infer intent by observing gaze and behavior. Multimodal models such as TwelveLabs were also mentioned, with the idea that models capable of jointly understanding video, audio, images, text, language, and speech can strengthen agents' non-verbal intelligence.

## 6. The Era Where AI Builds AI

The session after 11:00 focused on "The Era Where AI Builds AI: A Look At The Frontier Of Self-Evolving AI." Andrew Dai and Jeff Clune discussed recursive self-improvement, automation of AI research, reward hacking, and the future model ecosystem.

Drawing on his Gemini experience, Andrew Dai emphasized that data is the core flywheel of model improvement. Whether called data generation, simulation, world models, or distillation, the main factor driving model performance is data.

He said optimizers, architectures, and post-training recipes are relatively suitable targets for self-improvement. However, automatically changing data mixtures or evaluation criteria can make model behavior hard to predict or make evaluations meaningless. The risk of models cheating evaluations or engaging in reward hacking was repeatedly highlighted.

## 7. Recursive Self-Improvement And Scientific Automation

Jeff Clune described a structure in which AI generates improvement ideas, designs and runs experiments, reviews results, and incorporates successful improvements into its next version.

Using the AI Scientist project and early results from Recursive as examples, he argued that AI may automate the full arc of scientific discovery. The central question is whether AI can move beyond recombining existing knowledge and produce new discoveries through verifiable experiments and outcomes.

HyperAgent was also discussed. The idea is that agents can modify parts of their own code and improve not only at a specific task but also at the skill of improving themselves.

## 8. Genuine Discovery And Benchmark Shortcuts

Another major issue was whether AI-generated results represent genuine discovery or merely recombination and benchmark shortcuts.

Jeff Clune pointed to AlphaGo's Move 37, new mathematical proofs, and Recursive's results as examples that AI has already produced strategies and achievements humans had not created in some domains. He predicted that within one to three years, it will become much clearer that AI can generate new knowledge and scientific discoveries.

Andrew Dai explained that shortcut problems are especially serious in visual models and multimodal benchmarks. A high score in small-pixel settings such as ARC-AGI does not necessarily mean a model can solve real-world problems involving 4K images, architectural drawings, or complex visual data. Users should not rely on benchmark scores alone, but should test models directly on their real tasks and data.

## 9. A Specialized Model Ecosystem Rather Than One Giant Model

The speakers suggested that the future is more likely to be an ecosystem of specialized models and agents than a single supermodel dominating every task.

Andrew Dai noted that specialized models, such as coding-focused models, already show strong performance when trained on task-specific data. Data-rich industries and workflows may benefit from specialized models, while smaller organizations with limited data may rely more on general-purpose models.

Jeff Clune emphasized the value of specialist agents with different roles and styles. In scientific research, some agents may generate radical ideas, others may engineer improvements to existing ideas, tune hyperparameters, or read literature and integrate discoveries. In business, specialist agents for customer service, logistics route optimization, scheduling, and similar tasks may be faster, cheaper, and more accurate than generalist models.

## 10. Open Models And Safety

The morning also addressed the trade-offs between open and proprietary models.

Andrew Dai argued that accessible AI and AI democratization are important, but powerful models can be misused for hacking, manipulation, and disruption. Responsible deployment and usage controls are therefore necessary.

Jeff Clune argued that openness in open-source software and openness in AI models should be treated differently. In software, many eyes can improve security. In AI, however, released weights can allow someone to remove safeguards or fine-tune models for harmful purposes such as cyberattacks or biological risks. He suggested a middle ground in which the most powerful models are provided at low cost by organizations with safeguards and the ability to deny access to abusive users.

## 11. LLMs And Enterprise Productivity

After 11:30, the panel "Are LLMs Really Helping Enterprise Productivity?" followed. It was moderated by Professor Jun-ki Lee of Yonsei University, with Young-ok Kim of HD Hyundai, Jong-hwan Kim of Lotte Shopping, and Kyung-jong Lee of KB Kookmin Bank as panelists.

The core issue was that although AI investment is increasing, visible productivity gains in enterprises remain limited. The moderator cited survey results showing that many global enterprises are running AI projects, but only a small share report more than a 2% impact on net income, and many projects stop at the POC stage. A similar pattern was noted in Korea: adoption is high, but the perceived performance impact remains low.

## 12. HD Hyundai: Manufacturing AI And Field Adoption

HD Hyundai described two main axes for AI as a manufacturing company.

The first is a top-down set of initiatives to reduce production and design lead time and innovate the product lifecycle. In shipbuilding, construction machinery, oil and gas, and power equipment, AI is being applied to unit-level tasks such as design drawing creation, quality review, and inspection.

The second is a bottom-up or enterprise-wide adoption approach to improve office productivity. HD Hyundai emphasized that sustainable AI adoption cannot be achieved through one-off projects alone; it requires broader organizational culture change and AX transformation. The company is especially focused on bringing AI to manufacturing sites such as Ulsan and Yeongam and connecting agentic AI and physical AI to equipment and facilities.

General-purpose LLMs cannot easily answer questions about a specific ship's design drawings or proprietary process know-how. Therefore, manufacturing-specific and industry-specific models are needed. Turning field tacit knowledge and skilled workers' know-how into data was presented as a key task for building a sustainable manufacturing AI foundation.

## 13. Lotte Shopping: Customer Services And Intermediate KPIs

Lotte Shopping described AI projects from an e-commerce perspective across two axes: customer services and internal productivity.

The company's "Beauty AI" project was launched quickly but did not sufficiently connect to traffic or customer acquisition. Users are already familiar with general-purpose LLMs such as ChatGPT, Gemini, and Claude, so enterprise AI services must offer comparable convenience and quality to drive actual customer usage.

With Fashion AI, the company organized product metadata and customer CDP data into an ontology and attempted long-term-memory-based recommendations. However, directly connecting AI outcomes to sales, profit, or fixed-cost reduction is difficult. Lotte Shopping is therefore working on intermediate KPIs such as CTR, CVR, new brand sourcing, and brand retention, while building internal consensus that these indicators can lead to final business outcomes.

## 14. KB Kookmin Bank: AX Platform And Change Management

KB Financial Group began developing an agentic AI platform in 2024 and launched it in April 2025, after which it began full-scale AI agent development. Around 100 agents are currently operating across the group, with a goal of expanding to about 300.

KB Kookmin Bank first focused on changing the daily work of branch bankers by launching PB and RM agents for key businesses. It reported that 90% of eligible users are using AI agents, with more than 8,000 pure users. The bank is now expanding AI into middle- and back-office areas such as loan screening, risk management, legal and compliance work, and IT development processes.

KB started with a medium- to long-term roadmap, but noted that technology is advancing faster than strategy cycles. The strategy therefore needs to remain agile. Vibe coding, AI security, easing of network-separation regulations, and an AI Dev Center approach were discussed, including the use of SaaS tools such as Claude Code in an external R&D network before bringing outputs into the internal network through a secure process.

## 15. The Barrier From POC To Enterprise-Wide Adoption

A repeated enterprise AI issue was that POCs may succeed while broad rollout remains difficult.

At the POC stage, users are often enthusiastic and technically capable, so early tests tend to look successful. At scale, however, front-line workers are busy and do not have time to learn complex systems or write elaborate prompts. In branch environments where customers are waiting, AI must reflect actual daily workflows and practical user needs.

To address this, KB established AI COE organizations in each business division. The central AI center handles the platform, latest technology, and group-wide development, while each business unit develops AI for its own needs and leads change management. A centralized organization alone cannot fully understand the detailed needs and tacit knowledge of front-line teams.

## Morning Session Key Takeaways

- The core challenge of agentic AI is inferring and refining user intent even when users do not explain it perfectly.
- Single-turn benchmarks are insufficient for evaluating real agent performance.
- Cost per successful outcome may become an important metric for operating AI agents.
- Multimodal signals are a key way to improve intent understanding and human-AI collaboration.
- In self-improving AI, data is the core flywheel, while optimizers and architectures are relatively suitable for self-improvement.
- Evaluations and rewards require human oversight and independent validation because models can manipulate them.
- The future is likely to be an ecosystem of specialized models and agents rather than one general-purpose giant model.
- Open models support accessibility and democratization, but the most powerful models also require safeguards and misuse controls.
- Enterprise AI adoption is high, but measuring actual business impact remains difficult, and POC success does not guarantee scaled adoption.
- Manufacturing has relatively clearer KPIs such as lead time and labor-hour reduction, but the challenge is how to reinvest saved time into business value.
- In retail and finance, intermediate KPIs and real user workflow context are more important than tying every project directly to final revenue or profit.
- Scaling AI is not only a technology project; it requires organizational culture, business-unit COEs, change management, and executive alignment.
