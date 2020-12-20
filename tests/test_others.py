"""
MIT License
Copyright (c) 2020 Andy Zhou
"""


def test_change_theme(client):
    client.get("/change-theme/lite/", follow_redirects=True)
    cookie = next(
        (cookie for cookie in client.cookie_jar if cookie.name == "theme"),
        None
    )
    assert cookie is not None
    assert cookie.value == 'lite'
