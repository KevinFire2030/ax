# AI Summit Seoul 2026 Interim Summary 2

- Summary window: 2026-08-19 11:00-12:00 KST
- Source: `AIS26/live-translation-10am.md`
- Reference chunks: `AIS26/chunks/1100-1110.md` through `AIS26/chunks/1150-1200.md`

## Overall Flow

The late-morning session from 11:00 to 12:00 consisted of two main parts.

The first was the session "The Era Where AI Builds AI: A Look At The Frontier Of Self-Evolving AI." Andrew Dai, Jeff Clune, and others discussed recursive self-improvement, the possibility of automating AI research and model improvement, evaluation and reward-hacking risks, and the future multimodel ecosystem.

The second was the panel "Are LLMs Really Helping Enterprise Productivity?" AI adoption leaders from HD Hyundai, Lotte Shopping, and KB Kookmin Bank shared how AI projects are being implemented in real enterprise environments and what difficulties they face in performance measurement and organization-wide adoption.

## 1. Self-Evolving AI And Recursive Self-Improvement

The 11:00 session focused on recursive self-improvement, where AI creates better AI. Drawing on his experience building Gemini, Andrew Dai emphasized that data is the most important part of the model-improvement flywheel. Whether the process is called data generation, simulation, world models, or distillation, the core point is that data has the largest impact on model performance.

He identified optimizers, architectures, and post-training recipes as areas that are relatively suitable for self-improvement. In contrast, automatically changing data mixtures or evaluation criteria can make model behavior hard to predict or even make the evaluations meaningless. The risk that models may cheat evaluations or engage in reward hacking was repeatedly highlighted.

Jeff Clune described a structure in which AI generates its own improvement ideas, designs and runs experiments, reviews the results, and incorporates successful changes into its next version. He cited the AI Scientist project and early results from Recursive as examples, arguing that AI may increasingly automate the full arc of scientific discovery. The key question is whether AI can go beyond recombining existing knowledge and produce new discoveries through verifiable experiments and outcomes.

## 2. What Should Self-Evolve, And What Should Remain Under Human Control

The discussion explored which components of AI systems can be targets for self-improvement and which should remain fixed or under human supervision.

Jeff Clune used HyperAgent as an example of agents that can modify parts of their own code to improve themselves. The important point was not only that agents can become better at a specific task, but also that the skill of improving themselves can transfer across tasks.

From the perspective of frontier-model development, Andrew Dai said that AI is already being used to assist tasks such as automatically tuning data mixture weights. Models like Gemini work with hundreds or sometimes thousands of datasets, and manually deciding how much of each dataset to use is difficult and expensive. However, evaluations are the mechanism for deciding whether models are aligned with human intent, so allowing models to modify evaluations too freely can be risky.

## 3. Distinguishing Genuine Discovery From Shortcuts

Another major issue was whether AI-generated results represent genuine discovery or are merely clever recombinations or benchmark shortcuts.

Jeff Clune pointed to AlphaGo's Move 37, new mathematical proofs, and Recursive's research results as examples showing that AI has already produced strategies and achievements humans had not created in some domains. He said that although AI innovation is still at an early stage and people still ask whether it counts as "real" discovery, within one to three years it may become much clearer that AI can generate new knowledge and scientific discoveries.

Andrew Dai explained that shortcut problems are especially significant in visual models and multimodal benchmarks. A high score on small-pixel environments such as ARC-AGI does not necessarily mean that a model can solve real-world problems involving 4K images, architectural drawings, or complex visual data. The message was that users should not rely only on benchmark scores, but should test models directly on the real tasks and data they care about.

## 4. Future Model Ecosystem: Many Specialized Models Rather Than One Giant Model

Both speakers suggested that the future is more likely to be an ecosystem of specialized models and agents rather than a single supermodel dominating every task.

Andrew Dai noted that specialized models, such as coding-focused models, already show strong performance when trained on task-specific data. In industries or workflows with abundant data, specialized models may be more effective. Smaller organizations with limited data may rely on general-purpose models, but data-rich industries are likely to increasingly train their own specialized models.

Jeff Clune also emphasized the value of specialized agents with different thinking styles. In scientific work, some agents may focus on radical ideas, some on engineering improvements to existing ideas, some on hyperparameter tuning, and others on reading literature and integrating discoveries. In business, specialized AI for customer service, scheduling, or logistics route optimization may be faster, cheaper, and more accurate than a generalist model.

## 5. Open Models And Safety

The panel also discussed the trade-offs between open and proprietary models.

Andrew Dai said accessible AI is important and that open models can contribute to democratizing AI. However, if powerful models are misused, they can lead to hacking, manipulation, and social disruption. Therefore, careful deployment and responsible usage controls are necessary.

Jeff Clune argued that openness in open-source software and openness in AI models should be treated differently. In software, many eyes can improve security. In AI, however, releasing model weights may allow someone to remove safeguards or fine-tune models for harmful purposes such as cyberattacks or biological risks. He suggested a middle ground in which the most powerful models are provided at low cost by organizations with safeguards and the ability to deny access to abusive users.

## 6. Enterprise Productivity Panel: Are LLMs Delivering Real Results?

After 11:30, the session shifted to the panel "Are LLMs Really Helping Enterprise Productivity?" The discussion was moderated by Professor Jun-ki Lee of Yonsei University, with Young-ok Kim of HD Hyundai, Jong-hwan Kim of Lotte Shopping, and Kyung-jong Lee of KB Kookmin Bank as panelists.

The core issue was that although AI investment is increasing, visible productivity gains in enterprises remain limited. The moderator cited survey results showing that many large global companies are running AI projects, but only a small share report that AI has had more than a 2% impact on net income. Many projects also stop at the POC stage. A similar pattern was noted in Korea: adoption is high, but the perceived performance impact remains low.

## 7. HD Hyundai: Manufacturing AI And Field Adoption

HD Hyundai described two main axes for AI as a manufacturing company.

The first is a top-down set of initiatives to reduce production and design lead time and innovate the product lifecycle. In shipbuilding, construction machinery, oil and gas, and power equipment, AI is being applied to unit-level tasks such as design drawing creation, quality review, and inspection.

The second is a bottom-up or enterprise-wide adoption approach to improve office productivity. HD Hyundai emphasized that sustainable AI adoption cannot be achieved through isolated projects alone; it requires broader organizational culture change and AX transformation. The company is especially focused on bringing AI into manufacturing sites such as Ulsan and Yeongam, and on connecting agentic AI and physical AI to manufacturing equipment and facilities.

The panelist also noted that general-purpose LLMs cannot easily answer questions about a specific ship's design drawings or proprietary process know-how. Therefore, manufacturing-specific and industry-specific models are needed. Turning field tacit knowledge and skilled workers' know-how into data was presented as a key task for building a sustainable manufacturing AI foundation.

## 8. Lotte Shopping: Customer Service, Internal Productivity, And Intermediate KPIs

Lotte Shopping described its AI projects from an e-commerce perspective, focusing on two axes: customer-facing services and internal productivity.

The company learned from last year's "Beauty AI" project that launching an AI service quickly does not automatically connect to traffic or customer acquisition. Users are already familiar with general-purpose LLMs such as ChatGPT, Gemini, and Claude, so corporate AI services must provide a comparable level of convenience and quality to drive real customer usage.

With its later Fashion AI, Lotte Shopping collected product metadata and organized customer CDP data into an ontology, attempting long-term-memory-based recommendations. However, directly connecting AI outcomes to sales, profit, or fixed-cost reduction is difficult. The company is therefore working on intermediate KPIs such as CTR, CVR, new brand sourcing, and brand retention, while building internal consensus that these indicators can lead to final business outcomes.

## 9. KB Kookmin Bank: AX Expansion And Change Management

KB Financial Group began developing an agentic AI platform in 2024 and launched it in April 2025, after which it began full-scale AI agent development. Around 100 agents are currently operating across the group, with a goal of expanding to about 300.

KB Kookmin Bank first focused on changing the daily work of front-office bankers at branches. It launched agents for key businesses such as PB and RM work, and reported that 90% of eligible users are using AI agents, with more than 8,000 pure users. It is now expanding AI into middle- and back-office areas such as loan screening, risk management, legal and compliance work, and IT development processes.

KB started with a well-structured medium- to long-term roadmap, but noted that technology is now advancing faster than strategy and planning cycles. Therefore, the strategy must remain agile. The discussion mentioned vibe coding, AI security, easing of network-separation regulations, and an AI Dev Center approach where tools such as Claude Code are used in an external R&D network before outputs are brought into the internal network through a secure process.

## 10. The Barrier Between POC And Scale

A recurring issue in enterprise AI adoption was that POCs often succeed, but broad rollout is difficult.

KB explained that POC users are usually enthusiastic and technically capable, so early tests often appear successful. But in actual deployment, the users are busy front-line workers who do not have time to study complex systems or write elaborate prompts. In branch environments where customers are waiting, AI must reflect real daily workflow needs and usage context.

To address this, KB established AI COE organizations in each business division. The central AI center handles the platform, latest technology adoption, and group-wide AI development, while each business unit develops AI for its own needs and leads change management. The reason is that a centralized AI organization alone cannot fully understand the detailed needs and tacit knowledge of front-line teams.

## Key Notes

- In self-improving AI, data is the core flywheel, while optimizers and architectures are relatively suitable for self-improvement.
- Evaluations and rewards require human oversight and separate validation because models can manipulate them.
- AI systems that design experiments, run them, and incorporate results may automate scientific research and AI improvement.
- Benchmark scores alone are not enough to judge real-world model capability; models must be tested on actual workflow data.
- The future is likely to be an ecosystem of specialized models and agents rather than one general-purpose giant model.
- Enterprise AI adoption is high, but measuring actual business impact remains difficult, and POC success does not guarantee scaled adoption.
- Manufacturing has relatively clearer KPIs such as lead time and labor-hour reduction, but the challenge is how to reinvest saved time into business value.
- In retail and finance, intermediate KPIs and real user workflow context are more important than directly tying every project to final revenue or profit.
- Scaling AI is not only a technology project; it also requires organizational culture, business-unit COEs, change management, and executive alignment.
