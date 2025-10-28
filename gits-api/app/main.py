from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import List, Dict

app = FastAPI(title="Gist API")

GITHUB_API = "https://api.github.com"

class GistOut(BaseModel):
    id: str
    html_url: str
    description: str | None
    created_at: str
    files: List[str]

def user_exists(user: str) -> bool:
    """Check if GitHub user exists"""
    resp = requests.get(f"{GITHUB_API}/users/{user}", timeout=10)
    return resp.status_code == 200

def fetch_gists_for_user(user: str, per_page: int = 30, max_pages: int = 5) -> List[Dict]:
    """Fetch public gists for a user, handle invalid users and empty gists"""
    # Check user existence
    if not user_exists(user):
        raise HTTPException(status_code=404, detail=f"GitHub user '{user}' not found")

    # Fetch gists with pagination
    gists: List[Dict] = []
    page = 1
    while page <= max_pages:
        url = f"{GITHUB_API}/users/{user}/gists"
        params = {"per_page": per_page, "page": page}
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Failed to fetch from GitHub")

        page_items = resp.json()
        if not page_items:
            break
        gists.extend(page_items)
        if len(page_items) < per_page:
            break
        page += 1

    # Handle empty gist list
    if not gists:
        raise HTTPException(status_code=204)

    # Transform into output shape
    return [
        {
            "id": g.get("id"),
            "html_url": g.get("html_url"),
            "description": g.get("description"),
            "created_at": g.get("created_at"),
            "files": list(g.get("files", {}).keys()),
        }
        for g in gists
    ]

@app.get("/{user}", response_model=List[GistOut])
def get_gists(user: str):
    """Return list of public gists for the given GitHub user."""
    return fetch_gists_for_user(user)

@app.get("/health")
def health():
    return {"status": "ok"}
