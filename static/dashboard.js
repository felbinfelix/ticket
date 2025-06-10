// Simplified dashboard.js that loads and groups tickets
function groupTicketsByField(tickets, field) {
  return tickets.reduce((acc, ticket) => {
    const key = (ticket[field] || "Unknown").trim();
    if (!acc[key]) acc[key] = [];
    acc[key].push(ticket);
    return acc;
  }, {});
}

function sanitizeId(name) {
  return name.replace(/[^a-zA-Z0-9_-]/g, "_");
}

function loadData() {
  fetch("/data")
    .then(res => res.json())
    .then(data => {
      const validData = data.filter(t => t["ID"] && t["Group Name"]);
      const grouped = groupTicketsByField(validData, "Group Name");
      const tableContainer = document.getElementById("table-container");
      const tabsContainer = document.getElementById("group-tabs");
      tableContainer.innerHTML = "";
      tabsContainer.innerHTML = "";

      // All tab
      const allSection = document.createElement("div");
      allSection.classList.add("group-section", "active");
      allSection.id = "tab-All";
      const allTickets = Object.values(grouped).flat();
      allSection.appendChild(buildTable(allTickets));
      tableContainer.appendChild(allSection);

      Object.entries(grouped).forEach(([groupName, tickets]) => {
        const section = document.createElement("div");
        const safeId = sanitizeId(groupName);
        section.classList.add("group-section");
        section.id = `tab-${safeId}`;
        section.appendChild(buildTable(tickets));
        tableContainer.appendChild(section);
      });

      tabsContainer.appendChild(createTabButton("All", "All", true));
      Object.keys(grouped).forEach(groupName => {
        tabsContainer.appendChild(createTabButton(groupName, sanitizeId(groupName)));
      });
    });
}

function buildTable(tickets) {
  const table = document.createElement("table");
  const headers = Object.keys(tickets[0] || {});
  const thead = document.createElement("thead");
  const tr = document.createElement("tr");
  headers.forEach(h => {
    const th = document.createElement("th");
    th.textContent = h;
    tr.appendChild(th);
  });
  thead.appendChild(tr);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  tickets.forEach(row => {
    const tr = document.createElement("tr");
    headers.forEach(h => {
      const td = document.createElement("td");
      td.textContent = row[h] || "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function createTabButton(label, safeId, active) {
  const button = document.createElement("button");
  button.textContent = label;
  if (active) button.classList.add("active");
  button.onclick = () => {
    document.querySelectorAll(".tab-buttons button").forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    document.querySelectorAll(".group-section").forEach(s => s.classList.remove("active"));
    document.getElementById(`tab-${safeId}`).classList.add("active");
  };
  return button;
}

function syncData() {
  fetch("/sync", { method: "POST" })
    .then(res => res.json())
    .then(data => {
      alert("✅ Sync complete!");
      loadData();
    }).catch(err => {
      alert("❌ Sync failed.");
    });
}

window.addEventListener("DOMContentLoaded", loadData);
