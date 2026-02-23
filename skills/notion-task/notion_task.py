#!/usr/bin/env python3
"""Notion Task Creator

Usage:
  notion_task.py schema                  - Print task database schema (select options only)
  notion_task.py search-project <query>  - Search Projects database by name
  notion_task.py create '<json>'         - Create a task from a JSON string of field values

Key fields: Task (title), Kanban (select), Project (relation)

Environment variables required:
  NOTION_TOKEN        - Your Notion integration token (secret_...)
  NOTION_DATABASE_ID  - The ID of your task database
"""

import json
import os
import sys
import urllib.request
import urllib.error

NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"


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


def get_schema():
    """Fetch database schema. 1 API call — no relation entries fetched."""
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


def search_project(query):
    """Search the Projects relation database by name. 3 API calls total."""
    # 1. Get the Projects database_id from the Tasks schema
    db_id = get_database_id()
    db = notion_get(f"/databases/{db_id}")

    project_db_id = None
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

    # 3. Query with a title filter
    result = notion_post(
        f"/databases/{project_db_id}/query",
        {
            "filter": {"property": title_prop_name, "title": {"contains": query}},
            "page_size": 10,
        },
    )

    matches = []
    for page in result.get("results", []):
        title_prop = page["properties"].get(title_prop_name, {})
        title_text = "".join(t["plain_text"] for t in title_prop.get("title", []))
        if title_text:
            matches.append({"id": page["id"], "title": title_text})

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
    else:
        sys.exit(f"Unknown command: {command}. Use 'schema', 'search-project', or 'create'.")


if __name__ == "__main__":
    main()
