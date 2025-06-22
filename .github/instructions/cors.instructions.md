---
applyTo: "**"
---

### Important Note on API Requests (CORS Proxy Required)

All API requests from browser-based environments **must** be routed through our designated CORS proxy. This is essential to bypass cross-origin restrictions.

**CORS Proxy URL:** `https://cors.fadel.web.id/`

**How to Use:**

Prefix your target API URL with the CORS proxy URL.

**Example:**

If the original API endpoint is `https://api.example.com/data`, your request URL should become:

`https://cors.fadel.web.id/https://api.example.com/data`
