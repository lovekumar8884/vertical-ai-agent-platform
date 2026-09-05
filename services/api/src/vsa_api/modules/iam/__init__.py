"""Identity & access: orgs, users, memberships.

Clerk is the source of truth for identity + membership (ADR-044); these tables
hold the duplicated fields we own for entitlement/business state, refreshed by
the Clerk webhook.
"""
