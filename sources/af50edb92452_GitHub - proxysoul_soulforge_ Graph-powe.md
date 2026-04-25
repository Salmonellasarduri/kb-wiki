# GitHub - proxysoul/soulforge: Graph-powered code intelligence, multi-agent coding with codebase-aware AI. No more grep & pray · GitHub

Source: https://github.com/ProxySoul/soulforge


> proxysoul/soulforge: Graph-powered code intelligence, multi-agent coding with codebase-aware AI. No more grep & pray


Every AI coding tool starts blind. It reads files, greps around, slowly builds a mental model of your codebase. You wait. You pay. The agent is doing orientation work, not real work.
SoulForge already knows. It builds a live dependency graph on startup and keeps it updated as you work. The agent knows which files matter, what depends on what, and how far an edit will ripple before it writes a single line.
Result: ~2x fewer steps, ~2x lower cost on the same tasks. The agent spends time on real work, not figuring out where things are.
|
Graph of every file, symbol, and import, ranked by importance, enriched with git history, updated in real-time. The agent never wastes a turn orienting itself. Learn more |
Extracts exactly the function or class it needs by name. A 500-line file becomes a 20-line extraction. 33 languages supported. Learn more |
|
Parallel explore, code, and web search agents with shared cache. One agent's discovery reaches others instantly. Learn more |
Context state is tracked as the conversation happens. When it gets long, compaction fires instantly, often with zero LLM cost. Learn more |
|
LSP, ts-morph, tree-sitter, regex fallback chain. Dual LSP backend, works with or without the editor open. Learn more |
|
|
Opus for planning, Sonnet for coding, Haiku for cleanup. 20 providers built-in. Task router gives full control. |
Your config, your plugins, your LSP servers. The AI edits through the same editor you use. |
|
Connect to any Model Context Protocol server. stdio, HTTP, SSE transports. Auto-reconnect, namespaced tools. Learn more |
13 hook events (PreToolUse, PostToolUse, SessionStart, etc.). Claude Code compatible, drop in your existing |
|
Installable domain-specific capabilities with approval gates. Browse and install from the community registry with |
Up to 5 concurrent sessions with per-tab models, file claims, and git coordination. Learn more |
Even more
- User steering type while the agent works, messages inject mid-stream. More
- Lock-in mode hides narration, shows only tool activity and final answer
- Inline images pixel-perfect images and animated GIFs in chat via Kitty graphics protocol
- 24 themes Catppuccin, Dracula, Gruvbox, Nord, Tokyo Night, and more. Custom themes with hot reload. More
- Code execution sandboxed Python for data processing and calculations
- 100 slash commands Full reference
macOS and Linux. First launch offers to install Neovim and Nerd Fonts if missing.
brew tap proxysoul/tap && brew install soulforge
Other install methods
Bun (global):
bun install -g @proxysoul/soulforge
Prebuilt binary:
# Download from https://github.com/ProxySoul/soulforge/releases/latest
tar xzf soulforge-*.tar.gz && cd soulforge-*/ && ./install.sh
Build from source:
git clone https://github.com/ProxySoul/soulforge.git && cd soulforge && bun install
bun run dev
soulforge # launch, pick a model with Ctrl+L
soulforge --set-key anthropic sk-ant-... # save a key
soulforge --headless "your prompt here" # non-interactive
See GETTING_STARTED.md for a full walkthrough, or the full docs for everything.
| SoulForge | Claude Code | Codex CLI | Aider | |
|---|---|---|---|---|
| Codebase awareness | Live dependency graph with ranking | File reads + grep | MCP plugins | Tree-sitter + PageRank |
| Cost optimization | Surgical reads + instant compaction + shared cache + model mixing | Auto-compaction | Server-side compaction | - |
| Code intelligence | 4-tier fallback, dual LSP, 33 languages | LSP via plugins | MCP-based LSP | Tree-sitter AST |
| Multi-agent | Parallel dispatch with shared cache | Subagents + Teams | Multi-agent v2 | Single |
| Editor | Embedded Neovim (your config) | No | No | No |
| Providers | 20 + custom | Anthropic only | OpenAI only | 100+ LLMs |
| License | BSL 1.1 | Proprietary | Apache 2.0 | Apache 2.0 |
Verified April 2026. Report inaccuracies.
Anthropic · OpenAI · Google · xAI · Groq · DeepSeek · Mistral · Bedrock · Fireworks · MiniMax · Codex · Copilot · GitHub Models · Ollama · LM Studio · OpenRouter · LLM Gateway · Vercel AI Gateway · Proxy · any OpenAI-compatible API
Set a key and go: soulforge --set-key anthropic sk-ant-...
or export ANTHROPIC_API_KEY=sk-ant-...
Provider setup guide · Custom providers
| Architecture | System overview, agent tiers, intelligence router |
| Repo Map | Graph ranking, co-change analysis, blast radius |
| Commands | All 100 slash commands |
| Headless Mode | CLI flags, JSON output, CI/CD |
| Configuration | Config files, task router, custom providers |
| Themes | 24 themes, custom themes, hot reload |
| MCP Servers | Model Context Protocol integration |
| Copilot Provider | Setup and legal review |
Business Source License 1.1. Free for personal and internal use. Commercial use requires a commercial license. Converts to Apache 2.0 on March 15, 2030.
