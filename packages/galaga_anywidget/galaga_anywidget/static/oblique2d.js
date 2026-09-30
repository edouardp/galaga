function render({ model, el }) {
  const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
  const root = document.createElement("div");
  root.className = "galaga-oblique2d";
  el.replaceChildren(root);
  const redraw = () => {
    const { width, height, extent } = model.get("view");
    const scale = Math.min(width, height) / (2 * extent);
    const cx = width / 2, cy = height / 2;
    const xy = (x, y) => [cx + x * scale, cy - y * scale];
    const line = (x1, y1, x2, y2, color, cls = "") => {
      const a = xy(x1, y1), b = xy(x2, y2);
      return `<line class="${cls}" x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="${color}" marker-end="url(#arrow)"/>`;
    };
    const body = model.get("scene").map((item) => {
      if (item.kind === "basis" || item.kind === "vector") {
        const [x, y] = xy(item.x, item.y);
        return `${line(0, 0, item.x, item.y, item.color, item.kind)}<text x="${x + 7}" y="${y - 7}">${escapeHTML(item.label)}</text>`;
      }
      const pts = [[0, 0], [item.x1, item.y1], [item.x1 + item.x2, item.y1 + item.y2], [item.x2, item.y2]].map((p) => xy(...p));
      const points = pts.map((p) => p.join(",")).join(" ");
      const [x, y] = pts[2];
      return `<polygon class="bivector" points="${points}" fill="${item.color}"/><text x="${x + 6}" y="${y - 6}">${escapeHTML(item.label)}</text><text class="area" x="8" y="${height - 12}">oriented area = ${item.area.toFixed(3)}</text>`;
    }).join("");
    root.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Oblique metric vector and bivector geometry"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="context-stroke"/></marker></defs><line class="axis" x1="0" y1="${cy}" x2="${width}" y2="${cy}"/><line class="axis" x1="${cx}" y1="0" x2="${cx}" y2="${height}"/>${body}</svg>`;
  };
  model.on("change:scene", redraw);
  model.on("change:view", redraw);
  redraw();
  return () => { model.off("change:scene", redraw); model.off("change:view", redraw); };
}

export default { render };
