const resources = {
  authors: {
    title: "Авторы", single: "автора",
    fields: [{ key: "name", label: "Имя автора", type: "text" }],
  },
  genres: {
    title: "Жанры", single: "жанр",
    fields: [{ key: "name", label: "Название жанра", type: "text" }],
  },
  books: {
    title: "Книги", single: "книгу",
    fields: [
      { key: "title", label: "Название книги", type: "text" },
      { key: "author_id", label: "Автор", type: "select", source: "authors" },
      { key: "genre_id", label: "Жанр", type: "select", source: "genres" },
    ],
  },
  readers: {
    title: "Читатели", single: "читателя",
    fields: [
      { key: "name", label: "Имя читателя", type: "text" },
      { key: "email", label: "Контактный email", type: "email" },
    ],
  },
  loans: {
    title: "Выдачи", single: "выдачу",
    fields: [
      { key: "book_id", label: "Книга", type: "select", source: "books" },
      { key: "reader_id", label: "Читатель", type: "select", source: "readers" },
      { key: "loan_date", label: "Дата выдачи", type: "date" },
      { key: "returned", label: "Книга возвращена", type: "checkbox" },
    ],
  },
};

let active = "authors";
let editingId = null;
let records = [];
let lookups = {};

const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
})[char]);

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = `Ошибка HTTP ${response.status}`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch { /* Keep the HTTP status. */ }
    throw new Error(detail);
  }
  return response.status === 204 ? null : response.json();
}

function feedback(message, isError = false) {
  const box = $("#feedback");
  box.textContent = message;
  box.classList.toggle("error", isError);
}

function displayValue(field, value) {
  if (field.type === "checkbox") return value ? "Да" : "Нет";
  if (field.type === "select") {
    const match = (lookups[field.source] || []).find((item) => item.id === value);
    return match ? (match.title || match.name) : `#${value}`;
  }
  return value;
}

function renderTabs() {
  $("#tabs").innerHTML = Object.entries(resources).map(([key, item]) =>
    `<button type="button" class="tab ${key === active ? "active" : ""}" data-tab="${key}">${item.title}</button>`
  ).join("");
}

function renderRecords() {
  const fields = resources[active].fields;
  if (!records.length) {
    $("#records").innerHTML = '<p class="empty">Записей пока нет. Добавьте первую запись справа.</p>';
    return;
  }
  const headers = fields.map((field) => `<th>${escapeHtml(field.label)}</th>`).join("");
  const body = records.map((item) => `
    <tr>
      <td>${item.id}</td>
      ${fields.map((field) => `<td>${escapeHtml(displayValue(field, item[field.key]))}</td>`).join("")}
      <td>
        <button class="text-button" type="button" data-edit="${item.id}">Изменить</button>
        <button class="text-button danger" type="button" data-delete="${item.id}">Удалить</button>
      </td>
    </tr>
  `).join("");
  $("#records").innerHTML = `<table><thead><tr><th>ID</th>${headers}<th>Действия</th></tr></thead><tbody>${body}</tbody></table>`;
}

function renderForm(item = null) {
  editingId = item?.id ?? null;
  $("#form-eyebrow").textContent = item ? `Запись #${item.id}` : "Новая запись";
  $("#form-title").textContent = `${item ? "Изменить" : "Добавить"} ${resources[active].single}`;
  const fields = resources[active].fields.map((field) => {
    const value = item?.[field.key];
    if (field.type === "checkbox") {
      return `<label class="field check-field"><input name="${field.key}" type="checkbox" ${value ? "checked" : ""}><span class="field-label">${field.label}</span></label>`;
    }
    if (field.type === "select") {
      const options = (lookups[field.source] || []).map((choice) =>
        `<option value="${choice.id}" ${choice.id === value ? "selected" : ""}>${escapeHtml(choice.title || choice.name)}</option>`
      ).join("");
      return `<label class="field"><span class="field-label">${field.label}</span><select name="${field.key}" required><option value="">Выберите…</option>${options}</select></label>`;
    }
    const initial = value ?? (field.type === "date" ? new Date().toISOString().slice(0, 10) : "");
    return `<label class="field"><span class="field-label">${field.label}</span><input name="${field.key}" type="${field.type}" value="${escapeHtml(initial)}" required></label>`;
  }).join("");
  $("#record-form").innerHTML = `${fields}<div class="form-actions"><button class="button" type="submit">${item ? "Сохранить" : "Добавить"}</button>${item ? '<button class="button button-secondary" type="button" id="cancel-edit">Отмена</button>' : ""}</div>`;
}

async function loadResource() {
  const config = resources[active];
  const sources = [...new Set(config.fields.filter((field) => field.source).map((field) => field.source))];
  try {
    const loaded = await Promise.all([
      request(`/api/${active}`),
      ...sources.map((source) => request(`/api/${source}`)),
    ]);
    records = loaded[0];
    sources.forEach((source, index) => { lookups[source] = loaded[index + 1]; });
    $("#section-title").textContent = config.title;
    renderTabs();
    renderRecords();
    renderForm();
  } catch (error) {
    feedback(error.message, true);
  }
}

$("#tabs").addEventListener("click", async (event) => {
  const tab = event.target.closest("[data-tab]");
  if (!tab) return;
  active = tab.dataset.tab;
  feedback("");
  await loadResource();
});

$("#refresh-button").addEventListener("click", loadResource);

$("#records").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-edit]");
  if (edit) {
    renderForm(records.find((item) => item.id === Number(edit.dataset.edit)));
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  const remove = event.target.closest("[data-delete]");
  if (!remove) return;
  const id = Number(remove.dataset.delete);
  if (!confirm(`Удалить запись #${id}?`)) return;
  try {
    await request(`/api/${active}/${id}`, { method: "DELETE" });
    await loadResource();
    feedback("Запись удалена.");
  } catch (error) {
    feedback(error.message, true);
  }
});

$("#record-form").addEventListener("click", (event) => {
  if (event.target.id === "cancel-edit") renderForm();
});

$("#record-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const config = resources[active];
  const data = new FormData(event.currentTarget);
  const body = {};
  config.fields.forEach((field) => {
    body[field.key] = field.type === "checkbox" ? data.has(field.key)
      : field.type === "select" ? Number(data.get(field.key))
      : data.get(field.key);
  });
  const wasEditing = editingId !== null;
  try {
    await request(`/api/${active}${wasEditing ? `/${editingId}` : ""}`, {
      method: wasEditing ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    await loadResource();
    feedback(wasEditing ? "Изменения сохранены." : "Запись добавлена.");
  } catch (error) {
    feedback(error.message, true);
  }
});

loadResource();
