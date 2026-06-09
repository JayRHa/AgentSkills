# Story Splitting Patterns

When a story is too big to fit in a sprint, split it into **thin vertical slices** — each
delivering end-to-end value — using one of these patterns (SPIDR + classics).

| Pattern | Split by | Example |
| --- | --- | --- |
| **Workflow steps** | Stages of a process | "Checkout" → enter address → choose shipping → pay → confirm |
| **Business rules** | Each rule separately | Discounts: first do flat %, later add tiered, later add coupons |
| **Happy / unhappy path** | Success first, errors later | "Pay" → successful payment, then declined-card handling |
| **Data variations** | Input types | Import CSV first, then XLSX, then JSON |
| **Operations (CRUD)** | Create/Read/Update/Delete | Ship "view profile" before "edit profile" |
| **Interface variations** | Channel/device | Web form first, then mobile, then API |
| **Effort / quality** | Crude then refined | Manual export button before scheduled auto-export |
| **Spike** | Separate the unknown | Time-boxed research story to de-risk, then the build story |

## Rules for good splits

1. **Vertical, not horizontal** — every slice touches UI→logic→data and is demoable. Never split into "build the backend" + "build the frontend".
2. **Each slice is independently valuable** or at least independently shippable behind a flag.
3. **Roughly equal size** — avoid one giant + several trivial slices.
4. **Preserve the "why"** — the benefit should survive in each slice.

## Smell test

If a proposed slice can't be demoed to a user on its own, it's probably a horizontal layer — re-split.
