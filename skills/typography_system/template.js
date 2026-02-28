// ============================================================
// Typography System Generator — Figma Plugin Template
// Executed via execute_figma_code by the Typography Skill
//
// PLACEHOLDERS (all replaced before execution):
//   {{DOC_TITLE}}          — e.g. "Typography — Desktop"
//   {{PRIMARY_FONT}}       — primary font family string
//   {{SECONDARY_FONT}}     — secondary / UI font family string
//   {{WEIGHTS_JSON}}       — JS array literal:
//                            [{"name":"Bold","style":"Bold"}, ...]
//                            name  → column header label
//                            style → Figma font style string
//   {{STYLES_JSON}}        — JS array literal, one object per row:
//                            {
//                              variant:    "H1",
//                              category:   "HEADLINE",  // DISPLAY|HEADLINE|TITLE|BODY|LABEL
//                              fontFamily: "Ploni ML v2 AAA",
//                              fontStyle:  "Bold",       // must match Figma style name
//                              size:       32,
//                              lineHeight: 40,
//                              weightName: "Bold",       // must match a name in WEIGHTS
//                              usage:      "Page titles",
//                              isBody:     false
//                            }
//   {{SAMPLE_TEXT_HEADER}} — short 3-4 word phrase for heading rows
//   {{SAMPLE_TEXT_BODY}}   — short paragraph for body rows
// ============================================================

const DOC_TITLE     = "{{DOC_TITLE}}";
const PRIMARY_FONT  = "{{PRIMARY_FONT}}";
const SECONDARY_FONT= "{{SECONDARY_FONT}}";
const WEIGHTS       = {{WEIGHTS_JSON}};
const STYLES        = {{STYLES_JSON}};
const SAMPLE_HEADER = "{{SAMPLE_TEXT_HEADER}}";
const SAMPLE_BODY   = "{{SAMPLE_TEXT_BODY}}";

// ── Helpers ───────────────────────────────────────────────────

function hexRgb(h) {
  return {
    r: parseInt(h.slice(1,3), 16) / 255,
    g: parseInt(h.slice(3,5), 16) / 255,
    b: parseInt(h.slice(5,7), 16) / 255,
  };
}
const solid = h => [{ type: "SOLID", color: hexRgb(h) }];

function mkFrame(name) {
  const f = figma.createFrame();
  f.name = name;
  f.fills = [];
  f.clipsContent = false;
  return f;
}

function setV(f, { gap=0, pt=0, pb=0, pl=0, pr=0, main="MIN", cross="MIN" } = {}) {
  f.layoutMode            = "VERTICAL";
  f.primaryAxisSizingMode = "AUTO";
  f.counterAxisSizingMode = "AUTO";
  f.itemSpacing           = gap;
  f.paddingTop    = pt;  f.paddingBottom = pb;
  f.paddingLeft   = pl;  f.paddingRight  = pr;
  f.primaryAxisAlignItems = main;
  f.counterAxisAlignItems = cross;
}

function setH(f, { gap=0, pt=0, pb=0, pl=0, pr=0, main="MIN", cross="MIN" } = {}) {
  f.layoutMode            = "HORIZONTAL";
  f.primaryAxisSizingMode = "AUTO";
  f.counterAxisSizingMode = "AUTO";
  f.itemSpacing           = gap;
  f.paddingTop    = pt;  f.paddingBottom = pb;
  f.paddingLeft   = pl;  f.paddingRight  = pr;
  f.primaryAxisAlignItems = main;
  f.counterAxisAlignItems = cross;
}

// Creates a text node. Font must already be loaded.
function mkText(chars, { family, style="Regular", size=16, color="#000000", align="LEFT" } = {}) {
  const t = figma.createText();
  t.fontName             = { family, style };
  t.characters           = String(chars);
  t.fontSize             = size;
  t.fills                = solid(color);
  t.textAlignHorizontal  = align;
  return t;
}

function stroke(f, hex) {
  f.strokes      = solid(hex);
  f.strokeWeight = 1;
  f.strokeAlign  = "INSIDE";
}

// ── Pre-load every font we'll use ────────────────────────────

const fontKeys = new Set();
fontKeys.add(`${PRIMARY_FONT}||Regular`);
fontKeys.add(`${SECONDARY_FONT}||Regular`);
for (const w of WEIGHTS) fontKeys.add(`${PRIMARY_FONT}||${w.style}`);
for (const s of STYLES)  fontKeys.add(`${s.fontFamily}||${s.fontStyle}`);

for (const key of fontKeys) {
  const [family, style] = key.split("||");
  try { await figma.loadFontAsync({ family, style }); } catch(_) {}
}

// ── Root frame ───────────────────────────────────────────────

const ROOT_WIDTH = 1440;

const root = mkFrame("Typography System");
root.fills = solid("#FFFFFF");
setV(root, { pt:135, pb:135, pl:40, pr:40, gap:0 });
root.counterAxisSizingMode = "FIXED";
root.cornerRadius = 50;
root.resize(ROOT_WIDTH, 100); // height grows via auto-layout

// ── 1. Header ────────────────────────────────────────────────

const hdr = mkFrame("Header");
hdr.fills = solid("#EAECF2");
setV(hdr, { pt:80, pb:80, pl:80, pr:80, gap:16, cross:"CENTER" });
hdr.layoutSizingHorizontal = "FILL";

hdr.appendChild(mkText(DOC_TITLE,            { family:PRIMARY_FONT,   size:80, color:"#000000" }));
hdr.appendChild(mkText("See design guideline",{ family:SECONDARY_FONT, size:24, color:"#000000" }));

root.appendChild(hdr);

// ── 2. Font Overview ─────────────────────────────────────────

const overview = mkFrame("Font Overview");
setH(overview, { pt:40, pb:40, pl:40, pr:40, gap:40, cross:"CENTER" });
stroke(overview, "#CCCDD5");
overview.layoutSizingHorizontal = "FILL";

// Left — identity
const ovLeft = mkFrame("Identity");
setV(ovLeft, { gap:8, cross:"MAX" });
ovLeft.appendChild(mkText("Aא", { family:PRIMARY_FONT, size:56, align:"RIGHT" }));
ovLeft.appendChild(mkText(PRIMARY_FONT, { family:SECONDARY_FONT, size:22 }));

// Middle — weight samples
const ovMid = mkFrame("Weight Samples");
setH(ovMid, { gap:32, cross:"CENTER" });
for (const w of WEIGHTS) {
  const wf = mkFrame(w.name);
  setV(wf, { gap:8, cross:"CENTER" });
  wf.appendChild(mkText("Aא",  { family:PRIMARY_FONT, style:w.style, size:56 }));
  wf.appendChild(mkText(w.name,{ family:SECONDARY_FONT, size:22 }));
  ovMid.appendChild(wf);
}

// Right — character set
const ovRight = mkFrame("Char Set");
setV(ovRight, { gap:0 });
const charTxt = mkText(
  "אבגדהוזחטיכלמנסעפצקרשתףךן\n0123456789\n!@#$%^&*?)",
  { family:PRIMARY_FONT, size:56, color:"#02042B", align:"RIGHT" }
);
charTxt.lineHeight = { value:130, unit:"PERCENT" };
ovRight.appendChild(charTxt);

overview.appendChild(ovLeft);
overview.appendChild(ovMid);
overview.appendChild(ovRight);
root.appendChild(overview);

// ── 3. Column Header Row ─────────────────────────────────────

const colHdr = mkFrame("Column Headers");
setH(colHdr, { pt:16, pb:16, pl:32, pr:32, gap:0, main:"SPACE_BETWEEN", cross:"CENTER" });
stroke(colHdr, "#CCCDD5");
colHdr.layoutSizingHorizontal = "FILL";

for (const lbl of ["System/Specs", ...WEIGHTS.map(w => w.name), "Usage"]) {
  colHdr.appendChild(mkText(lbl, { family:SECONDARY_FONT, size:18, color:"#363636" }));
}
root.appendChild(colHdr);

// ── 4. Typography Rows ───────────────────────────────────────

for (const s of STYLES) {
  const row = mkFrame(s.variant);
  setH(row, { pt:32, pb:32, pl:32, pr:32, gap:40, main:"SPACE_BETWEEN", cross:"CENTER" });
  stroke(row, "#CCCDD5");
  row.layoutSizingHorizontal = "FILL";

  // Left — specs column
  const specs = mkFrame("Specs");
  setV(specs, { gap:12 });

  const catTag = mkFrame("Category Tag");
  setH(catTag, { pt:6, pb:6, pl:12, pr:12 });
  catTag.fills        = solid("#FFF7F3");
  catTag.cornerRadius = 12;
  catTag.appendChild(mkText(s.variant, { family:SECONDARY_FONT, size:24, color:"#363636" }));
  specs.appendChild(catTag);

  const chip = mkFrame("Size Chip");
  setH(chip, { pt:4, pb:4, pl:8, pr:8, gap:8, cross:"CENTER" });
  chip.fills        = solid("#F9F9F9");
  chip.cornerRadius = 5;
  chip.appendChild(mkText("Aa",              { family:SECONDARY_FONT, size:12, color:"#7281A7" }));
  chip.appendChild(mkText(`${s.size}px`,     { family:SECONDARY_FONT, size:20, color:"#363636" }));
  chip.appendChild(mkText(`${s.lineHeight}px`,{ family:SECONDARY_FONT, size:20, color:"#363636" }));
  specs.appendChild(chip);

  row.appendChild(specs);

  // Middle — one column per weight
  for (const w of WEIGHTS) {
    const midCol = mkFrame(`${s.variant} · ${w.name}`);
    setV(midCol, { gap:0, cross:"CENTER", main:"CENTER" });

    if (s.weightName === w.name) {
      const sample = s.isBody ? SAMPLE_BODY : SAMPLE_HEADER;
      midCol.appendChild(mkText(sample, {
        family: s.fontFamily,
        style:  s.fontStyle,
        size:   s.size,
        color:  "#02042B",
      }));
    }
    row.appendChild(midCol);
  }

  // Right — usage
  row.appendChild(mkText(s.usage, { family:SECONDARY_FONT, size:20, color:"#363636" }));

  root.appendChild(row);
}

// ── Place on canvas ──────────────────────────────────────────

figma.currentPage.appendChild(root);
root.x = 0;
root.y = 0;
figma.viewport.scrollAndZoomIntoView([root]);

return {
  success: true,
  nodeId:  root.id,
  message: `Typography system built — ${STYLES.length} styles across ${WEIGHTS.length} weights`,
};
