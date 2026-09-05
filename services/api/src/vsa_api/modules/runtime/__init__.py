"""Agent runtime: prompt composition and LLM streaming.

Sprint 1 is a single-provider (OpenAI ``gpt-4o-mini``) streaming runtime with no
LangGraph. The public seam is ``ports``; ``prompt`` and ``llm`` are internal.
"""
