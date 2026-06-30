import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.routes.research import router as research_router
from backend.routes.packages import router as packages_router
from backend.routes.workspace import router as workspace_router
from backend.routes.collaboration import router as collaboration_router
from backend.routes.versioning import router as versioning_router
from backend.database import init_db

# Initialize User Storage SQLite Database
init_db()

app = FastAPI(
    title="ARMOURLINE",
    description="A cryptographically governed multi-agent engineering research system.",
    version="1.0.0"
)

# Allow CORS for easy Next.js integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include sub-routes
app.include_router(research_router)
app.include_router(packages_router)
app.include_router(workspace_router)
app.include_router(collaboration_router)
app.include_router(versioning_router)

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")

@app.get("/api/exports/{filename}")
def download_export(filename: str):
    file_path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested file was not found or has expired.")
    
    # Return file response
    return FileResponse(file_path, filename=filename)

# Mount static files for Next.js frontend export
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    @app.get("/")
    def read_root():
        return {"status": "ONLINE", "framework": "FastAPI (ArmorIQ Secured)"}
