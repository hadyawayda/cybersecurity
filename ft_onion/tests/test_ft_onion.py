from src.ft_onion.layers import seal, peel

def test_roundtrip():
    pt = b'hello onion'
    blob = seal(pt, ['a','b','c'])
    out = peel(blob, ['a','b','c'])
    assert out == pt
