from fastapi import FastAPI

from app.routers import alerts, transactions, watchlist

app = FastAPI(
    title="txn-screening-svc",
    version="0.1.0",
    description="Toy transaction-screening service. **Synthetic data only.**",
)

app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(watchlist.router)


@app.get("/health", tags=["ops"])
def health() -> dict[str, str]:
    return {"status": "ok"}
