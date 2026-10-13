import json
from collections import deque
from pathlib import Path


class Chama:
    def __init__(self, amount=1000):
        self.amount = amount
        self.waiting = deque()
        self.done = []
        self.months = []

    def members(self):
        return list(self.waiting) + self.done

    def add(self, name):
        if not name:
            raise ValueError("name is empty")
        if name in self.members():
            raise ValueError(f"{name} is already a member")
        if self.waiting:
            self.waiting.append(name)
        else:
            self.done.append(name)

    def remove(self, name):
        if name in self.waiting:
            self.waiting.remove(name)
        elif name in self.done:
            self.done.remove(name)
        else:
            raise ValueError(f"{name} is not a member")

    def set_amount(self, amount):
        if amount < 1:
            raise ValueError("amount must be at least 1")
        self.amount = amount

    def close_month(self, paid):
        members = self.members()
        if not members:
            raise ValueError("add members first")
        unknown = set(paid) - set(members)
        if unknown:
            raise ValueError("not members: " + ", ".join(sorted(unknown)))
        if not self.waiting:
            self.waiting.extend(self.done)
            self.done = []
        payee = self.waiting.popleft()
        self.done.append(payee)
        month = {
            "payee": payee,
            "amount": self.amount,
            "members": members,
            "paid": sorted(set(paid)),
        }
        self.months.append(month)
        return month

    def pay_late(self, n, name):
        if not 1 <= n <= len(self.months):
            raise ValueError("no such month")
        month = self.months[n - 1]
        if name not in month["members"]:
            raise ValueError(f"{name} was not a member that month")
        if name in month["paid"]:
            raise ValueError(f"{name} already paid")
        month["paid"].append(name)

    def view(self):
        months = []
        for i, m in enumerate(self.months, 1):
            months.append({
                "n": i,
                "payee": m["payee"],
                "pot": m["amount"] * len(m["paid"]),
                "unpaid": [x for x in m["members"] if x not in m["paid"]],
            })
        return {
            "amount": self.amount,
            "waiting": list(self.waiting),
            "done": self.done,
            "months": months,
        }

    def save(self, path):
        data = {
            "amount": self.amount,
            "waiting": list(self.waiting),
            "done": self.done,
            "months": self.months,
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path):
        chama = cls()
        if Path(path).exists():
            data = json.loads(Path(path).read_text())
            chama.amount = data["amount"]
            chama.waiting = deque(data["waiting"])
            chama.done = data["done"]
            chama.months = data["months"]
        return chama
