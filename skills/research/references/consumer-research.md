# Consumer & Enthusiast Research Strategy

For questions about products, hobbies, recommendations, reviews, services, local businesses, and any domain where personal experience and community consensus matter more than official documentation.

## The Core Problem

Web search for consumer topics is an **SEO graveyard**. The top results for "best X 2025" are affiliate-driven listicles recycling the same 10 recommendations. The actual signal lives in **specialist communities** where real users share daily experience — but search engines are bad at surfacing this.

**The strategy is inverted from technical research:** instead of starting broad and narrowing, start narrow (specialist communities) and only go broad to fill gaps.

## Where the Signal Lives

| Source | Signal Quality | Use For |
|--------|---------------|---------|
| **Specialist forums** (home-barista.com, head-fi.org, etc.) | Highest — experienced practitioners | Real-world usage, long-term experience, nuanced opinions |
| **Subreddit communities** (r/espresso, r/headphones, etc.) | High — collective experience, rapidly updated | Consensus picks, hidden gems, "what do you actually use" threads |
| **Enthusiast YouTube channels** (with testing methodology) | Medium-high — visual demonstrations | Comparisons with methodology, not just unboxing |
| **Manufacturer / official sites** | Medium — accurate specs but biased | Specs, pricing, availability, feature lists |
| **Expert/niche blogs** (individuals with domain credibility) | Medium — depends on the author | Deep reviews from people who test seriously |
| **SEO listicle sites** ("Best X 2025", affiliate blogs) | Low — optimized for revenue, not accuracy | Price aggregation only. Never trust their rankings. |
| **Amazon/retailer reviews** | Low-medium — volume helps but easily gamed | Failure modes and defects (negative reviews are more useful than positive) |

## Search Strategy

### Step 1: Identify Specialist Communities (BEFORE searching broadly)

For every consumer/enthusiast topic, there are 2-3 communities where the real experts congregate. Identify these FIRST.

**Common domain → community mappings:**

| Domain | Specialist Communities |
|--------|----------------------|
| Coffee/Espresso | home-barista.com, r/espresso, r/coffee, CoffeeGeek |
| Audio/Headphones | head-fi.org, r/headphones, r/audiophile, ASR (audiosciencereview.com) |
| Mechanical Keyboards | r/MechanicalKeyboards, geekhack.org, deskthority.net |
| Home Lab / Self-Hosting | r/homelab, r/selfhosted, ServeTheHome forums |
| Networking | r/homelab, r/networking, forums.servethehome.com |
| Cooking / Kitchen | r/Cooking, r/AskCulinary, Serious Eats, ChefSteps |
| Fitness / Training | r/fitness, r/weightroom, Stronger by Science |
| Photography | r/photography, fredmiranda.com, dpreview.com forums |
| PC Building | r/buildapc, r/sffpc, forums.overclock.net |
| Gaming (hardware) | r/monitors, rtings.com, TFTCentral |
| Cycling | r/cycling, r/bikewrench, weightweenies.starbike.com |
| Watches | r/Watches, watchuseek.com |
| Skincare | r/SkincareAddiction, r/AsianBeauty |
| Home improvement | r/HomeImprovement, r/HVAC, GardenWeb/Houzz forums |

If you don't know the specialist community for a domain, **search for it first**: `"[topic] forum" OR "[topic] community" OR "r/[topic]"`. Finding the right community is more valuable than 10 broad web searches.

### Step 2: Search Within Specialist Communities

**Use SearXNG (`mcp__searxng__searxng_web_search`) as your primary search tool for consumer research.** It aggregates 70+ search engines including Reddit as a direct source, returns cleaner results than WebSearch, and runs locally with no rate limits. SearXNG supports time range filtering and language filtering. Use `mcp__searxng__web_url_read` to retrieve full page content from URLs found in search results.

**When to use which search tool:**
- **SearXNG** — primary tool for all consumer research. Better at surfacing forum/community content.
- **WebSearch** — fallback if SearXNG is unavailable, or for quick single-fact lookups.
- **Playwright** — when you need to read the actual content of a specific thread/page that search found.

Use targeted searches within identified communities:

**Effective query patterns:**
- `site:reddit.com/r/espresso "daily driver" beans` — find what people actually use daily
- `site:home-barista.com "what do you use" espresso beans` — practical experience
- `"[topic] forum" underrated OR "hidden gem" OR "sleeper pick"` — find non-obvious recommendations
- `site:reddit.com/r/[subreddit] "[product]" review OR experience OR "months later"` — long-term real usage

**Thread types with highest signal:**
- "What's your daily driver?" — reveals what people actually use, not what's hyped
- "X months/years with [product]" — long-term experience reports
- "Unpopular opinion" / "Overrated/underrated" — contrarian views that challenge consensus
- "Alternatives to [popular product]" — lesser-known options
- "What I wish I knew before buying" — experience-based advice
- Stickied recommendation threads / buying guides — community-curated, maintained over time

**Thread types with lowest signal:**
- "Best X 2025?" — attracts drive-by answers and often links to SEO listicles
- Brand new accounts recommending specific products — possible astroturfing
- Threads with only 1-2 replies — not enough consensus signal

### Step 2b: Use Playwright When WebSearch/WebFetch Fail

WebSearch can't do `site:` filtering and WebFetch often can't parse forum content (returns CSS/HTML skeleton instead of posts). When you identify a specific forum thread or Reddit discussion worth reading, use **Playwright** to navigate to the page and extract the actual content.

**When to use Playwright:**
- Forum threads (home-barista.com, head-fi.org, etc.) that WebFetch can't parse
- Reddit threads where you need to read actual comments, not just titles
- Any JavaScript-rendered page that returns empty or broken content via WebFetch
- Paginated forum threads where you need to click through pages

**Pattern:**
1. `browser_navigate` to the URL
2. `browser_snapshot` to read page content
3. `browser_click` to expand comments, load more, or navigate pages if needed
4. `browser_snapshot` again after interaction

### Step 3: Fill Gaps with Broader Search

Only after specialist communities have been searched, use broad web search for:
- **Pricing and availability** — where to buy, current prices, deals
- **Specs and compatibility** — manufacturer details, dimensions, technical specifications
- **Local availability** — "where to buy [product] near [location]"
- **Niche blogs** — individual reviewers with demonstrated expertise

### Step 4: Recognize Reddit as a Network of Specialist Forums

Reddit is NOT one site. It's thousands of specialist communities. Search specific subreddits, not "reddit" broadly.

**Key Reddit search tactics:**
- Use `site:reddit.com/r/SPECIFIC_SUBREDDIT` rather than just `site:reddit.com`
- Check the subreddit's wiki/sidebar — often has curated recommendations
- Sort by top/all-time for consensus picks
- Look for user flair (indicates experience level in some communities)
- Cross-reference recommendations across 2-3 related subreddits

## Source Credibility (Consumer/Enthusiast)

Weight sources in this order:

1. **Forum veterans with post history** — years of experience, no financial incentive
2. **Subreddit consensus** (multiple users independently recommending) — crowd-filtered
3. **Independent reviewers with methodology** — testing, not just opinions
4. **Manufacturer specs** — accurate but incomplete picture
5. **Retailer reviews** (high volume, focus on negatives) — useful for failure modes
6. **SEO listicles / "Best X" articles** — treat as noise, not signal

**Key rule:** Community consensus from experienced users > any individual review > any listicle. A product that 50 forum regulars independently recommend is more trustworthy than one that 10 SEO articles rank #1.

## Consumer-Specific Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| **SEO trust** — top Google results must be authoritative | Top results are affiliate-optimized, not accuracy-optimized | Search specialist communities first, broad web last |
| **Popularity = quality** — the most recommended product must be best | Popular picks are often safe/mainstream, not best for specific needs | Ask: "best for MY use case" not "best overall" |
| **Review score averaging** — 4.5 stars means good | Review distributions matter more than averages. Bimodal = quality control issues. | Read 1-3 star reviews for failure modes |
| **Recency bias** — newest = best | Established products often outperform trendy ones | Look for "X years later" reviews and long-term reports |
| **Single-community bias** — one subreddit said it, must be true | Every community has its own biases and favorites | Cross-reference across 2-3 independent communities |

## Output Adaptations for Consumer Research

When presenting consumer/enthusiast findings:

- **Lead with the specific recommendation** for the user's stated use case, not a generic "top 10"
- **Explain WHY** something is recommended — what makes it good for their specific situation
- **Include price ranges** — budget context matters for consumer decisions
- **Note where to buy** — availability and convenience matter
- **Distinguish consensus picks from hidden gems** — label which is which
- **Include dissenting views** — if a popular pick has vocal critics, surface that
- **Cite specific community sources** — "recommended by multiple users on r/espresso" > "highly rated online"
