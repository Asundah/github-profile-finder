import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI (
    title = "Github Profile Finder API"
)

# CORS: Allow local testing AND Vercel URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://github-profile-finder.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/user/{username}")
async def get_user(username: str):
    if not GITHUB_TOKEN:
        raise HTTPException(status_code=500, detail="Server misconfigured: missing Github token")

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    async with httpx.AsyncClient() as client:
        # 1. Fetch User Profile
        user_res = await client.get(f"https://api.github.com/users/{username}", headers=headers)
        if user_res.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")
        if user_res.status_code != 200:
            raise HTTPException(status_code=user_res.status_code, detail="Github API error")

        user_data = user_res.json()

        # 2. Fetch User Repos (Top 5 by stars)
        repos_res = await client.get(f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100", headers=headers)
        repos_data = repos_res.json() if repos_res.status_code == 200 else []

        # Sort repos by stargazers_count descending, take top 5
        top_repos = sorted(repos_data, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:5]
        top_repos_clean = [{"name": r["name"], "stars": r["stargazers_count"], "url": r["html_url"]} for r in top_repos]

        return {
            "avatar_url": user_data.get("avatar_url"),
            "name": user_data.get("name") or user_data.get("login"),
            "bio": user_data.get("bio") or "No bio provided.",
            "followers": user_data.get("followers"),
            "public_repos": user_data.get("public_repos"),
            "top_repos": top_repos_clean
        }