const $ = (id) => document.getElementById(id);
const money = (n) => "KES " + n.toLocaleString();
const paid = new Set();
let state = null;

function el(tag, cls, text) {
  const node = document.createElement(tag);
  if (cls) node.className = cls;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function call(method, path, body) {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json();
  if (!res.ok) {
    $("msg").textContent = typeof data.detail === "string" ? data.detail : "Check what you typed.";
    return;
  }
  $("msg").textContent = "";
  state = data;
  render();
}

function potText() {
  const count = state.waiting.length + state.done.length;
  $("pot").textContent = `Collected ${money(paid.size * state.amount)} of ${money(count * state.amount)}`;
}

function render() {
  const members = [...state.waiting, ...state.done];
  for (const name of paid) {
    if (!members.includes(name)) paid.delete(name);
  }
  const roundOpen = state.waiting.length > 0;
  const next = state.waiting[0] || state.done[0];

  $("amount").value = state.amount;
  $("next").textContent = next || "nobody yet";
  $("close").textContent = next ? `Close month and pay ${next}` : "Close month";
  $("close").disabled = !next;

  $("checks").replaceChildren(
    ...members.map((name) => {
      const box = el("input");
      box.type = "checkbox";
      box.checked = paid.has(name);
      box.dataset.name = name;
      const label = el("label");
      label.append(box, ` ${name} paid`);
      const li = el("li");
      li.append(label);
      return li;
    })
  );
  potText();

  $("order").replaceChildren(
    ...members.map((name) => {
      const li = el("li", "", name);
      if (roundOpen && state.done.includes(name)) li.append(el("span", "muted", "received"));
      const b = el("button", "", "Remove");
      b.dataset.act = "remove";
      b.dataset.name = name;
      li.append(b);
      return li;
    })
  );

  $("history").replaceChildren(
    ...[...state.months].reverse().map((m) => {
      const li = el("li");
      li.append(el("strong", "", `Month ${m.n}`), ` ${m.payee} received ${money(m.pot)}`);
      for (const name of m.unpaid) {
        const b = el("button", "", `${name} paid late`);
        b.dataset.act = "late";
        b.dataset.n = m.n;
        b.dataset.name = name;
        li.append(b);
      }
      return li;
    })
  );
}

document.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-act]");
  if (!b) return;
  if (b.dataset.act === "remove") {
    if (confirm(`Remove ${b.dataset.name} from the rotation?`)) call("DELETE", `/api/members/${encodeURIComponent(b.dataset.name)}`);
  } else {
    call("POST", `/api/months/${b.dataset.n}/late`, { name: b.dataset.name });
  }
});

$("checks").addEventListener("change", (e) => {
  const name = e.target.dataset.name;
  if (e.target.checked) paid.add(name);
  else paid.delete(name);
  potText();
});

$("close").addEventListener("click", async () => {
  await call("POST", "/api/months", { paid: [...paid] });
  if (!$("msg").textContent) paid.clear();
  render();
});

$("addForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  await call("POST", "/api/members", { name: $("newname").value.trim() });
  if (!$("msg").textContent) $("newname").value = "";
});

$("amountForm").addEventListener("submit", (e) => {
  e.preventDefault();
  call("PUT", "/api/amount", { amount: Number($("amount").value) });
});

call("GET", "/api/chama");
