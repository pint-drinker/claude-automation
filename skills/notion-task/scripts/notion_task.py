#!/usr/bin/env python3
"""Notion Task Creator

Usage:
  notion_task.py schema                       - Print task database schema (select options only)
  notion_task.py search-project <query>       - Search Projects database by name
  notion_task.py create '<json>'              - Create a task from a JSON string of field values
  notion_task.py smart-create '<json>'        - Create a task, resolving ProjectName to a relation ID

Key fields: Task (title), Kanban (select), Project (relation), ProjectName (smart-create only)

Environment variables required:
  NOTION_TOKEN        - Your Notion integration token (secret_...)
  NOTION_DATABASE_ID  - The ID of your task database
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

PROJECT_CACHE_MAX_AGE_DAYS = 10
SCHEMA_CACHE_MAX_AGE_DAYS = 30


def get_skill_dir():
    # Script lives in scripts/, skill root is one level up
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_cache_dir():
    return os.path.join(get_skill_dir(), "cache")


def get_project_schema_path():
    return os.path.join(get_cache_dir(), "project.json")


def get_kanban_schema_path():
    return os.path.join(get_cache_dir(), "kanban.json")


def get_headers():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("Error: NOTION_TOKEN environment variable not set")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def get_database_id():
    db_id = os.environ.get("NOTION_DATABASE_ID")
    if not db_id:
        sys.exit("Error: NOTION_DATABASE_ID environment variable not set")
    return db_id.replace("-", "")


def notion_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        sys.exit(f"Notion API error {e.code}: {error_body}")


def notion_post(path, data):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=get_headers(), method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        sys.exit(f"Notion API error {e.code}: {error_body}")


def _fetch_schema_from_notion():
    """Fetch database schema from Notion (no caching)."""
    db_id = get_database_id()
    db = notion_get(f"/databases/{db_id}")

    schema = {
        "database_name": db.get("title", [{}])[0].get("plain_text", ""),
        "properties": {},
    }

    for prop_name, prop_data in db["properties"].items():
        prop_type = prop_data["type"]
        prop_info = {"type": prop_type}

        if prop_type == "select":
            prop_info["options"] = [opt["name"] for opt in prop_data["select"]["options"]]
        elif prop_type == "multi_select":
            prop_info["options"] = [opt["name"] for opt in prop_data["multi_select"]["options"]]
        elif prop_type == "status":
            prop_info["options"] = [opt["name"] for opt in prop_data["status"]["options"]]
        elif prop_type == "relation":
            # Store the related DB id for use by search-project, but don't fetch entries
            prop_info["database_id"] = prop_data["relation"]["database_id"]

        schema["properties"][prop_name] = prop_info

    return schema


def _load_schema_cached(max_age_days=SCHEMA_CACHE_MAX_AGE_DAYS):
    """Load task DB schema (including Kanban options) with a 5-day cache."""
    path = get_kanban_schema_path()
    now = datetime.now(timezone.utc)
    max_age = timedelta(days=max_age_days)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_updated_str = data.get("last_updated")
            if last_updated_str:
                last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
                if now - last_updated <= max_age:
                    return data
        except Exception:
            # Fall through to a full refresh
            pass

    schema = _fetch_schema_from_notion()
    schema["last_updated"] = (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )

    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=2)
    except Exception:
        # If writing fails, still return the in-memory schema
        pass

    return schema


def get_schema():
    """Fetch database schema, using a cached copy when fresh."""
    return _load_schema_cached()


def search_in_projects(projects, q):
    """Intelligent-ish text search over cached projects."""
    q = q.strip().lower()
    if not q:
        return []
    q_words = [w for w in q.split() if w]

    scored = []
    for p in projects:
        title = p.get("title") or ""
        t = title.lower()
        score = 0

        if t == q:
            score += 100
        if q in t:
            score += 50
        for w in q_words:
            if w in t:
                score += 10

        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda item: (-item[0], item[1].get("title", "")))
    return [p for _, p in scored][:10]


def _load_project_cache(max_age_days=PROJECT_CACHE_MAX_AGE_DAYS):
    """Load cached project schema + projects list, refreshing if stale or missing."""
    path = get_project_schema_path()
    now = datetime.now(timezone.utc)
    max_age = timedelta(days=max_age_days)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            last_updated_str = data.get("last_updated")
            if last_updated_str:
                last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
                if now - last_updated <= max_age:
                    return data
        except Exception:
            # Fall through to a full refresh
            pass

    return refresh_projects_cache()


def refresh_projects_cache():
    """Fetch Projects DB schema + all projects from Notion and write project.json."""
    # 1. Get project_db_id from kanban schema cache if available (no API call needed)
    project_db_id = None
    try:
        kanban_path = get_kanban_schema_path()
        if os.path.exists(kanban_path):
            with open(kanban_path, "r", encoding="utf-8") as f:
                kanban_data = json.load(f)
            project_db_id = kanban_data.get("properties", {}).get("Project", {}).get("database_id")
    except Exception:
        pass  # Fall through to API call below

    # Fallback: fetch task DB schema from API to find project_db_id
    if not project_db_id:
        db_id = get_database_id()
        db = notion_get(f"/databases/{db_id}")
        for prop_name, prop_data in db["properties"].items():
            if prop_name == "Project" and prop_data["type"] == "relation":
                project_db_id = prop_data["relation"]["database_id"]
                break

    if not project_db_id:
        sys.exit("Error: No 'Project' relation property found in Tasks database")

    # 2. Find the title property name in the Projects database
    projects_db = notion_get(f"/databases/{project_db_id}")
    title_prop_name = next(
        (name for name, data in projects_db["properties"].items() if data["type"] == "title"),
        None,
    )
    if not title_prop_name:
        sys.exit("Error: Could not find title property in Projects database")

    # 3. Query all projects (paginated)
    projects = []
    payload = {"page_size": 100}
    while True:
        result = notion_post(f"/databases/{project_db_id}/query", payload)
        for page in result.get("results", []):
            title_prop = page["properties"].get(title_prop_name, {})
            title_text = "".join(t["plain_text"] for t in title_prop.get("title", []))
            if title_text:
                projects.append({"id": page["id"], "title": title_text})

        if not result.get("has_more"):
            break
        payload["start_cursor"] = result.get("next_cursor")
        if not payload["start_cursor"]:
            break

    cache_data = {
        "project_db_id": project_db_id,
        "title_property": title_prop_name,
        "last_updated": (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        ),
        "projects": projects,
    }

    path = get_project_schema_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        # If writing fails, we still return the in-memory data
        pass

    return cache_data


def search_project(query):
    """Search the Projects database by name using a cached schema + project list."""
    # First attempt: use cached (or refreshed-if-stale) project list
    cache_data = _load_project_cache()
    projects = cache_data.get("projects", []) if cache_data else []
    matches = search_in_projects(projects, query)

    # If nothing found, force a refresh from Notion and try again
    if not matches:
        cache_data = refresh_projects_cache()
        projects = cache_data.get("projects", []) if cache_data else []
        matches = search_in_projects(projects, query)

    print(json.dumps(matches))


def resolve_field_name(field_name, schema):
    """Case-insensitive field name lookup."""
    if field_name in schema["properties"]:
        return field_name
    return next(
        (k for k in schema["properties"] if k.lower() == field_name.lower()), None
    )


def build_page_properties(field_values, schema):
    """Convert flat field_values dict into Notion API properties format."""
    properties = {}

    for field_name, value in field_values.items():
        resolved = resolve_field_name(field_name, schema)
        if not resolved:
            print(f"Warning: field '{field_name}' not found in schema, skipping", file=sys.stderr)
            continue

        prop = schema["properties"][resolved]
        prop_type = prop["type"]

        if prop_type == "title":
            properties[resolved] = {"title": [{"text": {"content": str(value)}}]}
        elif prop_type == "select":
            properties[resolved] = {"select": {"name": value}}
        elif prop_type == "multi_select":
            values = value if isinstance(value, list) else [value]
            properties[resolved] = {"multi_select": [{"name": v} for v in values]}
        elif prop_type == "status":
            properties[resolved] = {"status": {"name": value}}
        elif prop_type == "date":
            if isinstance(value, dict):
                properties[resolved] = {"date": value}
            else:
                properties[resolved] = {"date": {"start": value}}
        elif prop_type == "relation":
            ids = value if isinstance(value, list) else [value]
            properties[resolved] = {"relation": [{"id": v} for v in ids]}
        elif prop_type == "checkbox":
            properties[resolved] = {"checkbox": bool(value)}
        elif prop_type == "number":
            properties[resolved] = {"number": float(value)}
        elif prop_type == "rich_text":
            properties[resolved] = {"rich_text": [{"text": {"content": str(value)}}]}

    return properties


def create_task(field_values_json):
    """Create a Notion page. 2 API calls: schema fetch + page create."""
    field_values = json.loads(field_values_json)
    schema = get_schema()
    db_id = get_database_id()
    properties = build_page_properties(field_values, schema)

    result = notion_post("/pages", {
        "parent": {"database_id": db_id},
        "properties": properties,
    })

    title = next(
        (v for k, v in field_values.items() if k.lower() in ("task", "name", "title")),
        "Task",
    )

    print(json.dumps({
        "success": True,
        "page_id": result.get("id", ""),
        "url": result.get("url", ""),
        "title": title,
    }))


def smart_create(field_values_json):
    """Create a task, resolving an optional ProjectName string to a relation ID.

    Accepts all the same fields as 'create', plus an optional 'ProjectName' string.
    ProjectName is resolved to a Project relation ID by searching the project cache.
    If no match is found after a cache refresh, the task is created without a project.

    Output JSON includes url, title, and project_matched (resolved project title or null).
    """
    field_values = json.loads(field_values_json)

    project_name = field_values.pop("ProjectName", None)
    project_matched = None

    if project_name:
        cache_data = _load_project_cache()
        projects = cache_data.get("projects", []) if cache_data else []
        matches = search_in_projects(projects, project_name)

        if not matches:
            cache_data = refresh_projects_cache()
            projects = cache_data.get("projects", []) if cache_data else []
            matches = search_in_projects(projects, project_name)

        if matches:
            field_values["Project"] = [matches[0]["id"]]
            project_matched = matches[0]["title"]

    schema = get_schema()
    db_id = get_database_id()
    properties = build_page_properties(field_values, schema)

    result = notion_post("/pages", {
        "parent": {"database_id": db_id},
        "properties": properties,
    })

    title = next(
        (v for k, v in field_values.items() if k.lower() in ("task", "name", "title")),
        "Task",
    )

    print(json.dumps({
        "success": True,
        "page_id": result.get("id", ""),
        "url": result.get("url", ""),
        "title": title,
        "project_matched": project_matched,
    }))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "schema":
        print(json.dumps(get_schema(), indent=2))
    elif command == "search-project":
        if len(sys.argv) < 3:
            sys.exit("Usage: notion_task.py search-project <query>")
        search_project(sys.argv[2])
    elif command == "create":
        if len(sys.argv) < 3:
            sys.exit("Usage: notion_task.py create '<json>'")
        create_task(sys.argv[2])
    elif command == "smart-create":
        if len(sys.argv) < 3:
            sys.exit("Usage: notion_task.py smart-create '<json>'")
        smart_create(sys.argv[2])
    else:
        sys.exit(f"Unknown command: {command}. Use 'schema', 'search-project', 'create', or 'smart-create'.")


if __name__ == "__main__":
    main()
