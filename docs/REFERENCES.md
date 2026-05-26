# References used for this draft

These references were used to align MCP-Cortex with the current MCP ecosystem as of May 22, 2026.

- Model Context Protocol specification, version 2025-11-25. The spec describes MCP as a JSON-RPC based protocol for sharing context, exposing tools/capabilities, and building composable integrations and workflows.
- MCP Security Best Practices. The security guidance highlights confused-deputy risks, per-client consent requirements, redirect URI validation, state parameter validation, and related controls.
- 2026 MCP Roadmap. The roadmap emphasizes transport scalability, agent communication, governance maturation, and enterprise readiness.
- SEP-2567 Sessionless MCP via Explicit State Handles. This informed the MCP-Cortex decision to use explicit state handles rather than hidden sessions.
- MCP Transports documentation. This informed the decision to avoid requiring a new transport and to preserve stdio/Streamable HTTP compatibility.
- User-provided critique, `Pasted text.txt`, which framed the key limitations: discrete request-response tool calling, bolted-on context, brittle natural-language discovery, insufficient effect/data-flow contracts, central-orchestrator assumptions, poor streaming/high-dimensional support, and lack of built-in self-improvement loops.
