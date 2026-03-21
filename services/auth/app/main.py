from fastapi import FastAPI

app = FastAPI(title="CareFlow Auth Service")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "auth",
    }
