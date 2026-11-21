import json
from typing import Annotated
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from department_ai.core.config.settings import Settings, get_settings
from department_ai.modules.ai_assistant.infrastructure.models import (
    Conversation,
    ConversationMessage,
)
from department_ai.modules.ai_assistant.presentation.schemas import ChatRequest, ChatResponse
from department_ai.modules.identity.infrastructure.models import OrganizationMembership
from department_ai.modules.identity.presentation.dependencies import CurrentUser, DatabaseSession

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: CurrentUser,
    session: DatabaseSession,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ChatResponse:
    membership = session.get(
        OrganizationMembership,
        (current_user.id, payload.organization_id),
    )
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Organization access required"
        )

    conversation = None
    history: list[dict[str, str]] = []
    if payload.conversation_id is not None:
        conversation = session.scalar(
            select(Conversation).where(
                Conversation.id == payload.conversation_id,
                Conversation.user_id == current_user.id,
                Conversation.organization_id == payload.organization_id,
            )
        )
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        history = [
            {"role": message.role, "content": message.content}
            for message in session.scalars(
                select(ConversationMessage)
                .where(ConversationMessage.conversation_id == conversation.id)
                .order_by(ConversationMessage.created_at, ConversationMessage.id)
                .limit(20)
            )
        ]

    answer = _ask_ollama(settings, [*history, {"role": "user", "content": payload.message}])

    if conversation is None:
        conversation = Conversation(
            organization_id=payload.organization_id,
            user_id=current_user.id,
        )
        session.add(conversation)
        session.flush()
    session.add_all(
        [
            ConversationMessage(
                conversation_id=conversation.id, role="user", content=payload.message
            ),
            ConversationMessage(conversation_id=conversation.id, role="assistant", content=answer),
        ]
    )
    session.commit()
    return ChatResponse(conversation_id=conversation.id, answer=answer)


def _ask_ollama(settings: Settings, messages: list[dict[str, str]]) -> str:
    body = json.dumps(
        {"model": settings.ollama_model, "messages": messages, "stream": False}
    ).encode("utf-8")
    request = Request(
        f"{settings.ollama_base_url.rstrip('/')}/api/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
            result: object = json.loads(response.read())
    except HTTPError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ollama returned HTTP {error.code}",
        ) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not reach the Ollama server",
        ) from error

    message = result.get("message") if isinstance(result, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Ollama returned an empty response",
        )
    return content.strip()
