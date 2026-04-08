# Data Structures & Language Comparisons — Design Spec

**Date:** 2026-04-06
**Purpose:** Two new content sections for the FinBytes site — data structures (build from scratch in 7 languages) under the Design tab, and language/library comparisons as a new sidebar tab.
**Audience:** Personal learning reference. Python is the anchor language; Rust, Go, TypeScript, C++, C# are "learning by comparison."

---

## Section 1: Data Structures (under Design & Reliability tab)

### Location
New block on the Design & Reliability tab (`docs/_tabs/design.md`), after the Queues & Reliability section.

### Format
Same as existing Design Pattern posts:
- Layout: `cpp-post` (8 tabs: Concept / Python / C# / C++ / Rust / Go / TypeScript / Compare)
- Collection: `_cpp` (stored in `docs/_cpp/series/K_Data structures/`)
- Each post: ~300-400 lines
- Implementation-focused: build each data structure from scratch in every language
- Compare tab: complexity table, stdlib equivalents, "when to use stdlib vs build your own"

### Posts (6 total)

#### 1. Dynamic Array
- **File:** `docs/_cpp/series/K_Data structures/2026-07-10-dynamic-array.html`
- **Permalink:** `/cpp/dynamic-array/`
- **Concept tab:** Contiguous memory, amortized O(1) append via doubling, capacity vs length
- **Each language:** Implement a growable array: init, push, get, resize
- **Compare:** Python list (over-allocates by ~12%), C++ vector (growth factor ~2x), Rust Vec (ownership transfer on push), Go slice (append may relocate, old slice is stale), TS array (dynamic by default, no manual management)
- **Key insight:** Who owns the memory when the array grows?

#### 2. Hash Map
- **File:** `docs/_cpp/series/K_Data structures/2026-07-17-hash-map.html`
- **Permalink:** `/cpp/hash-map-impl/`
- **Concept tab:** Hash function, buckets, collision resolution (chaining vs open addressing), load factor, rehashing
- **Each language:** Implement a hash map with chaining: put, get, delete, resize
- **Compare:** Python dict (insertion-ordered since 3.7, compact layout), Go map (random iteration order, not goroutine-safe), Rust HashMap (no order, requires Hash+Eq traits), C++ unordered_map (bucket interface exposed)
- **Key insight:** Iteration order guarantees vary wildly across languages

#### 3. Linked List
- **File:** `docs/_cpp/series/K_Data structures/2026-07-24-linked-list.html`
- **Permalink:** `/cpp/linked-list-impl/`
- **Concept tab:** Singly vs doubly linked, O(1) insert/remove at known position, O(n) search, no random access
- **Each language:** Implement singly-linked list: push_front, pop_front, find, insert_after
- **Compare:** Rust (notoriously hard — ownership model fights cyclic references, need Option<Box<Node>>), Go/Python (trivial with GC), C++ (raw pointers or unique_ptr), TS (straightforward class-based)
- **Key insight:** Why Rust makes linked lists hard — and what that teaches about ownership

#### 4. Binary Search Tree
- **File:** `docs/_cpp/series/K_Data structures/2026-07-31-binary-search-tree.html`
- **Permalink:** `/cpp/bst-impl/`
- **Concept tab:** BST property, insert, search, in-order traversal, delete (3 cases), unbalanced worst case O(n)
- **Each language:** Implement BST: insert, search, in_order traversal
- **Compare:** Recursive vs iterative styles per language, how each handles nullable/optional child nodes (Python None, Rust Option<Box<Node>>, Go *Node nil, C++ unique_ptr, TS | null)
- **Key insight:** Null/optional handling is where languages diverge most in tree code

#### 5. Priority Queue / Heap
- **File:** `docs/_cpp/series/K_Data structures/2026-08-07-priority-queue-heap.html`
- **Permalink:** `/cpp/heap-impl/`
- **Concept tab:** Complete binary tree stored as array, min-heap property, sift-up (insert), sift-down (extract-min), O(log n) both
- **Each language:** Implement min-heap: push, pop, peek, heapify
- **Compare:** Python heapq (module-level functions, not a class — quirky), C++ priority_queue (max-heap by default, need greater<> for min), Rust BinaryHeap (max-heap, no built-in min), Go heap.Interface (you implement the interface, library does the rest)
- **Key insight:** Stdlib heap APIs are surprisingly inconsistent across languages

#### 6. Stack & Queue
- **File:** `docs/_cpp/series/K_Data structures/2026-08-14-stack-and-queue.html`
- **Permalink:** `/cpp/stack-queue-impl/`
- **Concept tab:** LIFO vs FIFO, array-backed vs linked, when stdlib is enough
- **Each language:** Implement both from an array: push/pop (stack), enqueue/dequeue (queue with circular buffer)
- **Compare:** Python list-as-stack (fine) vs list-as-queue (O(n) popleft — use deque), Go slice-as-stack (fine) vs channel-as-queue (concurrent by design), Rust VecDeque
- **Key insight:** When the stdlib is enough vs when you build your own (tease lock-free queue from Queues & Reliability)

### Design tab update
Add a new `<div class="cpp-section">` block to `docs/_tabs/design.md`:
```
Data structures — 6 posts, date range filter for the K series
```

---

## Section 2: Language Comparisons (new sidebar tab)

### Location
New sidebar tab in `docs/_tabs/comparisons.md`:
- Title: "Comparisons"
- Icon: `fas fa-exchange-alt`
- Order: 4 (between Design & Reliability and Math / Finance)
- Permalink: `/comparisons/`

### Format
- Layout: `post` (standard blog post, NOT cpp-post — these aren't multi-tab)
- Stored in: `docs/_posts/` (regular posts with `section: comparisons` front matter)
- Each post: ~300-350 lines
- Structure per post: brief intro → same task in each language/library → comparison table → "when to use what" decision guide
- Code-heavy: the whole point is seeing the same operation in different syntaxes

### Posts (4 total)

#### 1. pandas vs polars
- **File:** `docs/_posts/2026-07-08-pandas-vs-polars.html`
- **Permalink:** `/comparisons/pandas-vs-polars/`
- **Operations compared:** Load CSV, filter rows, group-by aggregation, join two DataFrames, sort, add computed column
- **Sections:** API style (method chaining vs expression-based), lazy evaluation (polars only), memory usage, speed benchmark on a realistic dataset (~1M rows), error messages quality
- **Decision guide:** When to stay on pandas (ecosystem, existing code, small data), when to switch to polars (speed, memory, lazy eval, Rust-backed)

#### 2. Concurrency Models
- **File:** `docs/_posts/2026-07-09-concurrency-models.html`
- **Permalink:** `/comparisons/concurrency-models/`
- **Task:** Fetch 50 URLs concurrently, collect results
- **Languages:** Python (asyncio, threading, multiprocessing), Go (goroutines + WaitGroup), Rust (tokio), TypeScript (Promise.all), C++ (std::thread + std::async), C# (Task.WhenAll)
- **Sections:** The GIL explained (Python only), I/O-bound vs CPU-bound (which model wins where), code for each, timing comparison
- **Decision guide:** I/O-bound → async. CPU-bound → multiprocessing/goroutines/tokio. Mixed → Go or Rust.

#### 3. Type Systems & Validation
- **File:** `docs/_posts/2026-07-12-type-systems-validation.html`
- **Permalink:** `/comparisons/type-systems-validation/`
- **Task:** Validate a trading request (ticker: string uppercase, quantity: positive int, side: buy/sell, price: optional positive float)
- **Libraries:** Python Pydantic, TypeScript Zod, Rust serde + validator, Go struct tags + validator, C# DataAnnotations, C++ (manual — no standard equivalent)
- **Sections:** What the compiler catches at build time vs what needs runtime validation, error message quality, serialization/deserialization, schema generation
- **Decision guide:** Table of compile-time vs runtime guarantees per language

#### 4. HTTP Clients
- **File:** `docs/_posts/2026-07-13-http-clients.html`
- **Permalink:** `/comparisons/http-clients/`
- **Task:** GET a JSON API, POST with body, handle errors, set timeout
- **Libraries:** Python requests/httpx/aiohttp, Go net/http, Rust reqwest, TS fetch/axios, C# HttpClient, C++ cpp-httplib
- **Sections:** Sync vs async, connection pooling, error handling patterns, timeout configuration, testing/mocking
- **Decision guide:** When sync is fine (scripts, CLI), when async matters (APIs, high concurrency), which library per language

### Comparisons tab index page
Simple list with descriptions, same style as Math / Finance index:
```
pandas vs polars — lazy eval, memory, speed
Concurrency Models — asyncio vs goroutines vs tokio vs threads
Type Systems & Validation — Pydantic vs Zod vs serde
HTTP Clients — requests vs reqwest vs fetch vs net/http
```

---

## Files to create/modify

### New files:
- `docs/_cpp/series/K_Data structures/` — 6 post files
- `docs/_tabs/comparisons.md` — new sidebar tab
- `docs/_posts/` — 4 comparison post files

### Modified files:
- `docs/_tabs/design.md` — add Data Structures section block
- `docs/_config.yml` — no changes needed (K series picked up automatically by cpp collection)

### Total: 10 new posts + 1 new tab + 1 modified tab = 12 files

---

## Out of scope
- No code execution or benchmarks (numbers are illustrative/referenced, not measured)
- No video/interactive content
- The 20 early C++ posts (intro + series A-G) stay hidden at /cpp/ — not touched
- No changes to existing Design Pattern / Defensive / Queues posts
