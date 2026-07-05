## Answer

Auth and role enforcement is **primarily done at the API layer** (Fastify middleware + route `preHandler` hooks). The database has one small exception: RLS is enabled on `user_problem_attempts` to enforce row-level ownership (`user_id = auth.uid()`), but all role-based access control (creator/reviewer/admin vs. learner) lives entirely in the API. To add a reviewer-only endpoint, use `preHandler: [requireAuth, requireRole('reviewer', 'admin')]` — no DB changes needed.

---

## Key Findings

1. **JWT verification happens in a global `onRequest` hook** — `src/plugins/auth.ts` registers an `onRequest` hook that reads `Authorization: Bearer <token>`, verifies it against Supabase's JWKS endpoint, and populates `request.user = { sub, email, role }`. Invalid or absent tokens leave `request.user` undefined; the hook never rejects — it just doesn't populate the user. [Confidence: high — source is the file itself, verified 2026-06-10]

2. **The `user_role` claim in the JWT is injected by a Postgres function, not Supabase defaults.** `supabase/migrations/00000000000001_schema.sql` defines `public.custom_access_token_hook`, a Postgres function registered in `supabase/config.toml` as `[auth.hook.custom_access_token]`. It looks up `public.users.role` for the signing user and injects it as `user_role` into the JWT claims. The API reads this as `payload.user_role`, defaulting to `'learner'` if absent. [Confidence: high — migration + config file, both read 2026-06-10]

3. **Role enforcement at the route level is done with two exported functions from `src/plugins/auth.ts`:**
   - `requireAuth` — returns 401 if `request.user` is undefined.
   - `requireRole(...roles)` — returns 401 if unauthenticated, 403 if authenticated but role not in the allowlist.
   - Both are used as Fastify `preHandler` arrays: `preHandler: [requireAuth, requireRole('creator', 'reviewer', 'admin')]`.
   [Confidence: high — source is `src/plugins/auth.ts`, confirmed by grep across all route files]

4. **Every mutating route (POST/PUT/DELETE) for content objects requires `creator | reviewer | admin`.** This applies uniformly across domains, topics, concepts, edges, lessons, and problems. The `reviewer` role is currently bundled identically with `creator` — no existing endpoint distinguishes between them; reviewers have full write access everywhere creators do. [Confidence: high — verified via grep of all route files]

5. **The one database-level enforcement is RLS on `user_problem_attempts`** — only the row's `user_id` can SELECT or INSERT their own rows. This is ownership enforcement, not role enforcement. No other table has RLS enabled. The `db` client in `src/db/client.ts` connects with `DATABASE_URL` (the service-role or admin connection string), which bypasses RLS — meaning the API layer is authoritative for all role checks, since the DB won't enforce them on its own. [Confidence: high — migration 00000000000007, db client file, both read 2026-06-10]

6. **Role stored in `public.users.role` (text column, default 'learner').** Valid values referenced in code: `learner`, `creator`, `reviewer`, `admin`. Changing a user's role requires a direct DB update to `public.users` and a re-login to get a fresh JWT with the updated `user_role` claim (the hook runs at token-issue time). [Confidence: high — schema + test helpers]

---

## How Auth Works End-to-End

```
[Client]  →  POST /auth/v1/token (Supabase GoTrue)
                 ↓ triggers custom_access_token_hook (Postgres fn)
                 ↓ looks up public.users.role → injects user_role into JWT claims
             ← JWT with { sub, email, user_role: "reviewer" }

[Client]  →  POST /api/concepts/:id/lessons
             Authorization: Bearer <jwt>
                 ↓ onRequest hook (src/plugins/auth.ts)
                 ↓ jwtVerify against Supabase JWKS
                 ↓ request.user = { sub, email, role: "reviewer" }
                 ↓ preHandler: [requireAuth, requireRole('creator', 'reviewer', 'admin')]
                    requireAuth: request.user exists ✓
                    requireRole: "reviewer" in ['creator','reviewer','admin'] ✓
                 ↓ route handler executes
             ← 201 Created
```

For draft visibility (GET endpoints), the pattern is inline logic in the handler:
```ts
const canSeeDrafts = request.user && ['creator', 'reviewer', 'admin'].includes(request.user.role);
```
This is checked after the route is entered (no preHandler gate for GET), so unauthenticated users just get published-only results rather than a 401.

---

## How to Add a Reviewer-Only Endpoint

```ts
import { requireAuth, requireRole } from '../plugins/auth.js';

app.get('/api/review/queue', {
  schema: { security: [{ bearerAuth: [] }] },
  preHandler: [requireAuth, requireRole('reviewer', 'admin')],
}, async (request, reply) => {
  // request.user is guaranteed non-null here, with role 'reviewer' or 'admin'
});
```

No DB migration needed. No RLS changes needed. The role is already in the JWT (as long as the user's `public.users.role` is set to `reviewer` and they've logged in since that change).

---

## Contradictions & Surprises

- **No distinction between reviewer and creator in current routes.** Despite `reviewer` being a distinct role in the schema and referenced in planning docs, every existing protected route gates on `requireRole('creator', 'reviewer', 'admin')`. Reviewer is a superset of learner but currently identical in permissions to creator. If the intent is for reviewer to have different (potentially narrower) write access than creator, the current implementation doesn't enforce that — it would need to.

- **The `db` client bypasses RLS.** `src/db/client.ts` uses a single `DATABASE_URL` connection (the service-role key). This means Drizzle queries run as a superuser relative to RLS — row-level security on `user_problem_attempts` only matters if you ever connect with a user-scoped JWT (e.g., via Supabase client). The API's Drizzle client can read any user's attempts. The API enforces ownership by filtering on `userId` in the query, not by relying on RLS.

---

## Sources

- `src/plugins/auth.ts` — JWT verification, `requireAuth`, `requireRole` — verified 2026-06-10
- `src/app.ts` — plugin registration order — verified 2026-06-10
- `src/routes/lessons.ts`, `domains.ts`, `topics.ts`, `concepts.ts`, `edges.ts`, `problems.ts` — preHandler patterns — verified 2026-06-10
- `supabase/migrations/00000000000001_schema.sql` — `custom_access_token_hook`, `handle_new_user` trigger — verified 2026-06-10
- `supabase/migrations/00000000000007_user_problem_attempts.sql` — only table with RLS — verified 2026-06-10
- `supabase/config.toml` — `[auth.hook.custom_access_token]` registration — verified 2026-06-10
- `src/db/client.ts` — single Drizzle client with service-role URL — verified 2026-06-10
- `src/test-helpers.ts` — confirms `user_role` JWT claim shape and role values — verified 2026-06-10

---

## Open Questions

- What should `reviewer`-only actually mean? Currently reviewers have identical write access to creators. If the new endpoint should be reviewer-exclusive (creators can't hit it), that's supported — just use `requireRole('reviewer', 'admin')`. If reviewer should have read-only access on existing mutation routes, those routes would need updating too.
- Is there an admin-only management endpoint needed eventually (e.g., role assignment)? Not implemented yet.

---

## Promote to context/

**Auth is API-layer-only for role enforcement; DB provides identity anchoring only.**
- Role source of truth: `public.users.role` (text column)
- Role in JWT: `user_role` claim, injected at token-issue time by `custom_access_token_hook`
- Role in API: `request.user.role`, populated by global `onRequest` hook via JWKS verification
- Enforcement mechanism: `requireRole(...roles)` preHandler on each protected route
- DB layer: no role-based RLS exists; only `user_problem_attempts` has ownership RLS (uid-scoped)
- Drizzle client: service-role connection, bypasses all RLS
