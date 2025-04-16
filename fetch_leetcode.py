import os
import json
import time
import requests
from datetime import datetime

# Load environment variables
USERNAME = os.getenv("LEETCODE_USERNAME")
SESSION = os.getenv("LEETCODE_SESSION")
CSRF = os.getenv("LEETCODE_CSRF")

HEADERS = {
    "Content-Type": "application/json",
    "Referer": "https://leetcode.com",
    "User-Agent": "Mozilla/5.0",
    "x-csrftoken": CSRF,
    "cookie": f"LEETCODE_SESSION={SESSION}; csrftoken={CSRF}"
}

GRAPHQL_ENDPOINT = "https://leetcode.com/graphql"
LAST_FETCH_FILE = "last_fetch.json"
SAVE_ROOT = "leetcode"

LANGUAGE_EXT = {
    "cpp": "cpp",
    "python3": "py",
    "java": "java",
    "c": "c",
    "csharp": "cs",
    "javascript": "js",
    "typescript": "ts",
    "golang": "go",
    "ruby": "rb",
    "swift": "swift",
    "kotlin": "kt",
    "rust": "rs"
}

def read_last_timestamp():
    if not os.path.exists(LAST_FETCH_FILE):
        return 0
    with open(LAST_FETCH_FILE, "r") as f:
        data = json.load(f)
        return data.get("last_fetch", 0)

def save_last_timestamp(ts):
    with open(LAST_FETCH_FILE, "w") as f:
        json.dump({"last_fetch": ts}, f)

def fetch_submissions():
    submissions = []
    has_more = True
    offset = 0
    limit = 20
    last_fetch = read_last_timestamp()

    print("[+] Fetching submissions...")

    while has_more:
        query = {
            "operationName": "Submissions",
            "query": """
                query Submissions($offset: Int!, $limit: Int!) {
                  submissionList(offset: $offset, limit: $limit) {
                    hasNext
                    submissions {
                      id
                      timestamp
                      statusDisplay
                      lang
                      title
                      titleSlug
                    }
                  }
                }
            """,
            "variables": {
                "offset": offset,
                "limit": limit
            }
        }

        res = requests.post(GRAPHQL_ENDPOINT, json=query, headers=HEADERS)
        data = res.json()

        if "errors" in data:
            print("[-] Error fetching submissions:", data["errors"])
            break

        subs = data["data"]["submissionList"]["submissions"]
        for sub in subs:
            if sub["statusDisplay"] != "Accepted":
                continue
            if int(sub["timestamp"]) <= last_fetch:
                has_more = False
                break
            if sub["lang"] not in LANGUAGE_EXT:
                continue
            submissions.append(sub)

        has_more = data["data"]["submissionList"]["hasNext"]
        offset += limit

    print(f"[+] Found {len(submissions)} new accepted submissions.")
    return submissions

def fetch_code(submission_id):
    query = {
        "operationName": "submissionDetails",
        "query": """
            query submissionDetails($submissionId: Int!) {
              submissionDetails(submissionId: $submissionId) {
                code
              }
            }
        """,
        "variables": {
            "submissionId": int(submission_id)
        }
    }

    res = requests.post(GRAPHQL_ENDPOINT, json=query, headers=HEADERS)
    if res.status_code == 200:
        data = res.json()
        return data["data"]["submissionDetails"]["code"]
    else:
        print(f"[!] Error fetching code (HTTP {res.status_code}): {res.text}")
        return None

def get_problem_difficulty(title_slug):
    query = {
        "operationName": "questionData",
        "query": """
            query questionData($titleSlug: String!) {
              question(titleSlug: $titleSlug) {
                difficulty
              }
            }
        """,
        "variables": {"titleSlug": title_slug}
    }

    res = requests.post(GRAPHQL_ENDPOINT, json=query, headers=HEADERS)
    data = res.json()
    return data["data"]["question"]["difficulty"]

def sanitize_filename(title):
    return title.lower().replace(" ", "_").replace("/", "_")

def save_submission(sub, code, difficulty):
    lang = sub["lang"]
    ext = LANGUAGE_EXT.get(lang)
    if not ext:
        print(f"[!] Unsupported language: {lang}")
        return

    folder = os.path.join(SAVE_ROOT, lang, difficulty)
    os.makedirs(folder, exist_ok=True)

    filename = sanitize_filename(f"{sub['title']}_{sub['id']}") + f".{ext}"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"[✓] Saved: {filepath}")

def main():
    submissions = fetch_submissions()
    if not submissions:
        print("[*] No new accepted submissions.")
        return

    latest_ts = 0

    for sub in submissions:
        code = fetch_code(sub["id"])
        if not code:
            print(f"[-] Could not fetch code for: {sub['title']}")
            continue

        difficulty = get_problem_difficulty(sub["titleSlug"])
        save_submission(sub, code, difficulty)
        latest_ts = max(latest_ts, int(sub["timestamp"]))
        time.sleep(1.5)

    if latest_ts:
        save_last_timestamp(latest_ts)
        print("[✓] Updated last fetch timestamp.")

if __name__ == "__main__":
    main()
