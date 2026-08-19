# Track D Session 3 Summary (English)

- Time: 2026-08-19 14:30-15:00 KST
- Track: D
- Session title: From Data to Execution: AI-Based Operational Optimization Strategy
- Speaker: Eunjung / Yunjung Choi, Coupang Ads (name spelling to be confirmed)
- Source transcript: [`tracks/D/live-translation-track-d.md`](./tracks/D/live-translation-track-d.md)

## One-Sentence Summary

Coupang Ads built an AI advertising consultant to transform manual sales operations, campaign analysis, diagnosis, prioritization, and personalized pitching into a scalable workflow that helps more advertisers grow with consistent consulting quality.

## Core Message

The session introduced Coupang Ads' journey of building an AI advertising consultant for its sales organization. The speaker emphasized that building an AI initiative in software is one thing, but turning it into a reliable business operation at product level is a very different challenge.

Coupang Ads serves not only large brands but also sellers and advertisers on Coupang, many of whom are small and medium-sized businesses. More than 70% of advertisers were described as SMEs. For these advertisers, advertising terminology such as impressions, clicks, conversions, CTR, CVR, and eCPM can be intimidating, and spending ad budget can feel risky. Coupang Ads' goal is to help these sellers understand advertising more easily and improve business outcomes.

## Problem Definition

Before the AI consultant, account executives gathered data from multiple internal tools, BI dashboards, CRM history, and personal sales experience to analyze campaigns and pitch strategies to advertisers. However, the number of advertisers and campaigns was too large for high-quality consulting to scale.

The scale was significant. An AE handling SMEs may manage up to 600 advertisers, while AEs handling larger advertisers manage around 60. The number of campaigns to analyze exceeded 283,000. Meanwhile, one AE could handle around 150 pitches per week, creating a gap of about 500 times between demand and available sales capacity.

The company already had ML-based recommendations and templates, but AEs did not always use them in practice. The reason was that static recommendations or templates often failed to match the advertiser's current context, communication style, or actual sales conversation. The speaker framed this as a problem of context, not simply a lack of data.

## Goals of the AI Advertising Consultant

The AI advertising consultant was designed to compress work that previously took hours into a single conversation and a process that runs in minutes. Its major goals included:

- Integrating campaign data from multiple tools into one view within one minute.
- Automating performance-drop diagnosis using structured diagnostic playbooks.
- Prioritizing which campaigns should be pitched first.
- Generating advertiser-specific pitch scripts and reports based on context and customer profile.
- Explaining expected performance improvement from recommended actions.
- Reducing quality differences across AEs and creating consistent consulting quality.

## System Architecture

The speaker described the AI consultant architecture in four major areas.

First, the user interface was designed as a chatbot embedded in existing ad center and sales tools, rather than as a separate application. This allowed AEs to use the system inside their existing workflow.

Second, the LLM solving layer included a data retrieval layer and an API layer. The team initially moved quickly by using available APIs and direct access to the data warehouse. Later, they implemented a more consistent data retrieval structure using ClickHouse MCP and schema-based access to fact tables.

Third, at the API level, the team built LangGraph-based agents and an operational server that included service modules such as quotas and logging.

Fourth, security and privacy risks such as prompt injection, PII, and sensitive data handling were managed through the Coupang AI Gateway. All inputs and outputs were monitored through logging systems. Accumulated data was preprocessed and filtered for supervised fine-tuning and direct preference optimization of open-source base models.

## Agent Workflow

The agent uses a ReAct-style orchestrator to route questions and decide tool calls. The workflow includes three main flows: detailed campaign diagnosis, data queries, and simple lookup responses. The most important part is the deep-dive pipeline for campaign diagnosis.

The pipeline first selects a campaign and checks whether diagnosis is needed based on performance data. It then gathers category-level information, benchmark data, keyword data, and other relevant signals as LLM input. The analyst stage uses more than 25 diagnostic playbooks to identify causes of performance decline. The recommender layer then matches the diagnosis with existing recommendation systems. Finally, the pitch layer creates a report through hybrid rendering, and an evaluator stage verifies numbers and outputs through regeneration loops if problems are detected.

## Key Design Principles

The most important design principle was that pipeline order and branching are handled deterministically by code, while the LLM focuses on analysis and judgment. The speaker argued that if the LLM controls the entire flow, the team loses control and cannot guarantee the output.

Recommendations were also not delegated entirely to the LLM. Coupang already had ML-based recommendation and prediction models with measurable accuracy and coverage, so the team chose to combine those assets with LLM-based diagnosis and explanation. Hybrid rendering was used to prevent hallucinated numbers, while numerical validation was handled by deterministic systems and evaluation loops.

## Results and Challenges

After the alpha launch, the biggest issues were cost and latency. Because the number of campaigns was very large, costs were high. Even after reducing hours of work to around ten minutes, users still said the process was too slow and asked for lower latency.

Through optimization, the team reduced cost by 62% and brought latency down from around seven minutes to about one minute and thirty seconds. The next goal is to reduce response time to under thirty seconds. The speaker emphasized that LLMs are used mainly for conclusions, narrative, issue summaries, and action recommendations, while numbers and calculations are controlled and verified by the surrounding system.

## Key Takeaways

- Successful AI adoption starts with understanding real workflows and operational context, not just building a model.
- The core sales problem was not lack of data, but lack of context-aware interpretation and execution strategy.
- LLMs can power automation, but deterministic systems should control sequence, branching, and validation.
- Combining existing ML recommendation assets with LLM-based analysis can create a more practical enterprise AI tool.
- Preventing hallucination requires system-level control over numbers, rendering, and evaluation.
- AI tools must optimize speed, cost, quality, and security together to become useful in real operations.
