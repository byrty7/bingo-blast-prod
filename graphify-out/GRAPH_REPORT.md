# Graph Report - bingo-blast-main  (2026-05-05)

## Corpus Check
- 50 files · ~74,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 291 nodes · 373 edges · 38 communities (34 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]

## God Nodes (most connected - your core abstractions)
1. `_ensure_extras()` - 23 edges
2. `now_utc()` - 21 edges
3. `strip_mongo()` - 15 edges
4. `ws_room()` - 12 edges
5. `_track_counter()` - 10 edges
6. `LoadingState()` - 8 edges
7. `TestMisc` - 7 edges
8. `columnColor()` - 6 edges
9. `columnLetter()` - 6 edges
10. `iso()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `guest_login()` --calls--> `now_utc()`  [EXTRACTED]
  backend/server.py → backend/server.py  _Bridges community 1 → community 0_

## Communities (38 total, 4 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (46): achievements(), AddFriendRequest, avatars_list(), battle_pass(), bp_activate_premium(), bp_claim(), BPClaimRequest, CallRequest (+38 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (37): _auto_caller(), _award_bp_xp(), call_number(), check_line(), claim_bingo_computer(), claim_daily(), create_computer_match(), create_room() (+29 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (10): Bingo Blast backend API tests, TestComputerMatch, TestDailyReward, TestFriends, TestGuestAndUser, TestHealth, TestRazorpayMocked, TestRooms (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (9): Phase A/B/C engagement tests: - Missions (Phase B) - Battle Pass (Phase C) - Col, TestBattlePass, TestCollection, TestComputerMatchPhaseA, TestEnsureExtras, TestEvent, TestGuestLoginExtras, TestMissions (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.14
Nodes (7): canClaim(), hasLine(), onDab(), showFloat(), tryClaimBingo(), usePowerup(), WS_URL()

### Community 6 - "Community 6"
Cohesion: 0.14
Nodes (4): isExpoGo(), registerPushTokenForUser(), columnColor(), columnLetter()

## Knowledge Gaps
- **15 isolated node(s):** `Round-2 focused smoke tests for Bingo Blast backend.  Scope (per review request)`, `Backend smoke tests for Bingo Blast. Tests:   1. Razorpay toggle + config + mock`, `dabbed_set: set of actual numbers user marked. FREE center always counts.`, `Return number of lines that are 1-cell away from bingo.`, `Backfill extra fields for users created before the upgrade.` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestMisc` connect `Community 7` to `Community 2`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `_ensure_extras()` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **Why does `columnColor()` connect `Community 6` to `Community 5`?**
  _High betweenness centrality (0.005) - this node is a cross-community bridge._
- **What connects `Round-2 focused smoke tests for Bingo Blast backend.  Scope (per review request)`, `Backend smoke tests for Bingo Blast. Tests:   1. Razorpay toggle + config + mock`, `dabbed_set: set of actual numbers user marked. FREE center always counts.` to the rest of the system?**
  _15 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.08 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._