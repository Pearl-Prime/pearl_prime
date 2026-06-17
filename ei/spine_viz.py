"""
ei.spine_viz — a self-contained HTML visualization of the discovered
Contemplative Spine / CEG. No external JS deps; renders an SVG force-ish layout
of the roots sized by atom count, colored by universality, with a provenance
table (which teachers contribute to each universal root).
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path


def _svg_nodes(nodes) -> str:
    # simple radial layout: universal roots in an inner ring, others outer
    universal = [n for n in nodes if n.is_universal]
    other = [n for n in nodes if not n.is_universal]
    W, H = 900, 560
    cx, cy = W / 2, H / 2
    parts = []
    max_size = max((n.size for n in nodes), default=1)

    def place(group, radius, color):
        k = max(len(group), 1)
        for i, n in enumerate(group):
            ang = 2 * math.pi * i / k - math.pi / 2
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            r = 10 + 34 * math.sqrt(n.size / max_size)
            label = html.escape(n.label[:26])
            tip = html.escape(f"{n.node_id} | {n.size} atoms | {n.n_teachers} teachers: {', '.join(n.teachers)}")
            parts.append(
                f'<g><title>{tip}</title>'
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{color}" '
                f'fill-opacity="0.78" stroke="#1f2933" stroke-width="1.2"/>'
                f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" '
                f'font-size="10" fill="#0b1320" font-family="system-ui">{label}</text>'
                f'<text x="{x:.0f}" y="{y+12:.0f}" text-anchor="middle" '
                f'font-size="9" fill="#33424f">{n.n_teachers}T·{n.size}</text></g>'
            )

    place(universal, 150, "#7dd3fc")
    place(other, 250, "#fde68a")
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:960px">{"".join(parts)}</svg>'


def _provenance_table(nodes) -> str:
    rows = []
    for n in sorted(nodes, key=lambda x: -x.n_teachers):
        if not n.is_universal:
            continue
        dist = ", ".join(f"{t}×{c}" for t, c in
                         sorted(n.teacher_distribution.items(), key=lambda kv: -kv[1]))
        ex = html.escape((n.exemplar_texts[0] if n.exemplar_texts else "")[:160])
        rows.append(
            f"<tr><td>{n.node_id}</td><td><b>{html.escape(n.label)}</b></td>"
            f"<td>{n.n_teachers}</td><td>{n.size}</td>"
            f"<td style='font-size:11px'>{html.escape(dist)}</td>"
            f"<td style='font-size:11px;color:#475569'>“{ex}”</td></tr>"
        )
    return (
        "<table><thead><tr><th>root</th><th>label</th><th>#teachers</th>"
        "<th>#atoms</th><th>provenance (teacher×count)</th><th>exemplar (attributed)</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def write_spine_viz(result, out_path: Path) -> str:
    out_path = Path(out_path)
    n_univ = len(result.universal_nodes)
    page = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Contemplative Spine / CEG — discovered</title>
<style>
 body{{font-family:system-ui,Segoe UI,Arial;margin:24px;color:#0b1320;background:#f8fafc}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#475569;margin:0 0 16px;font-size:13px}}
 .legend span{{display:inline-block;margin-right:16px;font-size:12px}}
 .dot{{display:inline-block;width:11px;height:11px;border-radius:50%;vertical-align:middle;margin-right:5px}}
 table{{border-collapse:collapse;width:100%;margin-top:12px;background:#fff}}
 th,td{{border:1px solid #e2e8f0;padding:6px 8px;text-align:left;vertical-align:top}}
 th{{background:#f1f5f9;font-size:12px}}
 .meta{{font-size:12px;color:#334155;margin-top:8px}}
 code{{background:#eef2f7;padding:1px 5px;border-radius:4px}}
</style></head><body>
<h1>Contemplative Spine / Composite Essence Graph (CEG)</h1>
<p class="sub">spine ≡ CEG — one object, two roadmap names (#1517 Living Wisdom Graph · #1516 CEG). Advisory · free/local.</p>
<div class="legend">
 <span><span class="dot" style="background:#7dd3fc"></span>universal root (≥{result.universal_min_teachers} teachers)</span>
 <span><span class="dot" style="background:#fde68a"></span>narrower root</span>
 <span>circle size ∝ #atoms · label = top extracted terms</span>
</div>
{_svg_nodes(result.nodes)}
<p class="meta">
 atoms: <b>{result.n_atoms}</b> · roots: <b>{len(result.nodes)}</b> · universal roots:
 <b>{n_univ}</b> · modularity: <b>{result.modularity:.3f}</b> ·
 cluster: <code>{result.backend}</code> · embedding: <code>{html.escape(result.embedding_backend)}</code>
</p>
<h2 style="font-size:15px">Universal roots — provenance preserved (no homogenization)</h2>
{_provenance_table(result.nodes)}
</body></html>"""
    out_path.write_text(page, encoding="utf-8")
    return str(out_path)
