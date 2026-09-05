"""IAM HTTP routes: Clerk webhook, /me (with lazy-upsert backstop), members."""

from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import select, text

from vsa_api.config import get_settings
from vsa_api.modules.iam import service
from vsa_api.modules.iam.models import Membership, User
from vsa_api.modules.iam.schemas import MemberOut, MeResponse, UserOut
from vsa_api.platform.auth.deps import Principal, UnauthorizedError, require_principal
from vsa_api.platform.db.engine import get_sessionmaker
from vsa_api.platform.ids import IdType, from_uuid, to_uuid

router = APIRouter(prefix="/v1", tags=["iam"])


@router.post("/webhooks/clerk", status_code=204)
async def clerk_webhook(request: Request) -> Response:
    settings = get_settings()
    body = await request.body()
    try:
        service.verify_webhook_signature(
            payload=body,
            svix_id=request.headers.get("svix-id"),
            svix_timestamp=request.headers.get("svix-timestamp"),
            svix_signature=request.headers.get("svix-signature"),
            secret=settings.clerk_webhook_signing_secret.get_secret_value(),
        )
    except service.WebhookVerificationError as exc:
        raise UnauthorizedError("Invalid webhook signature.") from exc

    event = json.loads(body)
    async with get_sessionmaker()() as session, session.begin():
        await service.apply_clerk_event(session, event)
    return Response(status_code=204)


@router.get("/me", response_model=MeResponse)
async def me(
    principal: Annotated[Principal, Depends(require_principal)],
) -> MeResponse:
    async with get_sessionmaker()() as session, session.begin():
        await service.lazy_upsert_principal(
            session,
            clerk_user_id=principal.user_id,
            email=principal.claims.get("email", ""),
            org_slug=principal.claims.get("org_slug"),
            org_name=principal.claims.get("org_name"),
            org_role=principal.org_role,
        )
        return await service.load_me(session, clerk_user_id=principal.user_id)


@router.get("/orgs/{org_id}/members", response_model=list[MemberOut])
async def list_members(
    org_id: str,
    principal: Annotated[Principal, Depends(require_principal)],
) -> list[MemberOut]:
    org_uuid = to_uuid(org_id)
    async with get_sessionmaker()() as session, session.begin():
        await session.execute(
            text("SELECT set_config('app.org_id', :org_id, true)"),
            {"org_id": str(org_uuid)},
        )
        # RLS scopes this to the org; a caller outside the org sees no rows.
        rows = (
            await session.execute(
                select(Membership, User)
                .join(User, User.id == Membership.user_id)
                .where(Membership.org_id == org_uuid)
            )
        ).all()

    return [
        MemberOut(
            id=from_uuid(IdType.MEMBERSHIP, membership.id),
            role=membership.role,
            user=UserOut(id=from_uuid(IdType.USER, user.id), email=user.email, name=user.name),
        )
        for membership, user in rows
    ]
