---
name: Typography System Generator
description: Analyzes a Figma screen, extracts every text style, normalizes it, builds a complete typography system, and creates a structured documentation frame in Figma. Use this skill whenever the user mentions analyzing typography, extracting fonts or text styles, auditing a design system, building a type scale, documenting text styles, creating a style guide, or any task involving font analysis in Figma — even if they don't use the word "typography".
---

# Typography System Analysis & Generator

**YOUR MISSION**
Analyze a Figma screen, extract every text style, normalize it, and build a complete typography system. Then create a structured documentation frame in Figma using TalkToFigma MCP tools.

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

## STEP 7: BUILD THE FIGMA FRAME

Use TalkToFigma MCP tools (`create_frame`, `set_layout_mode`, `create_text`, `set_fill_color`, `set_corner_radius`, etc.) to build the documentation frame.

**Adapt to the design you analyzed.** Use the primary font family and colors discovered in Steps 1–3 — not hardcoded values. The structure below is a strict template based on standard styling systems:

### Frame Setup
- Fill: `#FFFFFF` 
- Layout: Vertical auto-layout
- Padding: `135px` top/bottom, `40px` left/right
- Corner radius: `50`

### Header Section
- Fill: `#EAECF2` 
- Layout: Vertical auto-layout, centered alignment, vertical padding `80px`
- Title: "Typography- Desktop" (or adapted dynamic title)
  - Font: Primary font (e.g., `Ploni ML v2 AAA`)
  - Style: Regular
  - Size: `80`
  - Color: `#000000`
- Subtitle: "See design guideline"
  - Font: Secondary font (e.g., `Roboto`)
  - Style: Regular
  - Size: `24`
  - Color: `#000000`

### Font Overview Section
Immediately below the Header, create a horizontal spec frame for the primary font.
- **Outer Frame:** Horizontal auto-layout, Border Stroke `#CCCDD5`, Padding `40px`.
- **Left Column (Font Info):**
  - Show "Aא" at Size `56`, Right-aligned, Color `#000000`.
  - Show the Font Family name at Size `22` below it.
- **Middle Column (Weights):**
  - Create a horizontal frame containing samples for each weight found in the design.
  - Each sample: A vertical frame showing "Aא" at Size `56` and the weight name (e.g., "Bold") below it at Size `22`.
- **Right Column (Character Set):**
  - Text: Full Hebrew alphabet (`אבגדהוזחטיכלמנסעפצקרשתףךן`), numbers, and symbols (`0123456789!@#$%^&*?)`) 
  - Size: `56`, Aligned Right, Line Spacing `9px`, Color `#02042B`.

### Column Headers Row
- Create a header row for the table with a bottom stroke `#CCCDD5`.
- **Dynamic Columns:** 
  - First column: "System/Specs"
  - Middle columns: Create a separate column header for *every unique font weight* found in the design (e.g., "Bold", "DemiBold", "Regular").
  - Last column: "Usage"
- Layout: Horizontal auto-layout, space evenly

### Typography Rows (one per normalized style)
Each row represents a specific style (e.g., H1, Body | L):
- **Row Styling:** Horizontal auto-layout, Fill Container, Padding `32px`, Border Stroke `#CCCDD5`

**Left Column — Specs:**
- Layout: Vertical auto-layout
- Category tag: Frame with background `#FFF7F3`, Corner radius `12`
  - Text: The Style Category (e.g., "H1", "Body | L") at Size `24`, Color `#363636`
- Spec details: Horizontal row indicating size and line height
  - Background: `#F9F9F9`, Corner radius `5` 
  - Text inside chip: `Aa` (Size `12`, Color `#7281A7`)
  - Text next to chip: `[Size]px` (Size `20`, Color `#363636`) and `[LineHeight]px` (Size `20`, Color `#363636`)

**Middle Columns — Examples per Weight:**
- **Dynamic Columns:** Instead of one single "examples" column, create a separate column for *each weight* defined in the header row.
- Content: Drop the sample text (provided by the user in Step 7) into the correct weight column.
- Color: `#02042B` or `#363636` (match the source design exactly).
- If a specific style doesn't use a certain weight, leave that column space empty to maintain alignment.

**Right Column — Usage:**
- Layout: Standard text block
- Content: Explain the explicit purpose of the text.
- Styling: Size `20`, Centered vertically, Color `#363636`

### Strict Tool Constraints
You MUST use TalkToFigma tools correctly to enforce ALL layout structures exactly as specified above. 
- Use exact hex codes. Never guess colors.
- Use explicit `set_layout_mode` to ensure grid alignments. No random node positioning.

### Generation Order
For every normalized style from Step 3:
1. Create a row frame
2. Populate left column with specs
3. Populate the middle weight columns with the appropriate sample text
4. Populate right column with the usage purpose
5. Append row to the main typography frame

---

## EXECUTION ORDER SUMMARY

1. Get Node ID from user or via `get_selection`
2. `scan_text_nodes` → `get_nodes_info` to extract all raw data
3. Normalize sizes, line heights, weights, and letter spacing
4. Map to type scale; note custom slots
5. Filter outliers
6. Present the full analysis (Step 5) to the user and wait for confirmation
7. Ask the user for sample text to use in the design:
   - One short sentence (3-4 words) for Headers
   - One short paragraph for Body text
8. Build the Figma documentation frame
