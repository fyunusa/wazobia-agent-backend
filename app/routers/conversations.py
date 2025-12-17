"""
Conversation management endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List

from ..database import get_db, Database
from .auth import get_current_user

router = APIRouter(prefix="/conversations", tags=["Conversations"])

# Limits
MAX_CONVERSATIONS = 5
MAX_MESSAGES_PER_CONVERSATION = 10


class ConversationResponse(BaseModel):
    id: int
    title: str
    message_count: int
    created_at: str
    updated_at: str


class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    language: Optional[str]
    created_at: str


class StatsResponse(BaseModel):
    conversation_count: int
    message_count: int
    max_conversations: int
    max_messages_per_conversation: int
    can_create_conversation: bool


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get all conversations for the authenticated user"""
    conversations = db.get_user_conversations(user['id'])
    return conversations


@router.get("/stats", response_model=StatsResponse)
async def get_user_stats(
    user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get user usage statistics"""
    stats = db.get_user_stats(user['id'])
    
    return StatsResponse(
        conversation_count=stats['conversation_count'],
        message_count=stats['message_count'],
        max_conversations=MAX_CONVERSATIONS,
        max_messages_per_conversation=MAX_MESSAGES_PER_CONVERSATION,
        can_create_conversation=stats['conversation_count'] < MAX_CONVERSATIONS
    )


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    title: str,
    user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Create a new conversation"""
    # Check conversation limit
    stats = db.get_user_stats(user['id'])
    if stats['conversation_count'] >= MAX_CONVERSATIONS:
        raise HTTPException(
            status_code=403,
            detail=f"You've reached the maximum of {MAX_CONVERSATIONS} conversations. Please upgrade for more."
        )
    
    conversation_id = db.create_conversation(user['id'], title)
    conversation = db.get_conversation(conversation_id, user['id'])
    
    return {
        **conversation,
        'message_count': 0
    }


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    user: dict = Depends(get_current_user),
    db: Database = Depends(get_db)
):
    """Get all messages in a conversation"""
    # Verify conversation belongs to user
    conversation = db.get_conversation(conversation_id, user['id'])
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.get_conversation_messages(conversation_id)
    return messages
