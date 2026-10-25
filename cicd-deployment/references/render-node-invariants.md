# Render fullstack Node/SPA invariants and failure diagnosis

Field-tested rules derived from production container debugging on Render:

1. **`npm install` DevDependency Retention**:
   - Render sets `NODE_ENV=production` inside build containers. Under this variable, npm automatically prunes `devDependencies` unless `--include=dev` is supplied.
   - **Mandatory Blueprint Setting:**
     ```yaml
     buildCommand: npm install --include=dev && npm run build
     ```
   - **Package Hardening:** Elevate core build tools (`vite`, `vue-tsc`, `typescript`, `tailwindcss`, `daisyui`) into `dependencies` in `package.json` so builds never throw `Exit Code 127: Command Not Found`.

2. **Explicit Node Runtime Pinning**:
   - Modern tooling (Vite 6, TypeScript 5.6+) requires Node 20+.
   - Add `"engines": { "node": ">=20.0.0" }` in `package.json`.
   - Specify `NODE_VERSION: 20` under `envVars` in `render.yaml`.

3. **`0.0.0.0` Host Binding**:
   - Express servers must explicitly bind to `0.0.0.0` (`app.listen(PORT, '0.0.0.0')`). Binding to default `localhost` or IPv6 loopback causes Render's IPv4 reverse-proxy port scanner to fail, timing out the deployment after 120 seconds.

4. **Zero-Downtime Health Probes**:
   - Expose explicit `GET /health` and `GET /api/health` endpoints returning HTTP 200 JSON `{ status: 'ok' }`.
   - Implement an express fallback for `GET /` if `dist/index.html` static bundles are building or pending.

5. **Diagnosing a failed deploy via the Render API (read-only first)**:
   - When a deploy fails or a health check times out, use `RENDER_API_KEY` to read `https://api.render.com/v1/services/{id}/events`.
   - Diagnose exit codes (`nonZeroExit: 127` means missing build dependencies).
   - Propose the fix (config patch via `PATCH /v1/services/{id}` or a code change) and ask the owner to confirm before applying it or triggering a fresh deploy with `clearCache: "clear"`. Do not patch services or redeploy on your own.
   - Validate post-deploy health using `ai-platform-sentinel`.
