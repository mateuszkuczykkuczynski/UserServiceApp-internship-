from redis import Redis


def test_is_redis_connected():
    redis_host = 'redis'
    r = Redis(redis_host, socket_connect_timeout=1)

    assert r.ping()
