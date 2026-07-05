## Answer

Role enforcement lives entirely in the **API layer** (Fastify `preHandler` hooks), not the database. The database has RLS on exactly one table (`user_problem_attempts`), and that policy is about row ownership (users can only see their own attempts), not roles. The role itself is embedded in the JWT via a Supabase custom access token hook and read by the Fastify auth plugin on every request.

---

## Key Findings

1. **Role enforcement is Fastify `preHandler` hooks, not RLS.** Every write/mutate endpoint uses `preHandler: [requireAuth, requireRole('creator', 'reviewer', 'admin')]`. The database has no role-based RLS policies — only one ownership-based RLS policy on `user_problem_attempts`. [Confidence: high]

2. **The role claim lives in the JWT, sourced from `public.users.role`.** A Supabase custom access token hook (`public.custom_access_token_hook`) fires at JWT mint time, reads `public.users.role` for the signing user, and injects a `user_role` claim into the JWT payload. The Fastify auth plugin reads `payload.user_role` and sets `request.user.role`. [Confidence: high]

3. **`reviewer` has the same permissions as `creator` everywhere today.** The `requireRole` call on all existing write endpoints is `requireRole('creator', 'reviewer', 'admin')`. There is no endpoint today that is reviewer-exclusive. [Confidence: high]

4. **Draft visibility uses an inline role check, not `requireRole`.** For read-only endpoints that filter by publish status (lessons, problems), the route checks `request.user?.role` inline to decide whether to include drafts. This is separate from the `preHandler` gate. [Confidence: high]

5. **The `public.users` table is the source of truth for role.** Role defaults to `'learner'` on signup (via `handle_new_user` trigger). Upgrading a user's role means updating `public.users.role`, then on next sign-in the new role flows into the JWT via the hook. [Confidence: high]

---

## How It Works (Auth Flow)

```
1. User signs up → handle_new_user trigger → public.users row created, role = 'learner'

2. User signs in → Supabase GoTrue mints JWT →
   custom_access_token_hook fires → reads public.users.role →
   injects user_role claim into JWT

3. Client sends: Authorization: Bearer <jwt>

4. Fastify onRequest hook (auth plugin) →
   jwtVerify(token, JWKS from Supabase) →
   sets request.user = { sub, email, role: payload.user_role || 'learner' }

5. Protected routes use preHandler:
   - requireAuth   → 401 if request.user is undefined
   - requireRole('creator','reviewer','admin')  → 403 if role not in list
```

**Role values:** `learner` (default), `creator`, `reviewer`, `admin`

---

## Adding a Reviewer-Only Endpoint

Use the exact same pattern as existing write endpoints, but pass only `'reviewer'` and `'admin'` to `requireRole`:

```ts
import { requireAuth, requireRole } from '../plugins/auth.js';

app.post('/api/some-resource/review', {
  schema: {
    body: ReviewSchema,
    security: [{ bearerAuth: [] }],
  },
  preHandler: [requireAuth, requireRole('reviewer', 'admin')],
}, async (request, reply) => {
  // request.user.role is guaranteed to be 'reviewer' or 'admin' here
});
```

No database changes needed. No RLS to configure. The role is already in the JWT.

---

## Sources

- `/home/juiz/Projects/arboreus-api/src/plugins/auth.ts` — `requireAuth` and `requireRole` implementations; JWT verification via JWKS
- `/home/juiz/Projects/arboreus-api/src/db/schema/users.ts` — `public.users` schema with `role` column
- `/home/juiz/Projects/arboreus-api/supabase/migrations/00000000000001_schema.sql` — `handle_new_user` trigger + `custom_access_token_hook`
- `/home/juiz/Projects/arboreus-api/supabase/migrations/00000000000007_user_problem_attempts.sql` — only RLS in the codebase (ownership-based, not role-based)
- `/home/juiz/Projects/arboreus-api/src/routes/domains.ts`, `concepts.ts`, `topics.ts`, `edges.ts`, `lessons.ts`, `problems.ts` — consistent `preHandler` pattern across all write routes
- `/home/juiz/Projects/arboreus-api/src/test-helpers.ts` — confirms four valid roles: `learner | creator | reviewer | admin`
- `/home/juiz/Projects/arboreus-api/src/auth.integration.test.ts` — documents JWT contracts (Contract 1.2: JWT contains `user_role`)
- `/home/juiz/Projects/arboreus-api/src/app.ts` — auth plugin registered before all route plugins

---

## Contradictions & Surprises

- The `reviewer` role exists in the type system and is accepted on all write routes, but no endpoint today is *exclusively* reviewer-gated. Every existing write endpoint grants access to `creator | reviewer | admin` equally. A reviewer-only endpoint would be the first that distinguishes reviewer from creator.
- RLS is notably absent from the main content tables (`domains`, `topics`, `concepts`, `lessons`, `problems`). Only `user_problem_attempts` has RLS, and it's row-ownership scoped, not role-scoped. Role enforcement is 100% the API layer's job.
- If `SUPABASE_URL` is not set, the auth plugin disables itself with a warning and all routes become unauthenticated. This is a local dev escape hatch, not a production concern.

---

## Open Questions

- Is there a plan to restrict which roles can *create* content vs which can only *review/approve* it? Right now `creator` and `reviewer` have identical write permissions — so `reviewer` is just an alias.
- Should a reviewer-only endpoint (e.g., approve/publish) prevent creators from calling it? That would be the first meaningful role split and the `requireRole` function handles it cleanly.
- The role-in-JWT approach means role changes take effect on next sign-in, not immediately. If reviewer access needs to be revokable in real time, that would require a different check (e.g., re-reading from `public.users` on each request).
