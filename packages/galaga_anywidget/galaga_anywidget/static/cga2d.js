const SVG_NS = "http://www.w3.org/2000/svg";
// Keep Python-derived geometry visually responsive without sending every
// pointer event through Marimo's reactive graph.
const POINT_SYNC_INTERVAL_MS = 33;
const POINT_EQUALITY_TOLERANCE = 1e-12;

function samePointCoordinates(coordinates, x, y) {
  return (
    Array.isArray(coordinates) &&
    coordinates.length === 2 &&
    Math.abs(coordinates[0] - x) <= POINT_EQUALITY_TOLERANCE &&
    Math.abs(coordinates[1] - y) <= POINT_EQUALITY_TOLERANCE
  );
}

function svgElement(name, attributes = {}) {
  const node = document.createElementNS(SVG_NS, name);
  for (const [key, value] of Object.entries(attributes)) {
    node.setAttribute(key, String(value));
  }
  return node;
}

function geometry(view) {
  const width = Number(view.width ?? 640);
  const height = Number(view.height ?? 420);
  const [xmin, xmax] = view.xlim ?? [-4, 4];
  const [ymin, ymax] = view.ylim ?? [-3, 3];
  const scale = Math.min(width / (xmax - xmin), height / (ymax - ymin));
  const xmid = (xmin + xmax) / 2;
  const ymid = (ymin + ymax) / 2;
  const visible = {
    xmin: xmid - width / (2 * scale),
    xmax: xmid + width / (2 * scale),
    ymin: ymid - height / (2 * scale),
    ymax: ymid + height / (2 * scale),
  };
  return {
    width,
    height,
    scale,
    visible,
    x: (value) => width / 2 + (value - xmid) * scale,
    y: (value) => height / 2 - (value - ymid) * scale,
    inverseX: (value) => xmid + (value - width / 2) / scale,
    inverseY: (value) => ymid - (value - height / 2) / scale,
  };
}

function lineEndpoints(item, visible) {
  const { a, b, c } = item;
  const epsilon = 1e-12;
  const candidates = [];
  const add = (x, y) => {
    if (
      Number.isFinite(x) &&
      Number.isFinite(y) &&
      x >= visible.xmin - epsilon &&
      x <= visible.xmax + epsilon &&
      y >= visible.ymin - epsilon &&
      y <= visible.ymax + epsilon &&
      !candidates.some(([px, py]) => Math.hypot(px - x, py - y) < epsilon)
    ) {
      candidates.push([x, y]);
    }
  };
  if (Math.abs(b) > epsilon) {
    add(visible.xmin, (-a * visible.xmin - c) / b);
    add(visible.xmax, (-a * visible.xmax - c) / b);
  }
  if (Math.abs(a) > epsilon) {
    add((-b * visible.ymin - c) / a, visible.ymin);
    add((-b * visible.ymax - c) / a, visible.ymax);
  }
  return candidates.slice(0, 2);
}

function drawGrid(svg, transform, enabled) {
  if (!enabled) return;
  const { visible } = transform;
  const group = svgElement("g", { class: "galaga-cga2d-grid" });
  const xStart = Math.ceil(visible.xmin);
  const xEnd = Math.floor(visible.xmax);
  const yStart = Math.ceil(visible.ymin);
  const yEnd = Math.floor(visible.ymax);
  if (xEnd - xStart <= 100) {
    for (let x = xStart; x <= xEnd; x += 1) {
      group.appendChild(
        svgElement("line", {
          x1: transform.x(x),
          y1: 0,
          x2: transform.x(x),
          y2: transform.height,
        }),
      );
    }
  }
  if (yEnd - yStart <= 100) {
    for (let y = yStart; y <= yEnd; y += 1) {
      group.appendChild(
        svgElement("line", {
          x1: 0,
          y1: transform.y(y),
          x2: transform.width,
          y2: transform.y(y),
        }),
      );
    }
  }
  svg.appendChild(group);
}

function drawAxes(svg, transform) {
  const { visible } = transform;
  const group = svgElement("g", { class: "galaga-cga2d-axes" });
  if (visible.ymin <= 0 && visible.ymax >= 0) {
    group.appendChild(
      svgElement("line", {
        x1: 0,
        y1: transform.y(0),
        x2: transform.width,
        y2: transform.y(0),
      }),
    );
  }
  if (visible.xmin <= 0 && visible.xmax >= 0) {
    group.appendChild(
      svgElement("line", {
        x1: transform.x(0),
        y1: 0,
        x2: transform.x(0),
        y2: transform.height,
      }),
    );
  }
  svg.appendChild(group);
}

function label(svg, item, x, y) {
  if (!item.label) return null;
  const text = svgElement("text", {
    x: x + 8,
    y: y - 8,
    class: "galaga-cga2d-label",
    fill: item.color,
  });
  text.textContent = item.label;
  svg.appendChild(text);
  return text;
}

function updateDipoleGeometry(rendered, item, transform) {
  const finite = item.finite !== false;
  rendered.node.setAttribute("visibility", finite ? "visible" : "hidden");
  if (rendered.label) {
    rendered.label.setAttribute("visibility", finite ? "visible" : "hidden");
  }
  if (!finite) return;
  const real = Boolean(item.real);
  rendered.realGroup.setAttribute("visibility", real ? "visible" : "hidden");
  rendered.imaginaryGroup.setAttribute("visibility", real ? "hidden" : "visible");
  if (real) {
    const x1 = transform.x(item.x1);
    const y1 = transform.y(item.y1);
    const x2 = transform.x(item.x2);
    const y2 = transform.y(item.y2);
    rendered.connector.setAttribute("x1", String(x1));
    rendered.connector.setAttribute("y1", String(y1));
    rendered.connector.setAttribute("x2", String(x2));
    rendered.connector.setAttribute("y2", String(y2));
    rendered.first.setAttribute("cx", String(x1));
    rendered.first.setAttribute("cy", String(y1));
    rendered.second.setAttribute("cx", String(x2));
    rendered.second.setAttribute("cy", String(y2));
    rendered.second.setAttribute("visibility", item.tangent ? "hidden" : "visible");
    if (rendered.label) {
      rendered.label.setAttribute("x", String(x2 + 8));
      rendered.label.setAttribute("y", String(y2 - 8));
    }
    rendered.title.textContent = item.tangent
      ? `${item.label || item.id}: tangent point (${item.x1.toFixed(4)}, ${item.y1.toFixed(4)})`
      : `${item.label || item.id}: point pair`;
    return;
  }

  const cx = transform.x(item.cx);
  const cy = transform.y(item.cy);
  const size = 6;
  rendered.imaginaryA.setAttribute("x1", String(cx - size));
  rendered.imaginaryA.setAttribute("y1", String(cy - size));
  rendered.imaginaryA.setAttribute("x2", String(cx + size));
  rendered.imaginaryA.setAttribute("y2", String(cy + size));
  rendered.imaginaryB.setAttribute("x1", String(cx - size));
  rendered.imaginaryB.setAttribute("y1", String(cy + size));
  rendered.imaginaryB.setAttribute("x2", String(cx + size));
  rendered.imaginaryB.setAttribute("y2", String(cy - size));
  if (rendered.label) {
    rendered.label.setAttribute("x", String(cx + 8));
    rendered.label.setAttribute("y", String(cy - 8));
  }
  rendered.title.textContent = `${item.label || item.id}: imaginary point pair`;
}

function drawDipole(svg, item, transform) {
  const node = svgElement("g", {
    class: "galaga-cga2d-object galaga-cga2d-dipole",
  });
  const realGroup = svgElement("g");
  const connector = svgElement("line", {
    stroke: item.color,
    class: `galaga-cga2d-dipole-connector galaga-cga2d-${item.line_style ?? "dotted"}`,
  });
  const first = svgElement("circle", {
    r: 5,
    fill: item.color,
    class: "galaga-cga2d-dipole-point",
  });
  const second = svgElement("circle", {
    r: 5,
    fill: item.color,
    class: "galaga-cga2d-dipole-point",
  });
  realGroup.append(connector, first, second);

  const imaginaryGroup = svgElement("g", {
    stroke: item.color,
    class: "galaga-cga2d-dipole-imaginary",
  });
  const imaginaryA = svgElement("line");
  const imaginaryB = svgElement("line");
  imaginaryGroup.append(imaginaryA, imaginaryB);
  const title = svgElement("title");
  node.append(realGroup, imaginaryGroup, title);
  svg.appendChild(node);

  const itemLabel = label(
    svg,
    item,
    transform.x(item.finite === false ? 0 : item.cx),
    transform.y(item.finite === false ? 0 : item.cy),
  );
  const rendered = {
    kind: item.kind,
    node,
    label: itemLabel,
    realGroup,
    connector,
    first,
    second,
    imaginaryGroup,
    imaginaryA,
    imaginaryB,
    title,
  };
  updateDipoleGeometry(rendered, item, transform);
  return rendered;
}

function render({ model, el }) {
  el.classList.add("galaga-cga2d-widget");
  const frame = document.createElement("div");
  frame.className = "galaga-cga2d-frame";
  const status = document.createElement("div");
  status.className = "galaga-cga2d-status";
  frame.appendChild(status);
  el.replaceChildren(frame);

  let activeDrag = null;
  let awaitingScene = null;
  let lastPythonSync = 0;
  let renderedGeometry = new Map();

  function syncPointToPython(id, x, y, forceSync = false) {
    const now = performance.now();
    if (!forceSync && now - lastPythonSync <= POINT_SYNC_INTERVAL_MS) return;
    const current = model.get("point_coordinates") ?? {};
    if (samePointCoordinates(current[id], x, y)) return;
    const next = { ...current };
    next[id] = [x, y];
    model.set("point_coordinates", next);
    model.save_changes();
    lastPythonSync = now;
  }

  function sceneReachedReleasedPoint() {
    if (!awaitingScene) return true;
    const item = (model.get("scene") ?? []).find(
      (entry) => entry.kind === "point" && entry.id === awaitingScene.id,
    );
    return (
      item &&
      Math.abs(item.x - awaitingScene.x) < 1e-9 &&
      Math.abs(item.y - awaitingScene.y) < 1e-9
    );
  }

  function updateDerivedGeometryDuringDrag() {
    const view = model.get("view") ?? {};
    const transform = geometry(view);
    const scene = model.get("scene") ?? [];
    for (const item of scene.filter((entry) => entry.kind !== "point")) {
      const rendered = renderedGeometry.get(item.id);
      if (!rendered || rendered.kind !== item.kind) continue;
      if (item.kind === "dipole") {
        updateDipoleGeometry(rendered, item, transform);
      } else if (item.kind === "line") {
        const endpoints = lineEndpoints(item, transform.visible);
        const visible = endpoints.length === 2;
        rendered.node.setAttribute("visibility", visible ? "visible" : "hidden");
        if (rendered.label) {
          rendered.label.setAttribute("visibility", visible ? "visible" : "hidden");
        }
        if (!visible) continue;
        const [[x1, y1], [x2, y2]] = endpoints;
        rendered.node.setAttribute("x1", String(transform.x(x1)));
        rendered.node.setAttribute("y1", String(transform.y(y1)));
        rendered.node.setAttribute("x2", String(transform.x(x2)));
        rendered.node.setAttribute("y2", String(transform.y(y2)));
        if (rendered.label) {
          rendered.label.setAttribute("x", String(transform.x((x1 + x2) / 2) + 8));
          rendered.label.setAttribute("y", String(transform.y((y1 + y2) / 2) - 8));
        }
      } else if (item.kind === "circle") {
        rendered.node.setAttribute("cx", String(transform.x(item.cx)));
        rendered.node.setAttribute("cy", String(transform.y(item.cy)));
        rendered.node.setAttribute("r", String(item.r * transform.scale));
        if (rendered.label) {
          rendered.label.setAttribute("x", String(transform.x(item.cx + item.r) + 8));
          rendered.label.setAttribute("y", String(transform.y(item.cy) - 8));
        }
      }
    }
  }

  function draw() {
    if (activeDrag) return;
    const view = model.get("view") ?? {};
    const transform = geometry(view);
    const svg = svgElement("svg", {
      viewBox: `0 0 ${transform.width} ${transform.height}`,
      role: "img",
      "aria-label": "Two-dimensional conformal geometric algebra plot",
    });
    svg.classList.add("galaga-cga2d-svg");
    drawGrid(svg, transform, Boolean(view.grid ?? true));
    drawAxes(svg, transform);

    const scene = model.get("scene") ?? [];
    const nextRenderedGeometry = new Map();
    for (const item of scene.filter((entry) => entry.kind !== "point")) {
      if (item.kind === "dipole") {
        nextRenderedGeometry.set(item.id, drawDipole(svg, item, transform));
      } else if (item.kind === "line") {
        const endpoints = lineEndpoints(item, transform.visible);
        if (endpoints.length === 2) {
          const [[x1, y1], [x2, y2]] = endpoints;
          const node = svgElement("line", {
            x1: transform.x(x1),
            y1: transform.y(y1),
            x2: transform.x(x2),
            y2: transform.y(y2),
            stroke: item.color,
            class: `galaga-cga2d-object galaga-cga2d-line galaga-cga2d-${item.line_style ?? "solid"}`,
          });
          svg.appendChild(node);
          const itemLabel = label(
            svg,
            item,
            transform.x((x1 + x2) / 2),
            transform.y((y1 + y2) / 2),
          );
          nextRenderedGeometry.set(item.id, { kind: item.kind, node, label: itemLabel });
        }
      } else if (item.kind === "circle") {
        const node = svgElement("circle", {
          cx: transform.x(item.cx),
          cy: transform.y(item.cy),
          r: item.r * transform.scale,
          stroke: item.color,
          class: `galaga-cga2d-object galaga-cga2d-circle galaga-cga2d-${item.line_style ?? "solid"}`,
        });
        svg.appendChild(node);
        const itemLabel = label(svg, item, transform.x(item.cx + item.r), transform.y(item.cy));
        nextRenderedGeometry.set(item.id, { kind: item.kind, node, label: itemLabel });
      }
    }

    const pointCoordinates = model.get("point_coordinates") ?? {};
    for (const item of scene.filter((entry) => entry.kind === "point")) {
      const synchronized = pointCoordinates[item.id];
      const pointX = Array.isArray(synchronized) ? synchronized[0] : item.x;
      const pointY = Array.isArray(synchronized) ? synchronized[1] : item.y;
      const point = svgElement("circle", {
        cx: transform.x(pointX),
        cy: transform.y(pointY),
        r: item.draggable ? 7 : 5,
        fill: item.color,
        tabindex: item.draggable ? 0 : -1,
        class: `galaga-cga2d-object galaga-cga2d-point${item.draggable ? " is-draggable" : ""}`,
      });
      const pointLabel = label(svg, item, transform.x(pointX), transform.y(pointY));
      const title = svgElement("title");
      title.textContent = `${item.label || item.id}: (${pointX.toFixed(4)}, ${pointY.toFixed(4)})`;
      point.appendChild(title);
      svg.appendChild(point);

      if (item.draggable) {
        point.addEventListener("pointerdown", (event) => {
          awaitingScene = null;
          activeDrag = {
            id: item.id,
            point,
            label: pointLabel,
            x: pointX,
            y: pointY,
            moved: false,
          };
          point.setPointerCapture(event.pointerId);
          point.classList.add("is-dragging");
          event.preventDefault();
        });
        point.addEventListener("pointermove", (event) => {
          if (!activeDrag || activeDrag.id !== item.id) return;
          const bounds = svg.getBoundingClientRect();
          const px = ((event.clientX - bounds.left) / bounds.width) * transform.width;
          const py = ((event.clientY - bounds.top) / bounds.height) * transform.height;
          const x = transform.inverseX(px);
          const y = transform.inverseY(py);
          activeDrag.x = x;
          activeDrag.y = y;
          activeDrag.moved = true;
          point.setAttribute("cx", String(transform.x(x)));
          point.setAttribute("cy", String(transform.y(y)));
          if (pointLabel) {
            pointLabel.setAttribute("x", String(transform.x(x) + 8));
            pointLabel.setAttribute("y", String(transform.y(y) - 8));
          }
          syncPointToPython(item.id, x, y);
        });
        const finish = (event) => {
          if (!activeDrag || activeDrag.id !== item.id) return;
          const released = activeDrag;
          if (released.moved) {
            syncPointToPython(released.id, released.x, released.y, true);
          }
          if (point.hasPointerCapture(event.pointerId)) {
            point.releasePointerCapture(event.pointerId);
          }
          point.classList.remove("is-dragging");
          activeDrag = null;
          awaitingScene = released.moved
            ? { id: released.id, x: released.x, y: released.y }
            : null;
          redraw();
        };
        point.addEventListener("pointerup", finish);
        point.addEventListener("pointercancel", finish);
      }
    }

    const oldSvg = frame.querySelector("svg");
    if (oldSvg) oldSvg.replaceWith(svg);
    else frame.prepend(svg);
    renderedGeometry = nextRenderedGeometry;
    status.textContent = model.get("error") || "";
    status.hidden = !status.textContent;
  }

  const redraw = () => {
    if (activeDrag) {
      updateDerivedGeometryDuringDrag();
      return;
    }
    if (!sceneReachedReleasedPoint()) return;
    awaitingScene = null;
    draw();
  };
  const updateStatus = () => {
    status.textContent = model.get("error") || "";
    status.hidden = !status.textContent;
  };
  model.on("change:scene", redraw);
  model.on("change:view", redraw);
  model.on("change:error", updateStatus);
  draw();

  return () => {
    model.off("change:scene", redraw);
    model.off("change:view", redraw);
    model.off("change:error", updateStatus);
  };
}

export default { render };
