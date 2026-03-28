# Story Splitting Patterns

Seven patterns for breaking oversized stories into vertical slices that each deliver end-to-end value.

## 1. Workflow Steps

Build the minimal happy path first, then add branches and alternate flows.

**Example:**
- Epic: "User can complete a booking"
- Split:
  - Story 1: User can select a date and submit a booking request
  - Story 2: User receives confirmation email after booking
  - Story 3: User can cancel a booking
  - Story 4: User can modify a booking date

**When to use:** The story describes a multi-step workflow where the first step alone has value.

## 2. Operations (CRUD)

Separate create, read, update, and delete into individual stories.

**Example:**
- Epic: "Admin can manage service categories"
- Split:
  - Story 1: Admin can view list of service categories
  - Story 2: Admin can create a new service category
  - Story 3: Admin can edit an existing service category
  - Story 4: Admin can delete a service category

**When to use:** The story involves managing a resource with multiple operations.

## 3. Business Rule Variations

Start with the simplest business rule, then layer in complexity.

**Example:**
- Epic: "System calculates pricing for quotes"
- Split:
  - Story 1: System applies flat rate pricing to a quote
  - Story 2: System applies weight-based pricing tiers
  - Story 3: System applies promotional discount codes
  - Story 4: System calculates tax based on location

**When to use:** Multiple business rules apply to the same feature, and each rule can ship independently.

## 4. Data Variations

Start with a single data type or simple input, then expand.

**Example:**
- Epic: "User can upload documents to a job"
- Split:
  - Story 1: User can upload a single PDF to a job
  - Story 2: User can upload multiple files at once
  - Story 3: User can upload images (JPG, PNG) to a job
  - Story 4: User can drag-and-drop files to upload

**When to use:** The story handles multiple data types or input formats that can be delivered incrementally.

## 5. Simple/Complex

Ship the simple version first, defer edge cases and advanced scenarios.

**Example:**
- Epic: "User can search for available tradies"
- Split:
  - Story 1: User can search tradies by postcode
  - Story 2: User can filter search results by trade type
  - Story 3: User can filter by availability date range
  - Story 4: User sees search results ranked by rating and proximity

**When to use:** The story has a core behavior that's valuable on its own, plus edge cases and enhancements that add polish.

## 6. Defer Performance

Make it work first, then make it fast.

**Example:**
- Epic: "Dashboard loads job history with real-time metrics"
- Split:
  - Story 1: Dashboard displays job history (basic query, no caching)
  - Story 2: Dashboard paginates job history for large datasets
  - Story 3: Dashboard caches frequently accessed metrics for sub-second load

**When to use:** The story bundles functional requirements with performance requirements. Separate them — correctness first, optimization second.

## 7. Break Out a Spike

When unknowns are too large to estimate or split, time-box an investigation.

**Example:**
- Epic: "Integrate with Xero for invoicing"
- Split:
  - Spike: Investigate Xero API capabilities and authentication flow (2 days)
  - Story 1: System authenticates with Xero using OAuth (after spike)
  - Story 2: System creates an invoice in Xero when a job is completed
  - Story 3: System syncs payment status from Xero

**When to use:** The team can't estimate or split because they don't understand the domain, technology, or integration well enough. The spike produces knowledge, not software.

---

## Splitting Validation

After splitting, apply this test to each resulting story:

1. **Does it deliver end-to-end value?** A user could validate the outcome.
2. **Is it independently deployable?** It could ship without the other stories.
3. **Is it small enough to complete in a sprint?** If not, split again.
4. **Does it avoid horizontal slicing?** It's not "build the API" or "create the schema" — it crosses all layers.

If any story fails these checks, it's a horizontal slice or a task — not a story. Re-split.
