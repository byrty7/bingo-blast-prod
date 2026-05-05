"""Extended API coverage: endpoints not fully exercised in test_bingo_blast.py."""
import os
import uuid

import pytest
import requests


@pytest.fixture
def fresh_user(api_client, base_url):
    r = api_client.post(
        f"{base_url}/api/guest/login",
        json={"device_id": f"EXT_{uuid.uuid4().hex}"},
    )
    assert r.status_code == 200, r.text
    return r.json()


class TestAvatarsAndProfile:
    def test_avatars_list(self, api_client, base_url):
        r = api_client.get(f"{base_url}/api/avatars/list")
        assert r.status_code == 200
        av = r.json()["avatars"]
        assert len(av) >= 1 and "url" in av[0]

    def test_user_update_username_and_avatar(self, api_client, base_url, fresh_user):
        av = api_client.get(f"{base_url}/api/avatars/list").json()["avatars"][0]["url"]
        r = api_client.post(
            f"{base_url}/api/user/update",
            json={"user_id": fresh_user["id"], "username": "ApiExtUser", "avatar": av},
        )
        assert r.status_code == 200, r.text
        u = r.json()["user"]
        assert u["username"] == "ApiExtUser"
        assert u["avatar"] == av


class TestRoomsById:
    def test_get_room_by_id(self, api_client, base_url, fresh_user):
        cr = api_client.post(
            f"{base_url}/api/rooms",
            json={
                "user_id": fresh_user["id"],
                "name": "Ext Room",
                "room_type": "free",
                "max_players": 4,
                "match_count": 1,
                "entry_fee": 0,
            },
        )
        assert cr.status_code == 200
        rid = cr.json()["id"]
        gr = api_client.get(f"{base_url}/api/rooms/{rid}")
        assert gr.status_code == 200
        assert gr.json()["id"] == rid


class TestRazorpayConfig:
    def test_config_endpoint(self, api_client, base_url):
        r = api_client.get(f"{base_url}/api/payments/razorpay/config")
        assert r.status_code == 200
        d = r.json()
        assert "use_real" in d and "mode" in d


class TestDashboard:
    def test_dashboard_html(self, api_client, base_url):
        r = api_client.get(f"{base_url}/dashboard/")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        body = r.text
        assert "Bingo Blast API Dashboard" in body
        assert "/api/guest/login" in body
        assert "/api/computer-match" in body
        assert "/api/guilds/create" in body


class TestMatchmaking:
    def test_join_queues_then_cancel(self, api_client, base_url, fresh_user):
        r = api_client.post(
            f"{base_url}/api/matchmaking/join",
            params={"user_id": fresh_user["id"]},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "queued"
        eid = data["entry_id"]
        s = api_client.get(f"{base_url}/api/matchmaking/status/{eid}")
        assert s.status_code == 200
        assert s.json()["status"] == "queued"
        c = api_client.post(f"{base_url}/api/matchmaking/cancel/{eid}")
        assert c.status_code == 200
        assert c.json()["ok"] is True


class TestVip:
    def test_info_then_activate(self, api_client, base_url, fresh_user):
        r = api_client.get(f"{base_url}/api/vip/info/{fresh_user['id']}")
        assert r.status_code == 200


@pytest.fixture
def vip_user(api_client, base_url):
    r = api_client.post(
        f"{base_url}/api/guest/login",
        json={"device_id": f"VIP_{uuid.uuid4().hex}"},
    )
    assert r.status_code == 200
    uid = r.json()["id"]
    api_client.post(
        f"{base_url}/api/vip/activate",
        params={"user_id": uid, "plan_id": "vip_monthly"},
    )
    return r.json()


class TestVipActivate:
    def test_activate_monthly(self, api_client, base_url, fresh_user):
        r = api_client.post(
            f"{base_url}/api/vip/activate",
            params={"user_id": fresh_user["id"], "plan_id": "vip_monthly"},
        )
        assert r.status_code == 200
        assert r.json()["ok"] is True
        info = api_client.get(f"{base_url}/api/vip/info/{fresh_user['id']}")
        assert info.status_code == 200
        assert info.json()["active"] is True


class TestCosmetics:
    def test_list_and_equip_default_frame(self, api_client, base_url, fresh_user):
        r = api_client.get(f"{base_url}/api/cosmetics/{fresh_user['id']}")
        assert r.status_code == 200
        frames = r.json()["cosmetics"]["frames"]
        assert any(f["id"] == "frame_default" for f in frames)
        eq = api_client.post(
            f"{base_url}/api/cosmetics/equip",
            params={
                "user_id": fresh_user["id"],
                "category": "frames",
                "item_id": "frame_default",
            },
        )
        assert eq.status_code == 200
        assert eq.json()["equipped"].get("frame") == "frame_default"


class TestPushRegister:
    def test_push_register(self, api_client, base_url, fresh_user):
        r = api_client.post(
            f"{base_url}/api/push/register",
            params={
                "user_id": fresh_user["id"],
                "token": "ExponentPushToken[test]",
                "platform": "expo",
            },
        )
        assert r.status_code == 200
        assert r.json()["ok"] is True


class TestGuildsExtended:
    def test_create_list_detail_leave(self, api_client, base_url):
        # New user + enough coins for guild (500 start + 500 purchase)
        r = api_client.post(
            f"{base_url}/api/guest/login",
            json={"device_id": f"GUILD_{uuid.uuid4().hex}"},
        )
        assert r.status_code == 200
        uid = r.json()["id"]
        api_client.post(
            f"{base_url}/api/payments/razorpay/verify",
            json={
                "user_id": uid,
                "item_id": "coins_500",
                "razorpay_order_id": "o",
                "razorpay_payment_id": "p",
                "razorpay_signature": "s",
            },
        )
        u = api_client.get(f"{base_url}/api/user/{uid}").json()
        assert u["bcoins"] >= 1000
        tag = uuid.uuid4().hex[:5].upper()
        cr = api_client.post(
            f"{base_url}/api/guilds/create",
            params={"user_id": uid, "name": "Test Guild", "tag": tag},
        )
        assert cr.status_code == 200, cr.text
        gid = cr.json()["id"]
        lst = api_client.get(f"{base_url}/api/guilds/list")
        assert lst.status_code == 200
        assert any(g["id"] == gid for g in lst.json())
        det = api_client.get(f"{base_url}/api/guilds/{gid}")
        assert det.status_code == 200
        assert det.json()["leader_id"] == uid
        lv = api_client.post(f"{base_url}/api/guilds/leave", params={"user_id": uid})
        assert lv.status_code == 200
