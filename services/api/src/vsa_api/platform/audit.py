"""Audit logging: compute a capped diff and write an ``audit_log`` row.

Every mutating service operation on org/user/membership/agent/agent_version
should record who did what. The ``diff`` is capped at 32 KB (frozen scope) so a
pathological payload cannot bloat the table.
"""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

MAX_DIFF_BYTES = 32 * 1024

_INSERT = text(
    """
    INSERT INTO audit_log
        (org_id, actor_user_id, action, resource_type, resource_id, diff, ip, ua)
    VALUES
        (:org_id, :actor_user_id, :action, :resource_type, :resource_id,
         CAST(:diff AS JSONB), :ip, :ua)
    """
)


def build_diff(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    """Return the per-field before/after for changed keys only."""
    before = before or {}
    after = after or {}
    changes: dict[str, Any] = {}
    for key in set(before) | set(after):
        if before.get(key) != after.get(key):
            changes[key] = {"before": before.get(key), "after": after.get(key)}
    return changes


def cap_diff(diff: dict[str, Any]) -> dict[str, Any]:
    """Return ``diff`` unchanged, or a truncation marker if it exceeds 32 KB."""
    size = len(json.dumps(diff, default=str).encode())
    if size <= MAX_DIFF_BYTES:
        return diff
    return {"_truncated": True, "_original_bytes": size}


async def write_audit(
    session: AsyncSession,
    *,
    org_id: uuid.UUID,
    actor_user_id: uuid.UUID | None,
    action: str,
    resource_type: str,
    resource_id: uuid.UUID | None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
    ip: str | None = None,
    ua: str | None = None,
) -> None:
    diff = cap_diff(build_diff(before, after))
    await session.execute(
        _INSERT,
        {
            "org_id": org_id,
            "actor_user_id": actor_user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "diff": json.dumps(diff, default=str),
            "ip": ip,
            "ua": ua,
        },
    )
