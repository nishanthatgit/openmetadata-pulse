# Demo Narrative

## 🎬 Title: "OpenMetadata Pulse: Govern Where You Work"
## Target Length: 2–3 minutes

---

## Opening Hook (15 seconds)
"OpenMetadata is the central nervous system of your data. But notifications shouldn't mean context-switching. Meet OpenMetadata Pulse: a standalone app that brings OM governance and alerts directly to where your team already lives—Slack."

## Demo Flow (90 seconds)

### Scene 1: Intelligent Event Routing (30s)
*   **Action**: Switch to OpenMetadata UI. Change the owner of table `dim_customers` to a specific Slack user (demonstrator). Then, apply a "PII.Sensitive" tag to a column.
*   **Action**: Switch immediately to Slack.
*   **Result**: Slack pings. A beautifully formatted Block Kit message arrives in the user's DM. 
*   **Script**: "Instead of blasting a `#general` channel, Pulse catches the OM Webhook, queries the MCP for the table owner, and routes the schema change alert directly to me. Noise reduced to zero."

### Scene 2: NL Queries via Slack Bolt (30s)
*   **Action**: In Slack, in a team channel, type `@Pulse how many tests failed in the ecommerce database today?`
*   **Result**: Pulse shows a "thinking" indicator, then returns a summarized list using the LangChain Agent.
*   **Action**: Type `@Pulse show me the upstream lineage for fact_sales`.
*   **Result**: Pulse returns an ASCII/Markdown lineage tree.
*   **Script**: "Data stewards don't need to learn OpenSearch DSL. They just ask the Pulse bot. Under the hood, we are using the official `data-ai-sdk` to execute exactly what is needed."

### Scene 3: The Pulse Dashboard (30s)
*   **Action**: Open `localhost:5173` (Community Dashboard).
*   **Result**: Show the React GUI heavily branded with OM colors. It shows a live feed of the Slack events and a pie chart of "Ownership Coverage".
*   **Script**: "Data leaders need a bird's-eye view. The Pulse dashboard consumes the same backend infrastructure via SSE, showing team health and governance burn-down charts in real time."

## Value / Architecture Slide (15 seconds)
*   Show Architecture Diagram.
*   **Script**: "Built strictly separated: Slack Bolt, FastAPI Webhooks, Smart Router, and the official data-ai-sdk. Track T-05. Team Data Dudes."
