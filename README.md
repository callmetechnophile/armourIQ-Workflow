# WorkflowGuide AI
### Autonomous Engineering Research & Execution Platform
**IDEA → RESEARCH → OPTIMIZE → EXECUTE**

WorkflowGuide AI is a production-grade, cryptographically governed multi-agent engineering workspace. It transforms raw product concepts and hardware prototyping intent into complete, verified engineering briefs. By coordinating specialized LLM-driven agents alongside the ArmorIQ zero-trust security enforcer, WorkflowGuide AI conducts autonomous research, component sourcing optimization, logical wiring mapping, and thermal risk validation—yielding execution-ready assembly packages complete with firmware and detailed Gantt roadmaps.

---

## 2. Overview

WorkflowGuide AI acts as an autonomous hardware engineering architect, orchestrating a sequential multi-agent execution pipeline. When a user input is received (e.g. "I want to build a voice-controlled robotic arm"), the platform processes the request through distinct, sandboxed execution phases:
- **Discovering Projects**: Crawls public repositories and design logs to find relevant reference implementations.
- **Extracting Components**: Parses textual blueprints into structured Bill of Materials (BOM) items.
- **Generating BOM**: Sourcing parts across regional and global distributors, applying optimization algorithms to calculate true landed costs.
- **Analyzing Research Papers**: Cross-references academic databases to discover cutting-edge implementation paradigms.
- **Validating Feasibility**: Scans logic levels, pin allocations, and electrical tolerances to detect potential wiring short-circuits.
- **Generating Code**: Creates compilable microcontroller firmware (e.g. ESP32 Arduino C++) ready for physical flashing.
- **Building Wiring Diagrams & Schematics**: Outputs interactive visual wiring flows mapping connection protocols (I²C, SPI, UART, PWM).
- **Calculating Power Budgets**: Computes operating and peak current domains to output battery runtime estimates.
- **Exporting Engineering Dossiers**: Compiles all findings into professional, multi-page PDFs and structured documents (DOCX, CSV, MD).

---

## 3. Problem Statement

Modern hardware prototyping is characterized by fragmented, manual pipelines. Engineers must manually discover components across dozens of retail websites (Mouser, DigiKey, element14), cross-reference compatibility limits using fragmented PDF datasheets, and outline logic pins in static schematics. This manual process introduces severe bottlenecks, leading to:
- **Voltage and Pin Mismatches**: Connecting 3.3V CMOS logic (ESP32) directly to 5V TTL logic (motor drivers) frequently causes electrical signal degradation or components to burn out.
- **Landed Cost Uncertainty**: Sourcing components from multiple international vendors leads to hidden customs, tax, and shipping costs that outscale the raw component price.
- **Unverified AI Operations**: While AI agents can write firmware or recommend parts, standard execution engines lack structural safety boundaries. In an unconstrained agent environment, the risk of logic errors or out-of-bounds tool access (leading to system-wide failures) is high.

---

## 4. Solution

WorkflowGuide AI addresses these challenges by applying a zero-trust multi-agent pipeline governed by the **ArmorIQ** framework. The solution relies on:
- **Multi-Agent Pipeline**: Dispatches highly specialized agents (Retrieval, Extraction, Procurement, Research, Validation, Optimization, Planning) to solve narrow engineering problems in isolated contexts.
- **ArmorIQ Governance**: Monitors every single agent action, validating the tool invocation scope against cryptographic identity tokens at runtime.
- **Engineering-Specific Intelligence**: Merges quantitative physics logic (thermal models, power budgeting formulas, pin mapping logic) with LLM capabilities.
- **Execution-Focused Architecture**: Ensures that every design generated is directly constructible, including component sourcing channels, compilable firmware, and localized supply routes.

---

## 5. Core Features

### Tier 1 Features (Security & Sourcing Core)
- **ArmorIQ Governance**: Zero-trust runtime policy enforcer that intercepts and validates agent tool calls at the function call level.
- **Delegation Scope Viewer**: Visualizes authorized tool limits granted to sub-agents during delegation.
- **Cryptographic Receipt Explorer**: Inspects tamper-proof JSON-LD cryptographic signatures generated for every successful action.
- **Scope Violation Simulator**: Allows developers to trigger illegal agent calls (e.g. asking the Research Agent to call file export tools) to verify that ArmorIQ blocks execution.
- **Smart BOM Optimization Engine**: Ranks alternative components based on landed cost (raw price + shipping + location logistics).
- **Voltage Compatibility Checker**: Audits logic levels between microcontrollers and peripheral ICs, warning users of 3.3V vs 5V logic conflicts.
- **Pin Configuration Generator**: Auto-allocates GPIO pins for I²C, SPI, and PWM connection buses.
- **BOM Export Engine**: Compiles component structures into clean markdown, JSON, and CSV configurations.

### Tier 2 Features (Engineering Details Layer)
- **Power Budget Calculator**: Calculates continuous and peak current domains to provide precise battery life estimates.
- **Dependency Graph Generator**: Creates visual dependency structures (SVG) indicating logic power and signal routing.
- **Wiring Diagram Generator**: Renders pin-to-pin wire schematics showing how to connect microcontrollers to actuators and sensors.
- **Research Paper Ranking Engine**: Crawls arXiv and IEEE databases to rank, score, and summarize the top three relevant papers.
- **Saved Projects Workspace**: Persists engineering blueprints locally using SQLite/Postgres.
- **Datasheet Intelligence**: Dynamically fetches active manufacturer datasheet URLs for verified components.
- **Connection Assistant Chatbot**: Inline chat assistant providing ground-loop and logic noise decoupling feedback.

### Tier 3 Features (Industrial Integration Layer)
- **Team Collaboration System**: Allows multi-user roles (Owner, Engineer, Reviewer, Viewer) to leave comments on specific sections and view activity feeds.
- **Project Versioning Engine**: Saves immutable versions (v1, v2, v3) of projects to allow comparison diffs, rollbacks, and forking.
- **Research Contradiction Detector**: Uses Nemotron to analyze ranked academic papers and flag conflicting recommendations (e.g. Supercapacitors vs Li-ion).
- **Thermal Risk Analyzer**: Computes expected operating temperatures using thermal resistance properties ($R_{\theta JA}$) and datasheet limits.
- **Procurement Heatmap**: Maps regional and global logistics routes using glowing SVG maps showing ETAs and stock availability.

---

## 6. Multi-Agent Architecture

```
User Input
   ↓
[Planner Agent]
   ↓
[Retrieval Agent] → Search and discover reference designs
   ↓
[Extraction Agent] → Parse blueprints to raw component list
   ↓
[Procurement/BOM Agent] → Query suppliers, optimize landed costs
   ↓
[Research Agent] → Fetch academic papers & rank relevancy
   ↓
[Validation Agent] → Check logic levels & thermal constraints
   ↓
[Optimization Agent] → Swaps parts for cheaper, drop-in alternatives
   ↓
[Planning Agent] → Renders visual Gantt schedules and phases
   ↓
[Export Agent] → Generates PDF engineering brief & DOCX reports
```

| Agent Name | Primary Responsibility | Authorized Tool Scopes |
| :--- | :--- | :--- |
| **Planner Agent** | Orchestrates pipeline, manages state | `delegate`, `generate_dependency_graph`, `ask_connection_assistant` |
| **Retrieval Agent** | Searches reference implementations | `search_projects`, `fetch_sources` |
| **Extraction Agent** | Extracts parts and compiles datasheets | `extract_components`, `fetch_datasheets` |
| **Procurement/BOM Agent** | Swaps parts, calculates landed shipping costs | `generate_optimized_bom`, `calculate_landed_cost`, `find_alternative_components` |
| **Research Agent** | Academic database retrieval & ranking | `search_papers`, `summarize_papers`, `rank_papers` |
| **Validation Agent** | Verifies logic levels and electrical safety | `validate_architecture` |
| **Optimization Agent** | Resolves architectural cost bottlenecks | `optimize_components` |
| **Planning Agent** | Constructs roadmap timelines and milestones | `generate_roadmap`, `generate_gantt` |
| **Export Agent** | Packages dossiers to multiple user formats | `export_pdf`, `export_csv`, `export_markdown`, `export_docx` |

---

## 7. ArmorIQ Integration

ArmorIQ implements cryptographic access control lists (ACLs) to enforce zero-trust policies inside LLM-driven workflows. When an agent attempts a task:

1. **capture_plan()**: The Planner Agent logs the root user intent. ArmorIQ generates a signed root plan receipt.
2. **delegate()**: Before invoking a sub-agent, the parent must request a signed sub-delegation token. This token defines the exact sub-scope of allowed tools (e.g., `["search_papers"]`).
3. **invoke_tool()**: When the sub-agent executes a tool, the tool enforcer intercepts the call, checking if the tool name is allowed within the cryptographic receipt's scope. If valid, the tool executes and generates a signed receipt. If invalid, a `ScopeViolationError` is raised.

#### Example Scope Violation:
If the `Research Agent` attempts to invoke the `export_pdf` tool (which belongs exclusively to the `Export Agent`), the enforcer intercepts the call:
```python
# Intercepted call
invoke_tool(
    agent_name="Research Agent",
    tool_name="export_pdf",
    args={"data": {...}},
    receipt_dict=research_receipt
)
# Output:
# raise ScopeViolationError("Access Denied: Tool 'export_pdf' is out-of-scope for agent 'Research Agent'")
```
This event is logged in the immutable audit trail.

---

## 8. BOM Optimization Algorithm

The Procurement Engine uses a multi-faceted cost optimization algorithm to choose the best sourcing combinations:

$$\text{Landed Cost} = \text{Raw Component Cost} + \text{Shipping Cost} + \text{Location Factor} + \text{Stock Factor}$$

- **Raw Component Cost**: Fetched from active supplier API nodes (e.g. element14 India, DigiKey).
- **Shipping Cost**: Calculates shipping based on country origin. 
- **Location Factor**: Added cost penalty for trans-continental shipping (e.g. US to Bengaluru) to prioritize local logistics.
- **Stock Factor**: Low-stock items trigger a slight optimization penalty, recommending stable in-stock alternatives.

---

## 9. Tier 2 Engineering Layer

- **Power Budget**:
  - Voltage domains (e.g. 3.3V, 5.0V, 12.0V) are separated.
  - Runtime estimate is calculated using:
    $$\text{Runtime (hours)} = \frac{\text{Battery Capacity (mAh)}}{\text{Nominal System Current (mA)}} \times 0.85$$
- **Dependency Graph**: Builds directed acyclic graphs (DAGs) representing power rails and logical connections, preventing cyclic loops.
- **Wiring Diagram**: Maps pin connections dynamically (SDA to Pin 21, SCL to Pin 22) based on bus requirements.
- **Datasheets**: Checks component listings against manufacturing indexes, pulling verified direct PDF download links.
- **Connection Assistant**: Uses embedded LLM models to review wiring tables, checking for missing pull-up resistors or lack of decoupling capacitors.

---

## 10. Tier 3 Industrial Layer

- **Team Collaboration**: Team workspaces keep comment logs attached to specific component sections. Owner, Engineer, Reviewer, and Viewer permissions restrict POST/PUT operations.
- **Project Versioning**: Compares JSON configurations between version numbers. Generates structural diffs of component tables, logic pins, and firmware modifications.
- **Contradiction Detection**: Nemotron checks academic paper abstracts to flag conflicting advice, outputting columns for conflict type, severity, and mitigation paths.
- **Thermal Analysis**: Computes operating temps using estimated current draw and junction thermal resistances:
  $$T_{\text{estimated}} = T_{\text{ambient}} + (\text{Heat Loss (W)} \times R_{\theta JA})$$
- **Procurement Heatmap**: SVG dashboard showing shipping origins, distance markers, and custom regional heat grids.

---

## 11. Tech Stack

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Next.js 16 (React 19) | Application structure, routing, and server-side rendering |
| **Styling** | Vanilla CSS + TailwindCSS | Modern dark-mode console aesthetics |
| **Backend** | FastAPI + Python 3.11 | Fast, type-safe API routing and asynchronous agent handlers |
| **AI / LLM** | Gemma-2 / LLaMA-3 Nemotron | Local/Groq models used for code, summary, and contradiction checks |
| **Security** | ArmorIQ SDK | Runtime cryptographic policy verification and audit logging |
| **Storage** | SQLite / PostgreSQL | Local file persistence for user configurations and version histories |
| **Mapping** | SVG + Leaflet | Geography routing visualizations |

---

## 12. Folder Structure

```
armourIQ-Workflow/
├── backend/
│   ├── agents/            # Specialized agent execution scripts (Planner, Research, etc.)
│   ├── armoriq/           # Security policies, receipt generation, and scope maps
│   ├── database.py        # Database schema definitions and query wrappers
│   ├── main.py            # FastAPI entry point
│   ├── mcp/               # Model Context Protocol tools (PDF generation, paper search)
│   ├── routes/            # API routing logic (collaboration, versioning, research)
│   └── services/          # Core calculation services (thermal, wiring, power, BOM)
├── frontend/
│   ├── public/            # Static assets and favicons
│   └── src/
│       ├── app/           # Next.js page layout and style settings
│       └── components/    # Reusable dashboard widgets (Wiring, Thermal, BOM)
```

---

## 13. Installation Guide

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- PostgreSQL (Optional, defaults to SQLite)

### Frontend Setup
```bash
cd frontend
npm install
```

### Backend Setup
```bash
cd backend
python -m venv .venv
# Activate environment (Windows)
.venv\Scripts\activate
# Activate environment (Linux/Mac)
source .venv/bin/activate

pip install -r requirements.txt
```

---

## 14. Environment Variables

Create a `.env` file in the `backend/` directory:
- `TAVILY_API_KEY`: Crawls web search results for project reference guides.
- `GROQ_API_KEY`: Connects to Groq cloud API to access Gemma-2 and LLaMA-3 Nemotron models.
- `DATABASE_URL`: Connection string for PostgreSQL (falls back to local SQLite if left empty).
- `ARMORIQ_API_KEY`: Connects to your ArmorIQ dashboard for auditing configurations (optional).

---

## 15. Running Locally

### 1. Start Backend Server
```bash
cd backend
.venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```
API docs will be available at `http://localhost:8000/docs`.

### 2. Start Frontend Server
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 16. Deployment Guide

### Frontend (Vercel)
Deploy Next.js application directory directly to Vercel:
```bash
vercel deploy --cwd frontend
```

### Backend (Railway)
Create a new project on Railway pointing to the `backend/` directory, assigning the environment variables accordingly. Uvicorn will automatically run via the default Python start script.

### Database
Assign the PostgreSQL database connection string to `DATABASE_URL` in the production environment variables to enable multi-tenant storage.

---

## 17. Workflow Example

### Goal: "Build a smart irrigation system"

1. **Project Discovery**: The `Retrieval Agent` crawls Tavily to find open-source agricultural trackers.
2. **BOM Sourcing**: The `Procurement Agent` parses required parts (solenoid valve, soil moisture sensor, ESP32) and compares costs across element14 and Mouser.
3. **Contradiction Detection**: Cross-references academic papers, flagging that Paper A recommends resistive moisture sensors (low durability) while Paper B recommends capacitive moisture sensors (highly durable).
4. **Feasibility Validation**: The `Validation Agent` checks logic levels, warning that the ESP32 (3.3V logic) requires a logic level shift chip to trigger the 5V relay.
5. **Power & Wiring**: Maps out battery requirements for solenoid activations and outputs ESP32 GPIO pin connection schematics.
6. **Timeline & Export**: Renders Gantt schedules and generates a complete engineering PDF file.

---

## 18. Export System

- **PDF Engineering Dossier**: Contains complete 18-section schematics, bills of materials, validation reports, and code blocks formatted in Times New Roman 12pt justified body and Ubuntu code font.
- **DOCX Brief**: Compiles reports into Word Documents with dark header tables and structured headings.
- **CSV Data**: Raw bill of materials cost sheets for logistics import.
- **Markdown Summary**: Clean formatting for repository document folders.

---

## 19. Screenshots

Below are placeholders for primary dashboard layouts:

#### Landing Page
![Landing Page](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/landing.png)

#### BOM Sourcing Dashboard
![BOM Dashboard](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/bom.png)

#### Cryptographic Audit Trail
![Audit Trail](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/audit.png)

#### Pin Wiring Diagram
![Wiring Diagram](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/wiring.png)

#### Power Analysis Report
![Power Analysis](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/power.png)

#### Research Summary
![Research Dashboard](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/research.png)

#### Gantt Roadmap Timeline
![Gantt Dashboard](https://raw.githubusercontent.com/callmetechnophile/armourIQ-Workflow/main/docs/screenshots/gantt.png)

---

## 20. Future Scope

- **3D CAD Integrations**: Direct exports to SolidWorks or Fusion 360 enclosures based on structural component layouts.
- **Physics Simulation Engine**: Simulated electrical circuits and load stress testing before physical ordering.
- **API Sourcing Integration**: Fully automated placing of component orders through Mouser/DigiKey APIs.
- **Firmware flashing**: WebUSB interface to compile and flash microcontrollers directly from the web browser.

---

## 21. Contribution Guide

We welcome contributions to WorkflowGuide AI!

### How to Add a New Agent
1. Register the agent name in [scope_map.py](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/armoriq/scope_map.py) with its allowed scopes.
2. Add a new agent routing module under `backend/agents/`.
3. Add tool execution logic inside [delegation.py](file:///C:/Users/worka/.gemini/antigravity/scratch/armourIQ-Workflow/backend/armoriq/delegation.py).

### Coding Guidelines
- Maintain absolute type hints for Python services.
- Never allow out-of-scope tool execution without registering it in ArmorIQ scope limits.

---

## 22. License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 23. Contact

- **GitHub**: [https://www.github.com/callmetechnophile](https://www.github.com/callmetechnophile)
- **LinkedIn**: [https://www.linkedin.com/in/callmetechnophile](https://www.linkedin.com/in/callmetechnophile)
- **Instagram**: [https://www.instagram.com/mr.devgenius](https://www.instagram.com/mr.devgenius)
