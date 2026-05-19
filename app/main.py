from fastapi import FastAPI

from app.routes.verify import router as verify_router


app = FastAPI(title="Decifact — Decision Equivalence Engine")
app.include_router(verify_router)