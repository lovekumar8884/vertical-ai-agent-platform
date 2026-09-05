"""Database access layer.

All Postgres access MUST go through ``TenantScopedSession`` so Row-Level
Security is applied. Raw engine/connection use is forbidden by the import
boundary lint rule.
"""
