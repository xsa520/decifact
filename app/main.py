from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.verify import router as verify_router
from app.routes.canonicalize import (
    router as canonicalize_router)
from app.routes.compare import router as compare_router
from app.routes.admit_and_compare import router as admit_and_compare_router


app = FastAPI(title="Decifact — Decision Equivalence Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
app.include_router(verify_router)
app.include_router(canonicalize_router)
app.include_router(compare_router)
app.include_router(admit_and_compare_router)