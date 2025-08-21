from __future__ import annotations

import os
import re
import json
import shutil
import subprocess
from typing import Callable, List, Optional, Tuple


def _ensure_wrangler_available() -> None:
    if shutil.which("wrangler") is None:
        raise RuntimeError("wrangler CLI not found. Install with: npm i -g wrangler")


def _require_env(var: str) -> str:
    val = os.environ.get(var)
    if not val:
        raise RuntimeError(f"Missing env: {var}")
    return val


def _run(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def _project_exists(project_name: str) -> bool:
    code, out, err = _run(["wrangler", "pages", "project", "list"])
    if code != 0:
        raise RuntimeError(f"Failed to list projects\n{err or out}")
    return any(project_name in line for line in out.splitlines())


def _create_project(project_name: str, production_branch: str = "main") -> None:
    code, out, err = _run(
        [
            "wrangler",
            "pages",
            "project",
            "create",
            project_name,
            f"--production-branch={production_branch}",
        ]
    )
    if code != 0:
        raise RuntimeError(
            f"Failed to create Pages project '{project_name}'\n"
            f"STDERR:\n{err}\nSTDOUT:\n{out}"
        )


def _deploy_pages(
    project_name: str, site_dir: str, branch: str = "main"
) -> Tuple[Optional[str], str]:
    code, out, err = _run(
        [
            "wrangler",
            "pages",
            "deploy",
            site_dir,
            f"--project-name={project_name}",
            f"--branch={branch}",
        ]
    )
    if code != 0:
        raise RuntimeError(
            f"Failed to deploy project '{project_name}' from '{site_dir}'\n"
            f"STDERR:\n{err}\nSTDOUT:\n{out}"
        )

    urls = set(re.findall(r"https?://[a-zA-Z0-9._/-]+", out))
    primary = next((u for u in urls if ".pages.dev" in u), (next(iter(urls), None)))
    return primary, out


def deploy_sites_under(
    sites_dir: str,
    image_copier: Optional[Callable[[str], None]] = None,
    account_envs_required: bool = True,
    branch: str = "main",
    report_path: str = "output/deployment_report.md",
    project_namer: Optional[Callable[[str], str]] = None,
    project_name: Optional[str] = None,
    json_report_path: str = "output/deployment.json",  # ✅ 추가
) -> List[Tuple[str, str]]:
    """
    Deploy the *entire* sites_dir as a single Cloudflare Pages project.
    Return: [(<folder-name>, <url>)]

    Changes from previous behavior:
    - No per-subfolder iteration. The whole `sites_dir` is uploaded as a single site.
    - `image_copier` and `project_namer` are ignored (kept for backward compatibility).
    """

    print(
        "🚀 Starting deployment via Cloudflare Pages (Wrangler Direct Upload, single project)...\n"
    )

    # 하위호환 경고
    if image_copier is not None:
        print("⚠️ [compat] `image_copier` is ignored in single-folder deploy mode.")
    if project_namer is not None:
        print("⚠️ [compat] `project_namer` is ignored in single-folder deploy mode.")

    _ensure_wrangler_available()
    if account_envs_required:
        _require_env("CLOUDFLARE_API_TOKEN")
        _require_env("CLOUDFLARE_ACCOUNT_ID")

    if not os.path.exists(sites_dir):
        print(f"⚠️ Sites directory not found: {sites_dir}")
        return []

    # 프로젝트 이름 결정
    if not project_name:
        base = os.path.basename(os.path.abspath(sites_dir))
        project_name = f"{base}-site"
    print(f"📦 Project name: {project_name}")
    print(f"📁 Deploy directory: {sites_dir}")

    deployed: List[Tuple[str, str]] = []

    try:
        if not _project_exists(project_name):
            print(f"🆕 Creating Pages project '{project_name}'...")
            _create_project(project_name, production_branch=branch)
        else:
            print(f"✅ Pages project '{project_name}' already exists.")

        print("🚚 Uploading files via Wrangler...")
        url, raw_out = _deploy_pages(project_name, sites_dir, branch=branch)

        if url:
            deployed.append((os.path.basename(sites_dir), url))
            print(f"✅ Deployed {sites_dir} → {url}\n")
        else:
            print("ℹ️ Deployment succeeded but URL not parsed. Raw output:")
            print(raw_out)

    except Exception as e:
        print("❌ Failed to deploy")
        print(str(e))

    if deployed:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        data = {folder: {"url": url} for folder, url in deployed}
        with open(report_path, "w", encoding="utf-8") as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
        print(f"📝 JSON report saved to `{report_path}`")
    else:
        print("\n⚠️ No deployments were successful.")
    return deployed
