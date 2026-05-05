#!/usr/bin/env python3
"""
Hit every REST endpoint on a running Bingo Blast API (smoke test).

Usage:
  cd backend && python scripts/smoke_test_apis.py
  BACKEND_URL=http://127.0.0.1:8000 python scripts/smoke_test_apis.py

Requires: requests (`pip install requests`)
Optional WebSocket check: pip install websocket-client

Exit code 0 if all required checks pass; 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests

Result = Tuple[str, bool, str]


def main() -> int:
    p = argparse.ArgumentParser(description="Smoke-test Bingo Blast REST APIs")
    p.add_argument(
        "--base-url",
        default=os.environ.get("BACKEND_URL")
        or os.environ.get("EXPO_PUBLIC_BACKEND_URL")
        or "http://127.0.0.1:8000",
        help="API origin without trailing slash (default: env BACKEND_URL or localhost:8000)",
    )
    p.add_argument("--skip-ws", action="store_true", help="Skip WebSocket smoke check")
    args = p.parse_args()
    base = args.base_url.rstrip("/")
    api = f"{base}/api"

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    results: List[Result] = []

    def ok(name: str, condition: bool, detail: str = "") -> None:
        results.append((name, condition, detail))

    def req(
        method: str,
        path: str,
        *,
        json_body: Any = None,
        params: Optional[Dict[str, Any]] = None,
        allowed: Tuple[int, ...] = (200,),
    ) -> Optional[requests.Response]:
        url = path if path.startswith("http") else f"{api}{path}"
        try:
            r = session.request(method, url, json=json_body, params=params, timeout=60)
        except requests.RequestException as e:
            ok(f"{method} {path}", False, str(e))
            return None
        cond = r.status_code in allowed
        detail = f"{r.status_code} {r.text[:200]}"
        ok(f"{method} {path}", cond, detail if not cond else f"{r.status_code}")
        return r if cond else None

    print(f"Base URL: {base}\n")

    # --- Core ---
    req("GET", "/", allowed=(200,))
    req("GET", "/dashboard", allowed=(200,))
    dev_a = f"smoke_a_{uuid.uuid4().hex[:12]}"
    dev_b = f"smoke_b_{uuid.uuid4().hex[:12]}"
    ra = req("POST", "/guest/login", json_body={"device_id": dev_a})
    rb = req("POST", "/guest/login", json_body={"device_id": dev_b})
    if not ra or not rb:
        print_summary(results)
        return 1
    ua = ra.json()
    ub = rb.json()
    uid_a, uid_b = ua["id"], ub["id"]

    req("GET", f"/user/{uid_a}")
    av = req("GET", "/avatars/list")
    first_avatar_url = None
    if av:
        avatars = av.json().get("avatars") or []
        if avatars:
            first_avatar_url = avatars[0]["url"]

    req(
        "POST",
        "/user/update",
        json_body={
            "user_id": uid_a,
            "username": "SmokeUser",
            **({"avatar": first_avatar_url} if first_avatar_url else {}),
        },
        allowed=(200, 400),
    )

    req("GET", f"/streak/{uid_a}")
    req("POST", "/daily-reward/claim", params={"user_id": uid_a}, allowed=(200, 400))
    req("POST", "/spin-wheel/spin", params={"user_id": uid_b}, allowed=(200, 400))

    req("GET", f"/missions/{uid_a}")
    req("POST", "/missions/claim", json_body={"user_id": uid_a, "mission_id": "nonexistent"}, allowed=(404, 400))

    req("GET", f"/battle-pass/{uid_a}")
    req(
        "POST",
        "/battle-pass/claim",
        json_body={"user_id": uid_a, "tier": 99, "track": "free"},
        allowed=(400, 404),
    )
    req("POST", "/battle-pass/activate-premium", params={"user_id": uid_a})

    req("GET", f"/collection/{uid_a}")
    req("POST", "/collection/claim", params={"user_id": uid_a}, allowed=(400,))

    req("GET", "/event/current")
    req("GET", "/leaderboard")
    req("GET", "/leaderboard", params={"period": "week"}, allowed=(200,))
    req("GET", "/tournaments")
    req("POST", "/tournament/register", params={"user_id": uid_a, "tournament_id": "tour_daily"}, allowed=(200, 400))
    req("GET", f"/achievements/{uid_a}")
    req("GET", f"/friends/{uid_a}")
    req(
        "POST",
        "/friends/add",
        json_body={"user_id": uid_a, "friend_code": ub.get("friend_code") or ub["id"].split("-")[0].upper()},
    )
    req("GET", f"/transactions/{uid_a}")
    req("GET", "/shop/items")
    req("GET", "/payments/razorpay/config")
    req("POST", "/payments/razorpay/create-order", json_body={"user_id": uid_a, "item_id": "coins_100"})
    req(
        "POST",
        "/payments/razorpay/verify",
        json_body={
            "user_id": uid_a,
            "item_id": "coins_100",
            "razorpay_order_id": "order_smoke",
            "razorpay_payment_id": "pay_smoke",
            "razorpay_signature": "sig_smoke",
        },
    )

    # Rooms
    rr = req(
        "POST",
        "/rooms",
        json_body={
            "user_id": uid_a,
            "name": "Smoke Room",
            "room_type": "free",
            "max_players": 10,
            "match_count": 1,
            "entry_fee": 0,
        },
    )
    room_id = rr.json().get("id") if rr else None
    req("GET", "/rooms")
    req("GET", "/rooms", params={"filter": "free"})
    if room_id:
        req("GET", f"/rooms/{room_id}")
        req("POST", f"/rooms/{room_id}/join", json_body={"user_id": uid_b})

    # Computer match (minimal)
    mc = req(
        "POST",
        "/computer-match",
        json_body={"user_id": uid_a, "difficulty": "easy", "num_cards": 1},
    )
    mid = mc.json().get("id") if mc else None
    if mid:
        req("POST", "/computer-match/call", json_body={"match_id": mid})
        req(
            "POST",
            "/computer-match/dab",
            json_body={"match_id": mid, "user_id": uid_a, "number": 1, "speed_bonus": False},
            allowed=(200, 400),
        )
        req(
            "POST",
            "/computer-match/use-powerup",
            params={"match_id": mid, "user_id": uid_a, "powerup_id": "reveal"},
            allowed=(200, 400),
        )
        req(
            "POST",
            "/computer-match/claim-bingo",
            json_body={"match_id": mid, "user_id": uid_a, "dabbed_numbers": [], "card_index": 0},
        )

    # Matchmaking
    mj = req("POST", "/matchmaking/join", params={"user_id": uid_b})
    entry_id = mj.json().get("entry_id") if mj else None
    if entry_id:
        req("GET", f"/matchmaking/status/{entry_id}")
        req("POST", f"/matchmaking/cancel/{entry_id}")

    # VIP
    req("GET", f"/vip/info/{uid_a}")
    req("POST", "/vip/activate", params={"user_id": uid_a, "plan_id": "vip_monthly"})

    # Cosmetics
    req("GET", f"/cosmetics/{uid_a}")
    req(
        "POST",
        "/cosmetics/equip",
        params={"user_id": uid_a, "category": "frames", "item_id": "frame_default"},
    )

    # Guilds: top up to 1000 BC then create / join / leave
    req(
        "POST",
        "/payments/razorpay/verify",
        json_body={
            "user_id": uid_a,
            "item_id": "coins_500",
            "razorpay_order_id": "o2",
            "razorpay_payment_id": "p2",
            "razorpay_signature": "s2",
        },
    )
    gr = req(
        "POST",
        "/guilds/create",
        params={"user_id": uid_a, "name": "SmokeGuild", "tag": "SMOKE"},
        allowed=(200, 400),
    )
    guild_id = gr.json().get("id") if gr and gr.status_code == 200 else None
    req("GET", "/guilds/list")
    if guild_id:
        req("GET", f"/guilds/{guild_id}")
    req("POST", "/guilds/join", params={"user_id": uid_b, "code_or_id": "INVALID"}, allowed=(404,))
    req("POST", "/guilds/leave", params={"user_id": uid_b}, allowed=(200, 400))
    if guild_id:
        req("POST", "/guilds/leave", params={"user_id": uid_a}, allowed=(200, 400))

    # Push scaffold
    req("POST", "/push/register", params={"user_id": uid_a, "token": "expo_smoke_token", "platform": "expo"})

    # WebSocket (optional)
    if not args.skip_ws and room_id:
        try:
            from websocket import create_connection  # type: ignore
        except ImportError:
            ok("WebSocket /api/ws/room/...", True, "skipped (pip install websocket-client)")
        else:
            ws_base = base.replace("https://", "wss://").replace("http://", "ws://")
            ws_url = f"{ws_base}/api/ws/room/{room_id}/{uid_a}"
            try:
                ws = create_connection(ws_url, timeout=10)
                msg = json.loads(ws.recv())
                ws.close()
                ok("WebSocket room_state", msg.get("type") == "room_state", str(msg)[:120])
            except Exception as e:
                ok("WebSocket room_state", False, str(e))

    print_summary(results)
    failed = [r for r in results if not r[1]]
    return 1 if failed else 0


def print_summary(results: List[Result]) -> None:
    print("\n--- Summary ---")
    passed = sum(1 for _, ok_flag, _ in results if ok_flag)
    print(f"Passed: {passed}/{len(results)}")
    for name, ok_flag, detail in results:
        status = "OK " if ok_flag else "FAIL"
        print(f"  [{status}] {name}")
        if not ok_flag and detail:
            print(f"         {detail}")


if __name__ == "__main__":
    sys.exit(main())
