# AI Disclosure — OpenMetadata Pulse

> Transparency about AI usage in this project, as required by the OpenMetadata Community Hackathon 2025.

---

## 🤖 AI in the Product (Runtime)

| Component | AI Model | Purpose |
|-----------|----------|---------|
| **Slack Bot — NL Queries** | OpenAI **GPT-4o-mini** | Interprets natural-language questions from users (e.g., `/pulse ask "which tables have no owner?"`) and generates structured, sourced responses |
| **Tool Selection** | GPT-4o-mini via LangChain | Selects the appropriate OpenMetadata MCP tool (`search_metadata`, `get_entity_details`, `get_entity_lineage`) based on user intent |
| **Response Formatting** | GPT-4o-mini | Summarizes raw JSON API responses into human-readable Slack Block Kit messages |

### Frameworks & SDKs

| Library | Version | Role |
|---------|---------|------|
| `langchain` | ≥0.2 | Agent orchestration, prompt management, tool binding |
| `langchain-openai` | ≥0.1 | OpenAI LLM integration for LangChain |
| `data-ai-sdk[langchain]` | latest | OpenMetadata MCP client — provides 12 tools for metadata operations |
| `slack-bolt` | ≥1.18 | Slack app framework for receiving commands and posting messages |

### Data Flow

```
User (Slack) → /pulse ask "..." → slack-bolt → LangChain Agent → GPT-4o-mini
                                                    ↓
                                            Tool Selection
                                                    ↓
                                          data-ai-sdk (MCP)
                                                    ↓
                                          OpenMetadata API
                                                    ↓
                                        Structured Response
                                                    ↓
                                    GPT-4o-mini (summarize)
                                                    ↓
                                      Slack Block Kit Message
```

### Important Notes

- **No training on user data**: We use OpenAI's API (not fine-tuning). No metadata is used to train models.
- **No data storage**: Queries and responses are not persisted beyond Slack's own message history.
- **Prompt safety**: All user inputs are sanitized before being sent to the LLM. System prompts constrain the model to metadata-related tasks only.

---

## 🛠️ AI in Development (Build-time)

The following AI tools were used during the development of this project:

| Tool | Usage |
|------|-------|
| **GitHub Copilot** | Code autocompletion and boilerplate generation |
| **Claude (Anthropic)** | Architecture planning, code review, documentation drafting |
| **ChatGPT (OpenAI)** | Debugging assistance, API research, prompt engineering |

### What AI Helped With

- ✅ Boilerplate code generation (FastAPI routes, Slack handlers, React components)
- ✅ Writing and refining documentation (README, setup guides)
- ✅ Debugging and troubleshooting (Docker configs, async Python patterns)
- ✅ Prompt engineering for the Slack bot's NL query system

### What Humans Did

- ✅ All architectural decisions and system design
- ✅ Integration logic between OpenMetadata, Slack, and the dashboard
- ✅ Testing, validation, and quality assurance
- ✅ Project management, task coordination, and delivery

---

## 📋 OpenAI Usage Policy

This project complies with [OpenAI's Usage Policies](https://openai.com/policies/usage-policies). Specifically:

- We do not use the API for any prohibited use cases
- We do not attempt to extract training data from the model
- We provide clear disclosure of AI usage to end users
- The Slack bot identifies itself as AI-powered in its responses

---

## 📄 License

This disclosure is part of the OpenMetadata Pulse project, licensed under Apache 2.0.
