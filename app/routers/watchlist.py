from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.models import Rule, WatchlistEntry, WatchlistEntryIn
from app.screening import RULES
from app.store import Store, get_store, new_id

router = APIRouter(tags=["reference data"])
StoreDep = Annotated[Store, Depends(get_store)]


@router.get("/watchlist", response_model=list[WatchlistEntry])
def list_watchlist(store: StoreDep) -> list[WatchlistEntry]:
    return list(store.watchlist.values())


@router.post("/watchlist", response_model=WatchlistEntry, status_code=status.HTTP_201_CREATED)
def add_watchlist_entry(body: WatchlistEntryIn, store: StoreDep) -> WatchlistEntry:
    with store.lock:
        entry = WatchlistEntry(id=new_id("wl"), **body.model_dump())
        store.watchlist[entry.id] = entry
    return entry


@router.delete("/watchlist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_watchlist_entry(entry_id: str, store: StoreDep) -> Response:
    with store.lock:
        if store.watchlist.pop(entry_id, None) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Watchlist entry not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/rules", response_model=list[Rule])
def list_rules() -> list[Rule]:
    return RULES
