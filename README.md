# Sentro — AI Compliance Copilot

Sentro is a multi-agent AI system that automates Level-1 AML/KYC compliance triage for private banking, built for the Kaggle 5-Day AI Agents Intensive Capstone Project.

## Problem
Manual AML/KYC alert review is slow, repetitive, and prone to human error, creating bottlenecks in private banking compliance teams.

## Solution
Sentro uses a two-agent workflow to automatically fetch client data and generate a risk assessment in seconds.

## Architecture
- **Orchestrator Agent**: Receives the compliance request and routes it to the specialist agent.
- **Risk Analyst Agent**: Fetches client data via MCP and produces a structured risk assessment (suspicious activity, risk rating, recommended action).
- **MCP Server**: Exposes a `get_client_data` tool that securely serves mock banking data.
- **Security Guardrail**: Intercepts and blocks prompt-injection attempts (e.g., "ignore previous instructions") before they reach the LLM.

## Tech Stack
- Google Agent Development Kit (ADK)
- Model Context Protocol (MCP)
- Groq (Llama 3.1) via LiteLLM

## How to Run
1. Install dependencies: pip install -r requirements.txt
2. Add your Groq API key to a `.env` file: GROQ_API_KEY=your_key_here
3. Start the MCP server: python mcp_server.py
4. In a separate terminal, run the agent: python main.py

## Security
Sentro includes a prompt-injection guardrail that blocks malicious instructions (e.g., "ignore previous instructions") before they reach the LLM, preventing manipulation of the risk assessment output.

## Author
Built by Anne for the Kaggle AI Agents: Intensive Vibe Coding Capstone Project.



