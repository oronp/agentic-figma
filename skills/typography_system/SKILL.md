---
name: Typography System Generator
description: Analyzes a Figma screen, extracts every text style, normalizes it, builds a complete typography system, and creates a structured documentation frame in Figma. Use this skill whenever the user mentions analyzing typography, extracting fonts or text styles, auditing a design system, building a type scale, documenting text styles, creating a style guide, or any task involving font analysis in Figma — even if they don't use the word "typography".
---

# Typography System Analysis & Generator

**YOUR MISSION**
Analyze a Figma screen, extract every text style, normalize it, and build a complete typography system. Then create a structured documentation frame in Figma using a single `execute_figma_code` call with the pre-built JS template.

## STEP 1: GET THE DATA

**Tools to use:**
- `get_selection` (if the user doesn't provide a Node ID)
- `scan_text_nodes` on the target node to find all text layers
- `get_nodes_info` on the found text nodes to extract detailed typography specs

**Extract for every text layer:** font family, size, weight, line-height, letter-spacing, and where it appears in the design.

**Output:** A raw inventory of every text style found — keep this as your working dataset.

---

## STEP 2: NORMALIZE

### Size Rounding
- Round to nearest whole number if within 0.5px (15.2 → 15px, 23.8 → 24px)
- Cluster close sizes that likely represent the same role (15px, 15.5px, 16px, 16.2px → 16px)
- Pick the most common value or the nearest standard size

### Line Height Conversion
Always convert to ratio: 24px on 16px font = 1.5 (150%)

Target ratios by category:
- Display: 110–115%
- Headline: 125–130%
- Title: 130–140%
- Body: 140–160%
- Label: 130–140%

### Weight Mapping
- 100–300 → Light
- 400 → Regular
- 500 → Medium
- 600 → Semibold
- 700 → Bold
- 800–900 → Black

### Letter Spacing Normalization
- Convert px values to em (divide by font size): 0.5px on 16px = 0.031em
- Cluster close values (0.10em, 0.12em → 0.10em)
- Flag very tight tracking (<−0.02em) as a potential readability concern
- Note intentionally loose tracking (>0.15em) — it typically signals labels or uppercase styles

### Multi-Family Handling
Identify each distinct font family and its role in the design:
- **Primary:** most commonly used (usually body/UI text)
- **Secondary:** used for display/headings or stylistic contrast
- **Tertiary/accent:** used sparingly (e.g., code font, pull quotes)

If the design uses multiple families, build a scale per family or note where families share size slots. Don't flatten everything into a single list — the family distinction is meaningful.

---

## STEP 3: MAP TO TYPE SCALE

Map every style to the closest slot in this hierarchy (Material Design / Google type scale):

**DISPLAY** — Large: 57px | Medium: 45px | Small: 36px
**HEADLINE** — H1: 32px | H2: 28px | H3: 24px
**TITLE** — Large: 22px | Medium: 16px | Small: 14px
**BODY** — Large: 16px | Medium: 14px | Small: 12px
**LABEL** — Large: 14px | Medium: 12px | Small: 11px

**Decision rules:**
- Non-standard size (e.g., 18px): is it closer to 16 or 20? Used enough to warrant its own slot?
- Sizes that don't fit cleanly: document as "Custom" and explain why they exist
- Record every mapping decision and your reasoning

---

## STEP 4: FILTER OUTLIERS

Do NOT include in the system:
- Sizes appearing only once with no clear pattern
- Obvious rounding drift (15.7px alongside 16px everywhere else)
- Placeholder or default-styled text
- Hidden or overlapping layers

---

## STEP 5: ANALYSIS OUTPUT

For each normalized style, produce this block and share it with the user before building the frame:

```text
STYLE: [category/variant]            ← e.g., headline/h1, body/medium
Font Family:    [name]
Size:           [px]
Line Height:    [px] ([ratio]%)
Weight:         [numeric] ([name])
Letter Spacing: [em] ([px equivalent])
Usage:          [where it appears, what content uses it]
Instances:      [count]
Example text:   "[actual text from the design]"
Decision notes: [normalization or mapping decisions]
```

After presenting all styles, summarize:
- Total unique styles in the system
- Font families and their roles
- Any accessibility warnings (see Step 6)
- Anything needing confirmation before building

**Wait for user confirmation before proceeding to Step 7.**

---

## STEP 6: SPECIAL CONSIDERATIONS

**RTL / Hebrew** *(only apply if the design contains RTL or Hebrew text)*
- Mark text direction as RTL
- Add 10–20% extra line height vs Latin equivalents
- Check whether fonts used actually support the Hebrew character set — if Latin-only fonts appear on Hebrew text, flag it as a potential rendering issue

**Accessibility**
- Body text minimum: 14px
- Body line height minimum: 140% (1.4)
- Avoid pure `#000000` for body text — suggest `#1A1A1A` or similar
- Flag any styles that fall below these thresholds

**Responsive Notes**
- Display and Headline styles typically reduce 20–30% on mobile
- Note which styles need responsive variants

---

## STEP 7: BUILD THE FIGMA FRAME VIA `execute_figma_code`

Do **not** use individual creation tools (`create_frame`, `create_text`, etc.).
Instead, fill the pre-built JS template and send a **single** `execute_figma_code` call.

### 7a — Prepare the data

Collect these values from Steps 1–6:

| Placeholder | Value | Example |
|---|---|---|
| `{{DOC_TITLE}}` | Frame title | `"Typography — Desktop"` |
| `{{PRIMARY_FONT}}` | Primary font family | `"Ploni ML v2 AAA"` |
| `{{SECONDARY_FONT}}` | Secondary / UI font family | `"Roboto"` |
| `{{WEIGHTS_JSON}}` | JS array of unique weights | see schema below |
| `{{STYLES_JSON}}` | JS array of normalized styles | see schema below |
| `{{SAMPLE_TEXT_HEADER}}` | Short 3–4 word phrase (from user) | `"Design System"` |
| `{{SAMPLE_TEXT_BODY}}` | Short paragraph (from user) | `"Body text goes here."` |

**`WEIGHTS_JSON` schema** — one entry per unique weight found in the design:
```json
[
  { "name": "Bold",    "style": "Bold" },
  { "name": "Regular", "style": "Regular" }
]
```
- `name` → column header label shown in the frame
- `style` → exact Figma font style string (must match what Figma accepts for that family)

**`STYLES_JSON` schema** — one entry per normalized style from Step 3:
```json
[
  {
    "variant":    "H1",
    "category":   "HEADLINE",
    "fontFamily": "Ploni ML v2 AAA",
    "fontStyle":  "Bold",
    "size":       32,
    "lineHeight": 40,
    "weightName": "Bold",
    "usage":      "Main page titles",
    "isBody":     false
  }
]
```
- `category` — one of: `DISPLAY`, `HEADLINE`, `TITLE`, `BODY`, `LABEL`
- `fontStyle` — must be the exact Figma style string for that family
- `weightName` — must match a `name` value in `WEIGHTS_JSON`
- `isBody` — `true` for BODY/LABEL rows (uses `SAMPLE_BODY`), `false` otherwise

### 7b — Fill the template

1. Read the file `skills/typography_system/template.js`
2. Replace every `{{PLACEHOLDER}}` with its real value:
   - String placeholders → replace the whole `"{{TOKEN}}"` (including quotes) with a quoted string literal
   - Array placeholders (`{{WEIGHTS_JSON}}`, `{{STYLES_JSON}}`) → replace the bare `{{TOKEN}}` (no surrounding quotes) with the raw JS array literal
3. **Do not modify any other part of the template.**

### 7c — Execute

Send the filled-in script via one tool call:
```
execute_figma_code(code = <filled-in template content>)
```

The tool returns `{ success, nodeId, message }`. Report the result to the user.

---

## EXECUTION ORDER SUMMARY

1. Get Node ID from user or via `get_selection`
2. `scan_text_nodes` → `get_nodes_info` to extract all raw data
3. Normalize sizes, line heights, weights, and letter spacing
4. Map to type scale; note custom slots
5. Filter outliers
6. Present the full analysis (Step 5) to the user and wait for confirmation
7. Ask the user for sample text:
   - One short sentence (3–4 words) for heading rows
   - One short paragraph for body rows
8. Read `skills/typography_system/template.js`, fill all `{{PLACEHOLDERS}}`, call `execute_figma_code`
