const API_BASE = 'http://localhost:8000';

const form = document.getElementById("search-form");
const input = document.getElementById("username");
const statusE1 = document.getElementById("status");
const card = document.getElementById("profile-card");

const avatarE1 = document.getElementById("avatar");
const nameE1 = document.getElementById("name");
const bioE1 = document.getElementById("bio");
const followersE1 = document.getElementById("followers");
const reposE1 = document.getElementById("repos");
const repoListE1 = document.getElementById("repo-list");

function setStatus(msg, isError = false) {
  statusE1.textContent = msg;
  statusE1.className = isError ? "status error" : "status";
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = input.value.trim();
  if (!username) return;

  // UI Reset
  card.classList.add("hidden");
  setStatus("Loading profile...");
  const btn = form.querySelector("button");
  btn.disabled = true;

  try {
    const response = await fetch(`${API_BASE}/api/user/${username}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Failed to fetch profile");
    }

    // Populate DOM
    avatarE1.src = data.avatar_url;
    nameE1.textContent = data.name;
    bioE1.textContent = data.bio;
    followersE1.textContent = data.followers;
    reposE1.textContent = data.public_repos;

    repoListE1.innerHTML = "";
    data.top_repos.forEach((repo) => {
      const li = document.createElement("li");
      li.innerHTML =
        `<a href="${repo.url}" target="_blank" rel="noopener">${repo.name}</a> <span>⭐ ${repo.stars}</span>`;
      repoListE1.appendChild(li);
    });

    setStatus("");
    card.classList.remove("hidden");
  } catch (err) {
    setStatus(err.message, true);
  } finally {
    btn.disabled = false;
  }
});
