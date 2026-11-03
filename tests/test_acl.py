def test_access_levels_are_explicit():
    allowed={"public":["public"],"staff":["public","staff"],"admin":["public","staff","admin"]}
    assert "admin" not in allowed["public"]
    assert "staff" not in allowed["public"]
