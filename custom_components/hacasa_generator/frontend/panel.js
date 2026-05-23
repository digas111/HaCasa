const DEFAULT_CONFIG = {
  name: "New HaCasa Dashboard",
  theme: "HaCasa Gold",
  icon: "mdi:view-dashboard",
  overview: {},
  navigation: [],
  rooms: [
    {
      name: "Living Room",
      area: "living_room",
      path: "room-living-room",
      icon: "mdi:sofa-outline",
      entities: {
        light: [],
        cover: [],
        climate: []
      },
      exclude: [],
      overrides: {}
    }
  ]
};

const cloneDefaultConfig = () => JSON.parse(JSON.stringify(DEFAULT_CONFIG));

class HaCasaGeneratorPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._configs = [];
    this._selectedId = null;
    this._config = cloneDefaultConfig();
    this._status = "";
    this._error = "";
    this._preview = null;
    this._renderResult = null;
    this._loaded = false;
  }

  set hass(value) {
    this._hass = value;
    if (!this._loaded) {
      this._loaded = true;
      this._loadConfigs();
    }
  }

  get hass() {
    return this._hass;
  }

  connectedCallback() {
    this.shadowRoot.addEventListener("click", (event) => this._handleClick(event));
    this.shadowRoot.addEventListener("input", (event) => this._handleInput(event));
    this._render();
  }

  async _call(type, payload = {}) {
    if (!this._hass) {
      throw new Error("Home Assistant is not ready yet");
    }
    return this._hass.connection.sendMessagePromise({ type, ...payload });
  }

  _errorMessage(error) {
    if (!error) {
      return "Unknown error";
    }
    if (typeof error === "string") {
      return error;
    }
    if (error.message && error.code) {
      return `${error.message} (${error.code})`;
    }
    if (error.message) {
      return error.message;
    }
    if (error.code) {
      return error.code;
    }
    try {
      return JSON.stringify(error);
    } catch (_jsonError) {
      return String(error);
    }
  }

  async _loadConfigs() {
    try {
      this._configs = await this._call("hacasa_generator/list_configs");
      if (this._configs.length > 0 && !this._selectedId) {
        await this._selectConfig(this._configs[0].id);
      } else {
        this._render();
      }
    } catch (error) {
      this._error = this._errorMessage(error);
      this._render();
    }
  }

  async _selectConfig(id) {
    try {
      const item = await this._call("hacasa_generator/get_config", { config_id: id });
      this._selectedId = item.id;
      this._config = item.config || cloneDefaultConfig();
      this._status = "";
      this._error = "";
      this._preview = null;
      this._renderResult = null;
      this._render();
    } catch (error) {
      this._error = this._errorMessage(error);
      this._render();
    }
  }

  _newConfig() {
    this._selectedId = null;
    this._config = cloneDefaultConfig();
    this._status = "";
    this._error = "";
    this._preview = null;
    this._renderResult = null;
    this._render();
  }

  _readEditorConfig() {
    const name = this.shadowRoot.querySelector("#dashboard-name")?.value.trim();
    const raw = this.shadowRoot.querySelector("#json-editor")?.value || "{}";
    const config = JSON.parse(raw);
    const previousNameSlug = this._slug(config.name);
    const previousSlug = config.slug ? this._slug(config.slug) : "";
    if (name) {
      config.name = name;
    }
    if (!previousSlug || previousSlug === previousNameSlug) {
      config.slug = this._slug(config.name);
    }
    return config;
  }

  async _save() {
    try {
      const config = this._readEditorConfig();
      const item = await this._call("hacasa_generator/save_config", {
        config_id: this._selectedId || undefined,
        config
      });
      this._selectedId = item.id;
      this._config = item.config;
      this._status = "Configuration saved.";
      this._error = "";
      await this._loadConfigs();
    } catch (error) {
      this._error = this._errorMessage(error);
      this._status = "";
      this._render();
    }
  }

  async _previewConfig() {
    try {
      const config = this._readEditorConfig();
      this._preview = await this._call("hacasa_generator/preview", { config });
      this._config = config;
      this._status = "Preview refreshed.";
      this._error = "";
      this._render();
    } catch (error) {
      this._error = this._errorMessage(error);
      this._status = "";
      this._render();
    }
  }

  async _renderDashboard() {
    try {
      const config = this._readEditorConfig();
      this._renderResult = await this._call("hacasa_generator/render", {
        config_id: this._selectedId || undefined,
        config
      });
      this._selectedId = this._renderResult.config.id;
      this._config = this._renderResult.config.config;
      this._status = "Dashboard rendered.";
      this._error = "";
      await this._loadConfigs();
      this._render();
    } catch (error) {
      this._error = this._errorMessage(error);
      this._status = "";
      this._render();
    }
  }

  async _deleteConfig() {
    if (!this._selectedId) {
      return;
    }
    try {
      await this._call("hacasa_generator/delete_config", { config_id: this._selectedId });
      this._newConfig();
      await this._loadConfigs();
    } catch (error) {
      this._error = this._errorMessage(error);
      this._render();
    }
  }

  _handleClick(event) {
    const action = event.target?.closest("[data-action]")?.dataset.action;
    if (!action) {
      return;
    }
    const id = event.target.closest("[data-id]")?.dataset.id;
    if (action === "select" && id) this._selectConfig(id);
    if (action === "new") this._newConfig();
    if (action === "save") this._save();
    if (action === "preview") this._previewConfig();
    if (action === "render") this._renderDashboard();
    if (action === "delete") this._deleteConfig();
  }

  _handleInput(event) {
    if (event.target?.id === "dashboard-name") {
      const previousNameSlug = this._slug(this._config.name);
      const previousSlug = this._config.slug ? this._slug(this._config.slug) : "";
      this._config = { ...this._config, name: event.target.value };
      if (!previousSlug || previousSlug === previousNameSlug) {
        this._config.slug = this._slug(event.target.value);
      }
      this._renderSlugOnly();
    }
  }

  _renderSlugOnly() {
    const slug = this.shadowRoot.querySelector("#slug-preview");
    if (slug) {
      slug.textContent = this._slug(this._config.slug || this._config.name);
    }
  }

  _slug(value) {
    return (value || "dashboard")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "dashboard";
  }

  _snapshotEditor() {
    const activeElement = this.shadowRoot.activeElement;
    const activeId = activeElement?.id;
    if (activeId !== "dashboard-name" && activeId !== "json-editor") {
      return {};
    }

    return {
      activeId,
      name: this.shadowRoot.querySelector("#dashboard-name")?.value,
      json: this.shadowRoot.querySelector("#json-editor")?.value,
      selectionStart: activeElement.selectionStart,
      selectionEnd: activeElement.selectionEnd,
      scrollTop: activeElement.scrollTop
    };
  }

  _restoreEditor(snapshot) {
    if (!snapshot.activeId) {
      return;
    }
    const element = this.shadowRoot.querySelector(`#${snapshot.activeId}`);
    if (!element) {
      return;
    }
    element.focus({ preventScroll: true });
    if (Number.isInteger(snapshot.selectionStart) && Number.isInteger(snapshot.selectionEnd)) {
      element.setSelectionRange(snapshot.selectionStart, snapshot.selectionEnd);
    }
    if (Number.isInteger(snapshot.scrollTop)) {
      element.scrollTop = snapshot.scrollTop;
    }
  }

  _render() {
    const editorSnapshot = this._snapshotEditor();
    const configText = editorSnapshot.json ?? JSON.stringify(this._config, null, 2);
    const dashboardName = editorSnapshot.name ?? this._config.name ?? "";
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          min-height: 100vh;
          color: var(--primary-text-color);
          background: var(--primary-background-color);
          font-family: var(--primary-font-family, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif);
        }
        .layout {
          display: grid;
          grid-template-columns: 280px 1fr;
          min-height: 100vh;
        }
        aside {
          border-right: 1px solid var(--divider-color);
          background: var(--card-background-color, var(--ha-card-background));
          padding: 16px;
        }
        main {
          padding: 22px;
          max-width: 1180px;
        }
        h1 {
          margin: 0 0 18px;
          font-size: 22px;
          font-weight: 800;
        }
        h2 {
          margin: 0 0 10px;
          font-size: 15px;
          font-weight: 800;
        }
        button {
          height: 38px;
          border: 0;
          border-radius: 8px;
          padding: 0 14px;
          font-weight: 700;
          color: var(--text-primary-color, white);
          background: var(--primary-color);
          cursor: pointer;
        }
        button.secondary {
          color: var(--primary-text-color);
          background: var(--secondary-background-color);
        }
        button.danger {
          color: white;
          background: var(--error-color, #db4437);
        }
        .config-list {
          display: grid;
          gap: 8px;
          margin-top: 14px;
        }
        .config-item {
          width: 100%;
          height: auto;
          min-height: 48px;
          justify-content: flex-start;
          text-align: left;
          color: var(--primary-text-color);
          background: var(--secondary-background-color);
        }
        .config-item[selected] {
          color: var(--text-primary-color, white);
          background: var(--primary-color);
        }
        .toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin: 18px 0;
        }
        .field {
          display: grid;
          gap: 6px;
          margin-bottom: 14px;
        }
        label {
          font-size: 12px;
          font-weight: 800;
          color: var(--secondary-text-color);
          text-transform: uppercase;
        }
        input, textarea {
          width: 100%;
          box-sizing: border-box;
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 10px 12px;
          color: var(--primary-text-color);
          background: var(--card-background-color, var(--ha-card-background));
          font: inherit;
        }
        textarea {
          min-height: 520px;
          font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
          font-size: 13px;
          line-height: 1.45;
        }
        .meta {
          color: var(--secondary-text-color);
          font-size: 13px;
        }
        .message {
          margin: 12px 0;
          padding: 12px;
          border-radius: 8px;
          background: color-mix(in srgb, var(--primary-color) 14%, transparent);
        }
        .error {
          background: color-mix(in srgb, var(--error-color, #db4437) 16%, transparent);
          color: var(--error-color, #db4437);
        }
        .panels {
          display: grid;
          grid-template-columns: minmax(0, 1fr) 360px;
          gap: 18px;
        }
        .panel {
          border: 1px solid var(--divider-color);
          border-radius: 8px;
          padding: 14px;
          background: var(--card-background-color, var(--ha-card-background));
        }
        pre {
          overflow: auto;
          max-height: 360px;
          margin: 0;
          font-size: 12px;
          line-height: 1.45;
          white-space: pre-wrap;
        }
        @media (max-width: 860px) {
          .layout, .panels {
            grid-template-columns: 1fr;
          }
          aside {
            border-right: 0;
            border-bottom: 1px solid var(--divider-color);
          }
        }
      </style>
      <div class="layout">
        <aside>
          <h1>HaCasa Generator</h1>
          <button data-action="new">Add dashboard</button>
          <div class="config-list">
            ${this._configs.map((item) => `
              <button class="config-item" data-action="select" data-id="${this._escape(item.id)}" ${item.id === this._selectedId ? "selected" : ""}>
                <span>${this._escape(item.name)}</span><br>
                <small>${this._escape(item.slug)}</small>
              </button>
            `).join("")}
          </div>
        </aside>
        <main>
          <h1>${this._selectedId ? "Edit dashboard" : "New dashboard"}</h1>
          ${this._status ? `<div class="message">${this._escape(this._status)}</div>` : ""}
          ${this._error ? `<div class="message error">${this._escape(this._error)}</div>` : ""}
          <div class="field">
            <label for="dashboard-name">Name</label>
            <input id="dashboard-name" value="${this._escape(dashboardName)}">
            <div class="meta">Render folder: /config/dashboard/HaCasa/<span id="slug-preview">${this._escape(this._slug(this._config.slug || dashboardName))}</span></div>
          </div>
          <div class="toolbar">
            <button data-action="save">Save</button>
            <button class="secondary" data-action="preview">Preview entities</button>
            <button data-action="render">Render dashboard</button>
            ${this._selectedId ? `<button class="danger" data-action="delete">Delete</button>` : ""}
          </div>
          <div class="panels">
            <div class="field">
              <label for="json-editor">Dashboard JSON</label>
              <textarea id="json-editor" spellcheck="false">${this._escape(configText)}</textarea>
            </div>
            <div class="panel">
              <h2>Preview</h2>
              ${this._preview ? `<pre>${this._escape(JSON.stringify(this._preview, null, 2))}</pre>` : `<div class="meta">Run preview to resolve areas and entity overrides.</div>`}
              ${this._renderResult ? `
                <h2 style="margin-top:18px;">Last render</h2>
                <pre>${this._escape(JSON.stringify(this._renderResult, null, 2))}</pre>
                <div class="message">Home Assistant needs a restart when configuration.yaml changed.</div>
              ` : ""}
            </div>
          </div>
        </main>
      </div>
    `;
    this._restoreEditor(editorSnapshot);
  }

  _escape(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }
}

customElements.define("hacasa-generator-panel", HaCasaGeneratorPanel);
