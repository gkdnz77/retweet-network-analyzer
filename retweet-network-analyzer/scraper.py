import os
import requests
import time

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "").strip()
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "twitter241.p.rapidapi.com").strip()
BASE_URL = f"https://{RAPIDAPI_HOST}"

def build_headers():
    if not RAPIDAPI_KEY:
        raise RuntimeError("RAPIDAPI_KEY is missing. Add your API key to the environment first.")
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }

def get_working_instance():
    return "rapidapi"

def get_tweet_id(url):
    parts = url.strip().split("/")
    for i, p in enumerate(parts):
        if p == "status" and i + 1 < len(parts):
            return parts[i + 1].split("?")[0].split("#")[0]
    for p in reversed(parts):
        clean = p.split("?")[0].split("#")[0]
        if clean.isdigit() and len(clean) > 10:
            return clean
    return parts[-1].split("?")[0].split("#")[0]

def get_tweet_info(tweet_url, instance):
    tweet_id = get_tweet_id(tweet_url)
    return {
        "id": tweet_id,
        "author": "@user",
        "text": "Tweet analysis in progress...",
        "rt_count": 0,
        "url": tweet_url
    }, None

def parse_user_from_result(user_result):
    if not user_result:
        return None

    core = user_result.get("core", {})
    legacy = user_result.get("legacy", {})

    screen_name = (core.get("screen_name") or legacy.get("screen_name") or "").strip()
    if not screen_name:
        return None

    name = core.get("name") or legacy.get("name") or screen_name
    created_at = core.get("created_at") or legacy.get("created_at") or ""
    rest_id = str(user_result.get("id") or user_result.get("rest_id") or "")

    followers_count = int(legacy.get("followers_count", 0) or 0)
    friends_count = int(legacy.get("friends_count", 0) or 0)
    statuses_count = int(legacy.get("statuses_count", 0) or 0)

    verified = bool(user_result.get("is_blue_verified", False) or legacy.get("verified", False))

    return {
        "username": screen_name,
        "name": name,
        "id": rest_id if rest_id.isdigit() else "",
        "created_at": created_at,
        "followers_count": followers_count,
        "friends_count": friends_count,
        "statuses_count": statuses_count,
        "verified": verified,
    }

def get_retweeters(tweet_url, instance, max_pages=5):
    tweet_id = get_tweet_id(tweet_url)
    retweeters = []
    cursor = None
    headers = build_headers()

    print(f"\n[SocialGraph] Tweet ID: {tweet_id} is being analyzed...")

    for page in range(max_pages):
        try:
            params = {"pid": tweet_id, "count": "40"}
            if cursor:
                params["cursor"] = cursor

            r = requests.get(
                f"{BASE_URL}/retweets",
                headers=headers,
                params=params,
                timeout=20
            )

            if r.status_code != 200:
                return retweeters, f"HTTP {r.status_code}: {r.text[:300]}"

            data = r.json()
            found = []
            next_cursor = None

            top_cursor = data.get("cursor", {})
            if top_cursor.get("bottom"):
                next_cursor = top_cursor["bottom"]

            instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])

            for instr in instructions:
                for entry in instr.get("entries", []):
                    entry_id = entry.get("entryId", "")

                    if "cursor-bottom" in entry_id:
                        val = entry.get("content", {}).get("value")
                        if val:
                            next_cursor = val
                        continue
                    if "cursor-top" in entry_id:
                        continue

                    content = entry.get("content", {})
                    item_content = content.get("itemContent", {})
                    user_result = item_content.get("user_results", {}).get("result", {})

                    if not user_result:
                        for item in content.get("items", []):
                            ur = (
                                item.get("item", {})
                                    .get("itemContent", {})
                                    .get("user_results", {})
                                    .get("result", {})
                            )
                            if ur:
                                user_result = ur
                                break

                    user = parse_user_from_result(user_result)
                    if not user:
                        continue

                    sn = user["username"]
                    if any(u["username"] == sn for u in found):
                        continue
                    if any(u["username"] == sn for u in retweeters):
                        continue

                    found.append(user)

            retweeters.extend(found)

            if next_cursor and next_cursor != cursor and len(found) > 0:
                cursor = next_cursor
                time.sleep(0.5)
            else:
                break

        except requests.exceptions.Timeout:
            return retweeters, f"Timeout on page {page + 1}"
        except Exception as e:
            return retweeters, str(e)

    return retweeters, None

def get_following_usernames(user_id):
    following = set()
    headers = build_headers()
    try:
        r = requests.get(
            f"{BASE_URL}/followings",
            headers=headers,
            params={"user": user_id, "count": "200"},
            timeout=15
        )
        if r.status_code != 200:
            return following

        def extract(obj, depth=0):
            if depth > 15:
                return
            if isinstance(obj, dict):
                sn = (obj.get("screen_name") or obj.get("core", {}).get("screen_name") or "").strip().lower()
                if sn:
                    following.add(sn)
                    return
                for v in obj.values():
                    extract(v, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, depth + 1)

        extract(r.json())
    except Exception:
        return following
    return following

class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        self.parent[self.find(x)] = self.find(y)

def classify_users(retweeters):
    usernames = [u["username"] for u in retweeters]
    username_lower_set = {u.lower() for u in usernames}

    id_map = {
        u["username"]: u["id"]
        for u in retweeters
        if u.get("id") and str(u["id"]).isdigit() and len(str(u["id"])) > 5
    }

    following_map = {}
    for uname, uid in id_map.items():
        following = get_following_usernames(uid)
        following_map[uname] = following & username_lower_set
        time.sleep(0.35)

    edge_set = set()
    for uname, following in following_map.items():
        for fl in following:
            orig = next((u for u in usernames if u.lower() == fl), None)
            if orig and orig != uname:
                edge_set.add((uname, orig))

    mutual_pairs = set()
    for (a, b) in edge_set:
        if (b, a) in edge_set:
            mutual_pairs.add(tuple(sorted((a, b))))

    uf = UnionFind(usernames)
    for a, b in mutual_pairs:
        uf.union(a, b)

    mutual_group_members = {}
    for uname in usernames:
        root = uf.find(uname)
        mutual_group_members.setdefault(root, []).append(uname)

    grouped = []
    for u in retweeters:
        username = u["username"]
        uname_lower = username.lower()
        digit_ratio = (sum(ch.isdigit() for ch in username) / len(username)) if username else 0.0

        if any(username in members and len(members) >= 2 for members in mutual_group_members.values()):
            group = "mutual"
        elif username in following_map and len(following_map[username]) > 0:
            group = "interaction"
        elif "2024" in u.get("created_at", "") or "2025" in u.get("created_at", ""):
            group = "new_follower"
        elif u.get("statuses_count", 0) < 100 and u.get("followers_count", 0) < 100:
            group = "unfollower"
        elif (digit_ratio >= 0.5 and u.get("statuses_count", 0) < 500) or (len(username) < 4 and u.get("statuses_count", 0) < 200):
            group = "bot_suspect"
        elif u.get("followers_count", 0) > 2000 or u.get("verified", False):
            group = "viral"
        else:
            group = "independent"

        grouped.append({
            **u,
            "group": group
        })

    return grouped
