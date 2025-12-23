# MCP Service - Endpoints Quick Reference

**Base URL:** `https://mcp.openanalyst.com`
**Auth:** `X-API-Key` header required (except health & callback)

---

## Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tools/health` | Health check (no auth) |

---

## Integrations

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/integrations` | List all available integrations |
| GET | `/api/integrations?detailed=false` | Simple list (names only) |
| GET | `/api/integrations/connected?user_id={id}` | Get user's connected integrations |
| GET | `/api/integrations/{provider}/status?user_id={id}` | Check if user has provider connected |
| POST | `/api/integrations/connect` | Initiate OAuth flow |
| POST | `/api/integrations/disconnect` | Disconnect an integration |
| GET | `/api/integrations/callback` | OAuth callback (no auth, internal) |

### Connect Request Body
```json
{"user_id": "xxx", "provider": "gmail", "redirect_url": "https://...", "force_reauth": false}
```

### Disconnect Request Body
```json
{"user_id": "xxx", "provider": "gmail"}
```

---

## Tools

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tools?user_id={id}` | Get user's available tools |
| GET | `/api/tools/actions/{provider}` | List all actions for a provider |
| GET | `/api/tools/actions/{provider}?include_schema=false` | Actions without schema |
| GET | `/api/tools/schema/{action}` | Get schema for specific action |
| POST | `/api/tools/execute` | Execute a tool |

### Execute Request Body
```json
{"user_id": "xxx", "action": "GMAIL_SEND_EMAIL", "params": {...}}
```

---

## Supported Providers

| Provider | Category |
|----------|----------|
| `gmail` | Email |
| `slack` | Communication |
| `whatsapp` | Communication |
| `googledocs` | Productivity |
| `googlesheets` | Productivity |
| `googledrive` | Storage |
| `googlebigquery` | Data |
| `googlemeet` | Video |
| `googleads` | Marketing |
| `googlemaps` | Location |
| `zoom` | Video |
| `youtube` | Media |
| `supabase` | Database |
| `linkedin` | Social |
| `facebook` | Social |
| `stripe` | Payment |

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 307 | Redirect (OAuth) |
| 400 | Bad request |
| 401 | Invalid API key |
| 404 | Not found |
| 422 | Validation error |
| 500 | Server error |
