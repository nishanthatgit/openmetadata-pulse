# AI Disclosure — OpenMetadata Pulse

> **Transparency statement**: This document discloses all AI technologies used in both the **runtime operation** and **development** of OpenMetadata Pulse, as required by the OpenMetadata Community Hackathon 2025 rules.

---

## 🤖 AI in the Product (Runtime)

OpenMetadata Pulse uses AI to power its **natural language Slack bot** — enabling data teams to query metadata using plain English instead of navigating the OM UI.

### Model

| Property | Value |
|----------|-------|
| **Provider** | [OpenAI](https://openai.com) |
| **Model** | `gpt-4o-mini` |
| **Usage** | Natural language → structured metadata queries |
| **API** | OpenAI Chat Completions API |

### Frameworks & SDKs

| Framework | Purpose | Link |
|-----------|---------|------|
| **LangChain** | LLM orchestration — prompt chaining, tool selection, output parsing | [langchain.com](https://langchain.com) |
| **`data-ai-sdk[langchain]`** | OpenMetadata MCP tool integration — exposes 12 OM tools (search, lineage, entity details, etc.) to the LLM | [PyPI](https://pypi.org/project/data-ai-sdk/) |
| **`slack-bolt`** | Slack Bot SDK — receives `/pulse` commands, posts Block Kit responses | [slack.dev](https://slack.dev/bolt-python/) |

### How AI Is Used at Runtime

1. User sends `/pulse ask "which tables have no owner?"` in Slack
2. `slack-bolt` receives the command and passes it to the **AI Query Engine**
3. **LangChain** constructs a prompt and asks **GPT-4o-mini** to select the appropriate MCP tools
4. **`data-ai-sdk`** executes the selected tools against the OpenMetadata API (e.g., `search_metadata`, `get_entity_details`, `get_entity_lineage`)
5. GPT-4o-mini formats the tool results into a human-readable response
6. The bot posts the response as a rich **Slack Block Kit** message

### Data & Privacy

- **No training**: User queries and metadata are **not** used to train any AI models
- **No persistence**: Queries are processed in real time and not stored by the AI provider beyond their standard API retention policy
- **API key**: The OpenAI API key is provided by the deploying organization and billed to their account
- Refer to [OpenAI's Usage Policies](https://openai.com/policies/usage-policies) for details

---

## 🛠️ AI in Development

The following AI tools were used as **coding assistants** during the development of this project:

| Tool | Usage |
|------|-------|
| **GitHub Copilot** | Code autocompletion and suggestion |
| **Claude (Anthropic)** | Code review, documentation drafting, architecture discussion |
| **ChatGPT (OpenAI)** | Debugging assistance, research, and brainstorming |

### What AI Did NOT Do

- AI did **not** autonomously write or commit code without human review
- All AI-generated suggestions were reviewed, tested, and validated by team members
- Architectural decisions were made by the team, not by AI
- All tests were designed and verified by humans

---

## 📋 Summary

| Category | AI Used | Details |
|----------|---------|---------|
| **Runtime — NL Queries** | ✅ Yes | GPT-4o-mini via LangChain + data-ai-sdk |
| **Runtime — Notifications** | ❌ No | Rule-based webhook routing, no AI |
| **Runtime — Dashboard** | ❌ No | Direct API aggregation, no AI |
| **Development — Coding** | ✅ Yes | Copilot, Claude, ChatGPT as assistants |
| **Development — Testing** | ❌ No | Human-designed test suites |

---

<p align="center">
  <em>This disclosure is provided in compliance with the OpenMetadata Community Hackathon 2025 rules.</em>
</p>
