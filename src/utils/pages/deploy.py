from __future__ import annotations
import os
import re
import shutil
import subprocess
from typing import List, Optional, Tuple
from dotenv import load_dotenv
from httpx import stream

load_dotenv()

CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")


class DeployError(RuntimeError): ...


def _check_wrangler_installed() -> None:
    if shutil.which("wrangler") is None:
        raise DeployError("wrangler CLI not found. Install with: npm i -g wrangler")


def _check_site_dir_exists(site_dir: str) -> None:
    if not os.path.exists(site_dir):
        raise FileNotFoundError(f"⚠️ Site directory not found: {site_dir}")


def _run(*args: str, cwd: Optional[str] = None) -> str:
    try:
        cp = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)
        return cp.stdout or cp.stderr
    except subprocess.CalledProcessError as e:
        msg = e.stderr or e.stdout or str(e)
        raise DeployError(f"Command failed: {' '.join(args)}\n{msg}") from e


def _project_exists(name: str) -> bool:
    try:
        _run("wrangler", "pages", "project", "get", name, "--format", "json")
        return True
    except DeployError:
        return False


def _create_project(domain: str, production_branch: str = "main") -> None:
    print(f"🆕 Creating Pages project '{domain}'...")
    try:
        _run(
            "wrangler",
            "pages",
            "project",
            "create",
            domain,
            f"--production-branch={production_branch}",
        )
    except DeployError as e:
        if "already exists" in str(e) or "8000002" in str(e):
            print(f"ℹ️ Project '{domain}' already exists. Skipping create.")
        else:
            raise


def _deploy_pages(domain: str, site_dir: str, branch: str = "main") -> str:
    out = _run(
        "wrangler",
        "pages",
        "deploy",
        str(site_dir),
        f"--project-name={domain}",
        f"--branch={branch}",
    )
    urls = set(re.compile(r"https?://[a-zA-Z0-9._/-]+").findall(out))
    url = next((u for u in urls if ".pages.dev" in u), next(iter(urls), None))
    if url:
        print(f"✅ Deployed {site_dir} → {url}\n")
    else:
        raise DeployError(
            f"ℹ️ Deployment succeeded but URL not parsed. Raw output:\n{out}"
        )
    return url


def deploy_site(site_dir: str, branch: str = "main", project_name: str = "site") -> str:
    print(
        "🚀 Starting deployment via Cloudflare Pages (Wrangler Direct Upload, single project)...\n"
    )
    _check_wrangler_installed()
    _check_site_dir_exists(site_dir)

    domain = f"{project_name}-site"

    print(f"📦 Domain: {domain}\n📁 Deploy directory: {site_dir}")

    if not _project_exists(domain):
        _create_project(domain, production_branch=branch)

    url = _deploy_pages(domain, site_dir, branch=branch)

    return url
