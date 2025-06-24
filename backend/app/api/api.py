from app.api.endpoints import notes, users, chat

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"]) 