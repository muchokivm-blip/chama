import random

import pytest

from chama import Chama


def chama_with(*names, amount=1000):
    c = Chama(amount)
    for name in names:
        c.add(name)
    return c


def test_everyone_receives_once_per_round():
    c = chama_with("wanjiru", "otieno", "amina", "kiprop")
    payees = [c.close_month(c.members())["payee"] for _ in range(4)]
    assert sorted(payees) == sorted(c.members())
    assert c.close_month([])["payee"] == payees[0]


def test_new_member_goes_last():
    c = chama_with("a", "b", "c")
    c.close_month([])
    c.add("d")
    payees = [c.close_month([])["payee"] for _ in range(3)]
    assert payees == ["b", "c", "d"]


def test_member_added_between_rounds_goes_last_in_the_next_one():
    c = chama_with("a", "b")
    c.close_month([])
    c.close_month([])
    c.add("c")
    payees = [c.close_month([])["payee"] for _ in range(3)]
    assert payees == ["a", "b", "c"]


def test_late_payment_adds_to_the_pot():
    c = chama_with("wanjiru", "otieno", "amina", amount=2000)
    c.close_month(["wanjiru", "otieno"])
    month = c.view()["months"][0]
    assert month["pot"] == 4000
    assert month["unpaid"] == ["amina"]
    c.pay_late(1, "amina")
    month = c.view()["months"][0]
    assert month["pot"] == 6000
    assert month["unpaid"] == []
    with pytest.raises(ValueError):
        c.pay_late(1, "amina")


def test_removed_member_leaves_the_rotation():
    c = chama_with("a", "b", "c")
    c.remove("b")
    payees = [c.close_month([])["payee"] for _ in range(2)]
    assert payees == ["a", "c"]


def test_bad_input():
    c = chama_with("a")
    with pytest.raises(ValueError):
        c.add("a")
    with pytest.raises(ValueError):
        c.close_month(["zed"])
    with pytest.raises(ValueError):
        Chama().close_month([])
    with pytest.raises(ValueError):
        c.pay_late(5, "a")


def test_save_and_load(tmp_path):
    c = chama_with("a", "b", "c", amount=500)
    c.close_month(["a", "b"])
    c.save(tmp_path / "c.json")
    again = Chama.load(tmp_path / "c.json")
    assert again.view() == c.view()
    assert again.close_month([])["payee"] == "b"


def test_random_joins_never_double_pay_in_a_round():
    random.seed(7)
    c = chama_with("a", "b", "c")
    seen = []
    for i in range(300):
        if random.random() < 0.2:
            c.add(f"m{i}")
        payee = c.close_month([])["payee"]
        assert payee not in seen
        seen.append(payee)
        assert not set(c.waiting) & set(c.done)
        if not c.waiting:
            seen = []
    assert len(c.months) == 300
