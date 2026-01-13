import uvicorn
from fastapi import FastAPI

from src.project.routers import project_router
from src.project_config import settings
from src.requirement.routers import requirement_router


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME
    )
    application.include_router(requirement_router)
    application.include_router(project_router)

    return application


app = get_application()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
