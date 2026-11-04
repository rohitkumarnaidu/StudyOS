from fastapi import APIRouter

from studyos_api.api.v1.routes import (
    ai,
    analytics,
    auth,
    bulk_import,
    examples,
    health,
    me,
    mistake_intelligence,
    note_export,
    note_search,
    notes,
    privacy,
    progress,
    quizzes,
    roadmap,
    syllabus,
    websocket,
)

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(health.router, tags=["health"])
router.include_router(me.router, tags=["identity"])
router.include_router(examples.router, tags=["examples"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(syllabus.router, prefix="/syllabus", tags=["syllabus"])
router.include_router(progress.router, prefix="/progress", tags=["progress"])
router.include_router(privacy.router, prefix="/privacy", tags=["privacy"])
router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
router.include_router(
    mistake_intelligence.router, prefix="/mistake-intelligence", tags=["mistake-intelligence"]
)
router.include_router(notes.router, prefix="/notes", tags=["notes"])
router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
router.include_router(websocket.router, tags=["websocket"])
router.include_router(bulk_import.router, prefix="/bulk-import", tags=["bulk-import"])
router.include_router(note_search.router, prefix="/note-search", tags=["note-search"])
router.include_router(note_export.router, prefix="/note-export", tags=["note-export"])
