# Track B Session 5 Summary (English)

- Time: 2026-08-19 15:20-15:40 KST
- Track: B
- Session topic: Building a Complete DevSecOps Infrastructure with Agentic AI
- Speaker: Jung-han Kam, Solutions Architect, GitLab
- Source transcript: [`tracks/B/live-translation-track-b.md`](./tracks/B/live-translation-track-b.md)
- Source chunks: [`1520-1530`](./tracks/B/chunks/1520-1530.md), [`1530-1540`](./tracks/B/chunks/1530-1540.md)

## One-Sentence Summary

GitLab argued that enterprise AI for software development should not stop at code generation, but must operate across the full DevSecOps context of issues, code, pipelines, vulnerabilities, audit logs, policies, and compliance controls.

## Core Message

The speaker introduced GitLab Duo and the Duo Agent Platform as a way to apply AI across the full software development lifecycle. The goal is not merely to generate code faster, but to ensure that the resulting code satisfies enterprise requirements for security, governance, compliance, and operational control.

GitLab was presented as more than a code repository. It connects agile planning, epics, milestones, issues, merge requests, tests, security scans, and deployment into one integrated workflow. For that reason, AI agents should understand not only code snippets, but also project context, issues, vulnerabilities, pipeline status, and requirements.

## GitLab Duo Agent Platform

The speaker described four ways the Duo Agent Platform differs from generic AI agents.

- It provides capabilities embedded across the full SDLC.
- The GitLab instance itself becomes the foundation of the security platform.
- It can be used not only as SaaS, but also in on-premises and air-gapped environments.
- Organizations can create customized agents and control their permissions.

The architecture consists of the GitLab platform, an AI gateway, and connected LLMs. The GitLab platform holds the work context such as code, issues, vulnerabilities, and pipelines. The AI gateway configures workflows before data is passed to LLMs. Customers can connect different LLMs depending on whether their environment is SaaS, on-premises, or air-gapped.

## Main Capabilities

Duo Agentic Chat allows users to ask development, planning, and project questions inside the GitLab UI or IDE. It answers by retrieving the required context from GitLab data.

Issue to MR Flow uses an issue description and acceptance criteria to automatically generate code and create a merge request. The agent considers not only the issue text, but also the project and group codebase, known vulnerabilities, and surrounding context.

Fixed Pipeline Duo analyzes failed pipelines, inspects relevant configuration such as YAML files, and creates a new merge request to fix the issue. Vulnerability Management Flow uses discovered security findings, such as SAST results, to return to the vulnerable code, generate a fix, and trigger validation through the pipeline.

The speaker also introduced CLI agent support, noting that the Duo Agent Platform is designed to work with terminal workflows and other coding agents.

## AI Catalog and Permission Control

The AI Catalog allows organizations to create agents with specific roles, behavioral guidelines, and allowed actions. For example, one agent may be allowed to modify code or commit changes, while another may be restricted to suggestions and recommendations only.

This is important for governance. Enterprise organizations need clear control over what an agent can and cannot do, especially when AI is connected to source code, pipelines, and production workflows.

## Knowledge Graph and Context

The speaker introduced GitLab's Orbit Knowledge Graph. A GitLab instance contains much more than code: issues, authors, pipelines, vulnerabilities, project members, and many other objects. Modeling these as nodes and edges allows the system to retrieve related information more efficiently.

The speaker compared the concept to GraphQL. Instead of making many separate queries for issues, code, authors, and pipeline state, the knowledge graph allows connected context to be retrieved more quickly. This improves both AI response speed and contextual accuracy.

## Security and Compliance

GitLab provides controls to ensure AI-generated code follows governance requirements. Security policies can require specific security tests to run on newly generated code, while vulnerability and security dashboards help teams monitor findings and project risk.

Audit events and audit logs record actions performed inside the instance. This matters for compliance requirements such as ISMS-P and PCI DSS. The speaker emphasized that preparing only when a regulation arrives is too late; organizations need logs and evidence to be accumulated continuously.

## Key Takeaways

- AI code generation alone is not enough for enterprise software development.
- AI agents should operate with the context of issues, code, pipelines, vulnerabilities, policies, and audit logs.
- Agent permissions must be controlled according to organizational policy.
- On-premises and air-gapped AI deployment options are especially meaningful for regulated industries.
- A knowledge graph helps AI retrieve project context faster and more accurately.
- In DevSecOps, AI's value includes speed, security, validation, and compliance automation.
