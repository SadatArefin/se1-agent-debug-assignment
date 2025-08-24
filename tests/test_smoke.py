from agent.agent import answer

def test_smoke_runs():
    out = answer("Who is Ada Lovelace?")
    assert isinstance(out, str)

def test_calc_sometimes():
    out = answer("What is 1 + 1?")
    assert out is not None
