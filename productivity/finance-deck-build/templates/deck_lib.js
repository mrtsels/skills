// deck_lib.js — starter theme + helpers for research-backed finance decks.
// Copy into the task folder, adjust palette, then write build_deck.js against
// these helpers. User defaults: Anthropic Sans/Serif, card layouts, navy/amber.
// pptxgenjs REQUIRED shape: every text-array item is {text, options} — flat
// objects collapse the array into ONE run-on paragraph (no error, no warning).
// Colors are hex WITHOUT '#'. LAYOUT_WIDE = 13.333 x 7.5in.
// Layout math: chips at (start, step, n, h) must end <= 7.1 (start + (n-1)*step + h).

const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_WIDE";

const C = {
  navy: "0B2545", navy2: "16324F", steel: "334E68", amber: "E8A33D",
  light: "F7FAFC", ink: "243B53", muted: "627D98", faint: "A8BCD0",
  card: "FFFFFF", border: "DCE3EC", rowalt: "F0F4F9", white: "FFFFFF",
};
const F = { body: "Anthropic Sans", head: "Anthropic Serif" }; // user default; mono uses F.body too
const M = 0.55, W = 13.333, H = 7.5;

function tag(slide, text) {
  slide.addText(text.toUpperCase(), { x: M, y: 0.32, w: 8, h: 0.3, fontSize: 11, color: C.amber, bold: true, charSpacing: 2, fontFace: F.body });
}
function title(slide, text, y = 0.62, size = 29) {
  slide.addText(text, { x: M, y, w: W - 2 * M, h: 0.75, fontSize: size, color: C.navy, bold: true, fontFace: F.head });
}
function footer(slide, n) {
  slide.addText(`Deck · ${new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" })}`, { x: M, y: H - 0.38, w: 6, h: 0.25, fontSize: 8, color: C.muted, fontFace: F.body });
  slide.addText(`${n}`, { x: W - M - 0.5, y: H - 0.38, w: 0.5, h: 0.25, fontSize: 9, color: C.muted, align: "right", fontFace: F.body });
}
// items: strings or {t, bold?, size?, color?, mono?}; gap = paraSpaceAfter
function bullets(slide, items, x, y, w, size = 13.5, gap = 8) {
  const arr = items.map((it) => {
    const o = { bullet: { code: "25AA", color: C.amber, indent: 12 }, fontSize: size, color: C.ink, fontFace: F.body, breakLine: true, paraSpaceAfter: gap };
    if (typeof it === "string") o.text = it;
    else { o.text = it.t; if (it.bold) o.bold = true; if (it.size) o.fontSize = it.size; if (it.color) o.color = it.color; if (it.mono) { o.fontFace = F.body; o.color = C.steel; } }
    return { text: o.text, options: o }; // REQUIRED shape — see top comment
  });
  slide.addText(arr, { x, y, w, h: 0.4 * items.length, valign: "top", align: "left" });
}
// KPI card: label (caps, amber), big value, optional sub. Dark variant for dark slides.
// PITFALL: keep start + (n-1)*step + h <= 7.1 or cards run off the slide bottom.
function chip(slide, x, y, w, h, label, value, sub, dark = false) {
  slide.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.09, fill: { color: dark ? C.navy2 : C.card }, line: { color: dark ? C.navy2 : C.border, width: 1 } });
  slide.addText(label.toUpperCase(), { x: x + 0.22, y: y + 0.16, w: w - 0.44, h: 0.26, fontSize: 9.5, color: C.amber, bold: true, charSpacing: 1, fontFace: F.body });
  slide.addText(value, { x: x + 0.22, y: y + 0.42, w: w - 0.44, h: 0.62, fontSize: 30, color: dark ? C.white : C.navy, bold: true, fontFace: F.head, valign: "middle" });
  if (sub) slide.addText(sub, { x: x + 0.22, y: y + h - 0.5, w: w - 0.44, h: 0.36, fontSize: 9, color: dark ? C.faint : C.muted, fontFace: F.body });
}
// Content card — the ANTI-TEXT-WALL default (user preference). Amber kicker +
// bold title + <=2 short lines (10-11pt). Use 2x2 grids (w~5.97 h~2.45) for
// concept pages, 4 stacked cards (w~8.0 h~1.28) beside a side panel for outlook.
function card(slide, x, y, w, h, kicker, t, lines, opts = {}) {
  slide.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.07, fill: { color: opts.fill || C.card }, line: { color: opts.line || C.border, width: 1 } });
  const pad = 0.22;
  let ty = y + 0.16;
  if (kicker) { slide.addText(kicker.toUpperCase(), { x: x + pad, y: ty, w: w - 2 * pad, h: 0.24, fontSize: 9, color: C.amber, bold: true, charSpacing: 1, fontFace: F.body }); ty += 0.28; }
  if (t) { slide.addText(t, { x: x + pad, y: ty, w: w - 2 * pad, h: 0.34, fontSize: 13.5, color: C.navy, bold: true, fontFace: F.body }); ty += 0.38; }
  const arr = lines.map((l) => {
    const o = { fontSize: opts.size || 11, color: C.ink, fontFace: F.body, breakLine: true, paraSpaceAfter: 3 };
    if (!opts.noBullet) o.bullet = { code: "25AA", color: C.amber, indent: 10 };
    o.text = (typeof l === "string" ? l : l.t);
    return { text: o.text, options: o };
  });
  slide.addText(arr, { x: x + pad + (opts.noBullet ? 0 : 0.08), y: ty, w: w - 2 * pad - (opts.noBullet ? 0 : 0.2), h: h - (ty - y) - 0.12, valign: "top" });
}
// PITFALL: every row must have exactly colW.length cells (short rows render blank cells silently).
function table(slide, rows, x, y, w, colW, fontSize = 11.5, headerFill = C.navy) {
  const body = rows.map((r, ri) => r.map((cell, ci) => {
    const first = ri === 0;
    const o = { fill: { color: first ? headerFill : (ri % 2 ? C.rowalt : C.card) }, color: first ? C.white : C.ink, fontSize: first ? fontSize : fontSize - 0.5, bold: first, fontFace: F.body, align: ci === 0 ? "left" : "center", valign: "middle", margin: [0.06, 0.1, 0.06, 0.1] };
    if (typeof cell === "object") { o.text = cell.t; if (cell.bold) o.bold = true; if (cell.color) o.color = cell.color; if (cell.align) o.align = cell.align; }
    else o.text = String(cell);
    return o;
  }));
  slide.addTable(body, { x, y, w, colW, rowH: 0.34, border: { type: "solid", color: C.border, pt: 0.5 }, fontFace: F.body, autoPage: false, valign: "middle" });
}
function divider(num, t, sub) {
  const s = p.addSlide();
  s.background = { color: C.navy };
  s.addText(num, { x: M, y: 1.1, w: 3, h: 2.2, fontSize: 150, color: "17395C", bold: true, fontFace: F.head });
  s.addText(t, { x: M + 0.12, y: 3.4, w: W - 2 * M, h: 1.0, fontSize: 40, color: C.white, bold: true, fontFace: F.head });
  if (sub) s.addText(sub, { x: M + 0.12, y: 4.5, w: W - 2 * M, h: 0.7, fontSize: 14, color: C.faint, fontFace: F.body });
  footer(s, "");
  return s;
}
// img: PNG path (embed PNG, keep SVG as source); h computed from known pixel ratio.
// sourceText renders ON THE SLIDE under the chart (user preference: never inside the chart).
function chartSlide(t, tagTxt, img, bulletsRight, n, imgW = 6.9, imgX = M, sourceText = "") {
  const s = p.addSlide();
  s.background = { color: C.light };
  tag(s, tagTxt);
  title(s, t);
  s.addImage({ path: img, x: imgX, y: 1.55, w: imgW, h: imgW * 0.556 });
  if (sourceText) s.addText("Source: " + sourceText, { x: imgX, y: 1.55 + imgW * 0.556 + 0.03, w: imgW, h: 0.22, fontSize: 8, color: C.muted, fontFace: F.body });
  if (bulletsRight) bullets(s, bulletsRight, imgX + imgW + 0.35, 1.7, W - 2 * M - imgW - 0.35);
  footer(s, n);
  return s;
}

// Research data pattern: one object holding every number that comes from live
// research; rd() guards let the deck build BEFORE research lands (placeholders
// show), then filling R is a single edit. Never hardcode researched numbers in
// slide code — route them through R so the provenance stays visible.
const R = {};
const rd = (v, fb = "—") => (v === null || v === undefined || v === "") ? fb : v;

module.exports = { p, C, F, M, W, H, tag, title, footer, bullets, chip, card, table, divider, chartSlide, R, rd };
