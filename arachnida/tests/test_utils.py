from src.spider.util import normalize_url, is_same_host, is_image_url

def test_normalize_url():
 assert normalize_url('HTTP://ExAmPle.com/a#frag')=='http://example.com/a'

def test_same_host():
 assert is_same_host('http://A.com/x','http://a.com/y')
 assert not is_same_host('http://a.com','http://b.com')

def test_is_image_url():
 assert is_image_url('http://x/y.jpg')
 assert not is_image_url('http://x/y.html')
