#!/usr/bin/env python3
"""Build a self-contained, horizontally navigable Kruskal presentation."""

from __future__ import annotations

import base64
import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", "/tmp/cse5311-matplotlib")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


FILES = {
    "vanilla": ROOT / "benchmark.csv",
    "radix": ROOT / "radix_sort_benchmark.csv",
}
PALETTE = {"vanilla": "#2864dc", "radix": "#0b8f76"}
INK = "#17243b"
MUTED = "#52627a"
GRID = "#dfe5ee"


def load_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {row["dataset"]: row for row in csv.DictReader(f)}


vanilla = load_rows(FILES["vanilla"])
radix = load_rows(FILES["radix"])
datasets = list(vanilla)
labels = [name.removeprefix("USA-road-d.").removesuffix(".gr-undirected.csv")
          .removesuffix(".graph-undirected.csv") for name in datasets]
edges = [int(vanilla[name]["edges"]) for name in datasets]
vanilla_t = [float(vanilla[name]["average_algorithm_time_seconds"]) for name in datasets]
radix_t = [float(radix[name]["average_algorithm_time_seconds"]) for name in datasets]
speedups = [a / b for a, b in zip(vanilla_t, radix_t)]
vanilla_mib = [float(vanilla[name]["allocated_space_mib"]) for name in datasets]
radix_mib = [float(radix[name]["allocated_space_mib"]) for name in datasets]
chart_order = sorted(range(len(datasets)), key=lambda i: edges[i])

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": GRID,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def save_runtime_plot() -> Path:
    fig, ax = plt.subplots(figsize=(11.5, 5.4), dpi=180)
    x = [edges[i] for i in chart_order]
    qsort = [vanilla_t[i] for i in chart_order]
    radix_sorted = [radix_t[i] for i in chart_order]
    ax.plot(x, qsort, "o-", color=PALETTE["vanilla"], lw=2.8,
            ms=8, label="Vanilla · comparison sort")
    ax.plot(x, radix_sorted, "o-", color=PALETTE["radix"], lw=2.8,
            ms=8, label="Radix sort")
    for i in chart_order:
        ax.annotate(labels[i], (edges[i], vanilla_t[i]), xytext=(6, 9), textcoords="offset points",
                    color=PALETTE["vanilla"], fontsize=9, weight="bold")
    for i in chart_order:
        ax.annotate(labels[i], (edges[i], radix_t[i]), xytext=(6, -16), textcoords="offset points",
                    color=PALETTE["radix"], fontsize=9, weight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(edges[chart_order[0]] * .78, edges[chart_order[-1]] * 1.42)
    ax.set_xlabel("Input edges (log scale)", labelpad=10)
    ax.set_ylabel("Sort + Kruskal scan time (seconds, log scale)", labelpad=10)
    ax.grid(True, which="both", color=GRID, linewidth=.8)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = ROOT / "runtime_comparison.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_speedup_plot() -> Path:
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=180)
    bars = ax.barh(labels, speedups, color=PALETTE["radix"], height=.58)
    ax.invert_yaxis()
    ax.set_xlabel("Vanilla time ÷ radix time (higher is faster)", labelpad=10)
    ax.set_xlim(0, max(speedups) * 1.22)
    ax.grid(axis="x", color=GRID, linewidth=.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    for bar, value in zip(bars, speedups):
        ax.text(value + .035, bar.get_y() + bar.get_height()/2,
                f"{value:.2f}×", va="center", color=INK, weight="bold")
    fig.tight_layout()
    path = ROOT / "speedup_comparison.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_memory_plot() -> Path:
    fig, ax = plt.subplots(figsize=(11.5, 5.2), dpi=180)
    x = [edges[i] for i in chart_order]
    qsort = [vanilla_mib[i] for i in chart_order]
    radix_sorted = [radix_mib[i] for i in chart_order]
    ax.plot(x, qsort, "o-", color=PALETTE["vanilla"], lw=2.8,
            ms=8, label="Vanilla · comparison sort")
    ax.plot(x, radix_sorted, "o-", color=PALETTE["radix"], lw=2.8,
            ms=8, label="Radix sort")
    for i in chart_order:
        ax.annotate(labels[i], (edges[i], vanilla_mib[i]), xytext=(6, 8),
                    textcoords="offset points", color=PALETTE["vanilla"],
                    fontsize=9, weight="bold")
    for i in chart_order:
        ax.annotate(labels[i], (edges[i], radix_mib[i]), xytext=(6, -16),
                    textcoords="offset points", color=PALETTE["radix"],
                    fontsize=9, weight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(edges[chart_order[0]] * .78, edges[chart_order[-1]] * 1.42)
    ax.set_xlabel("Input edges (log scale)", labelpad=10)
    ax.set_ylabel("Explicit array storage (MiB, log scale)", labelpad=10)
    ax.grid(True, which="both", color=GRID, linewidth=.8)
    ax.legend(frameon=False, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    path = ROOT / "memory_comparison.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def save_mst_diagram() -> Path:
    pos = {"A": (0, 1.1), "B": (1.5, 1.1), "C": (3, 1.1),
           "D": (1.5, -.45), "E": (3, -.45)}
    edges_data = [("A", "B", 1), ("B", "C", 2), ("A", "C", 3),
                  ("B", "D", 4), ("C", "D", 6), ("D", "E", 5), ("C", "E", 8)]
    chosen = {("A", "B"), ("B", "C"), ("B", "D"), ("D", "E")}
    label_pos = {("A", "B"): (.75, 1.36), ("B", "C"): (2.25, 1.36),
                 ("A", "C"): (1.50, 1.72), ("B", "D"): (1.23, .30),
                 ("C", "D"): (2.52, .46), ("D", "E"): (2.25, -.66),
                 ("C", "E"): (3.20, .30)}
    fig, ax = plt.subplots(figsize=(10.5, 4.1), dpi=180)
    for u, v, weight in edges_data:
        x1, y1 = pos[u]
        x2, y2 = pos[v]
        is_chosen = (u, v) in chosen or (v, u) in chosen
        ax.plot([x1, x2], [y1, y2], color=PALETTE["radix"] if is_chosen else "#aeb8c7",
                linewidth=4 if is_chosen else 2, linestyle="-" if is_chosen else "--", zorder=1)
        lx, ly = label_pos[(u, v)]
        ax.text(lx, ly, str(weight),
                ha="center", va="center", color=INK, fontsize=11,
                bbox={"alpha": .97, "facecolor": "white", "edgecolor": "none", "pad": 1.5}, zorder=3)
    for node, (x, y) in pos.items():
        ax.scatter([x], [y], s=1550, c="#edf3ff", edgecolors=PALETTE["vanilla"],
                   linewidths=2.2, zorder=2)
        ax.text(x, y, node, ha="center", va="center", fontsize=15, weight="bold", color=INK, zorder=4)
    ax.text(.5, -.20, "Accepted edges: 1 + 2 + 4 + 5 = 12    |    Dashed edges would create a cycle",
            transform=ax.transAxes, ha="center", color=MUTED, fontsize=10)
    ax.set_xlim(-.7, 3.7)
    ax.set_ylim(-1.1, 2.0)
    ax.set_axis_off()
    fig.tight_layout()
    path = ROOT / "mst_example.png"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def image_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


runtime_img = image_uri(save_runtime_plot())
speedup_img = image_uri(save_speedup_plot())
memory_img = image_uri(save_memory_plot())
mst_img = image_uri(save_mst_diagram())
largest = datasets[max(range(len(edges)), key=edges.__getitem__)]
largest_label = labels[edges.index(max(edges))]
largest_vanilla = vanilla_t[edges.index(max(edges))]
largest_radix = radix_t[edges.index(max(edges))]
largest_speedup = speedups[edges.index(max(edges))]
largest_mem_ratio = radix_mib[edges.index(max(edges))] / vanilla_mib[edges.index(max(edges))]

html = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kruskal: From spanning trees to faster sorting</title>
<style>
:root{--ink:#17243b;--muted:#52627a;--blue:#2864dc;--teal:#0b8f76;--line:#dfe5ee;--paper:#fff;--soft:#f4f7fb}
*{box-sizing:border-box}html,body{height:100%;margin:0;color:var(--ink);background:var(--paper);font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
body{overflow:hidden}.deck{display:flex;height:100vh;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;scroll-behavior:smooth;scrollbar-width:thin;scrollbar-color:#b8c4d4 #f1f3f7}
.slide{flex:0 0 100vw;width:100vw;height:100vh;scroll-snap-align:start;padding:5.2vh 7vw 8vh;position:relative;display:flex;flex-direction:column;justify-content:center;overflow:hidden;background:white}
.slide:nth-child(even){background:#fbfcfe}.eyebrow{font-size:13px;letter-spacing:.13em;text-transform:uppercase;font-weight:800;color:var(--teal);margin-bottom:15px}.slide h1,.slide h2{margin:0;letter-spacing:-.045em;line-height:1.05}.slide h1{font-size:clamp(42px,6vw,82px);max-width:970px}.slide h2{font-size:clamp(34px,4.1vw,57px);margin-bottom:16px}.lead{font-size:clamp(18px,2vw,25px);line-height:1.48;color:var(--muted);max-width:900px;margin:20px 0}.subtitle{font-size:20px;color:var(--muted);margin-top:22px}.tagline{display:inline-flex;align-items:center;gap:9px;padding:9px 13px;border:1px solid var(--line);border-radius:999px;color:var(--muted);font-size:14px;margin-top:14px;width:max-content}.dot{width:9px;height:9px;background:var(--teal);border-radius:50%}
.split{display:grid;grid-template-columns:1fr 1.2fr;gap:4vw;align-items:center}.visual{width:100%;max-height:52vh;object-fit:contain}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:22px}.card{border:1px solid var(--line);border-radius:15px;padding:18px 19px;background:white}.card b{display:block;font-size:17px;margin-bottom:7px}.card p{margin:0;color:var(--muted);font-size:15px;line-height:1.45}.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-top:24px}.step{border-top:3px solid var(--teal);padding:15px 13px 0 0;color:var(--muted);line-height:1.45}.step strong{display:block;color:var(--ink);font-size:16px;margin-bottom:5px}.chart{width:min(100%,1120px);max-height:57vh;object-fit:contain;align-self:center}.stats{display:flex;gap:13px;flex-wrap:wrap;margin:12px 0}.stat{padding:13px 16px;border:1px solid var(--line);border-radius:12px;min-width:170px}.stat strong{display:block;font-size:24px;color:var(--teal)}.stat span{font-size:13px;color:var(--muted)}
.complexity-slide .chart{max-height:40vh}.analysis-slide .chart{max-height:44vh}.formula{border-left:4px solid var(--teal);background:var(--soft);padding:11px 15px;border-radius:0 10px 10px 0;color:var(--ink);font-size:16px;line-height:1.45;margin:5px 0 11px}.formula b{color:var(--blue)}
.foot{position:absolute;left:7vw;right:7vw;bottom:25px;display:flex;justify-content:space-between;align-items:center;color:#7a8799;font-size:12px}.progress{position:fixed;top:0;left:0;height:4px;background:var(--teal);width:20%;z-index:4;transition:width .25s}.nav{position:fixed;right:22px;bottom:17px;z-index:5;display:flex;gap:7px}.nav button,.notes-toggle{border:1px solid var(--line);background:white;color:var(--ink);border-radius:10px;padding:9px 12px;cursor:pointer;box-shadow:0 2px 9px #17243b12}.nav button:hover,.notes-toggle:hover{background:var(--soft)}.notes-toggle{position:fixed;right:22px;top:17px;z-index:5;font-size:12px}.notes{display:none;position:fixed;right:22px;top:58px;z-index:5;width:min(350px,80vw);padding:14px;border:1px solid var(--line);border-radius:12px;background:#fff;color:var(--muted);box-shadow:0 8px 30px #17243b18;font-size:14px;line-height:1.5}.notes.show{display:block}.keyhint{margin-right:100px}
@media(max-width:760px){.slide{padding:6vh 6vw 9vh}.split{grid-template-columns:1fr;gap:10px}.split .visual{max-height:35vh}.cards{grid-template-columns:1fr}.steps{grid-template-columns:repeat(2,1fr)}.chart{max-height:45vh}.foot{left:6vw;right:6vw}.slide h2{font-size:36px}}
</style></head><body><div class="progress" id="progress"></div>
<button class="notes-toggle" onclick="document.querySelector('.notes').classList.toggle('show')">Speaker notes · N</button><aside class="notes" id="notes"></aside>
<main class="deck" id="deck">
<section class="slide" data-notes="Open with the practical purpose: finding a cheapest way to connect locations. Explain that disconnected inputs yield a minimum spanning forest. Transition: the greedy rule is simple; the cost is mainly ordering edges.">
 <div class="eyebrow">01 · The problem</div><div class="split"><div><h1>What does Kruskal solve?</h1><p class="lead">Kruskal’s algorithm finds a <b>minimum spanning tree</b>: the lowest-total-weight set of links that connects every vertex without cycles.</p><div class="tagline"><i class="dot"></i> A greedy algorithm for weighted, undirected graphs</div><div class="cards"><div class="card"><b>Purpose</b><p>Connect locations at minimum total cost.</p></div><div class="card"><b>Examples</b><p>Road, cable, or utility network planning.</p></div><div class="card"><b>Disconnected graph</b><p>Returns a minimum spanning forest, one tree per component.</p></div></div></div><div><img class="visual" src="__MST__" alt="Weighted graph showing selected minimum spanning tree edges"></div></div>
 <div class="foot"><span>Kruskal · introduction and performance comparison</span><span>0:00–0:25 · 2 min</span></div>
</section>
<section class="slide complexity-slide" data-notes="Walk the example: process edges from lowest weight upward. Keep an edge only if its endpoints are in different components. Edge 3 closes a cycle and is skipped. The dominant vanilla cost is comparison sorting, O(E log E); radix ordering takes O(E) for fixed-width 32-bit integer weights. The disjoint-set operations add O(E alpha(V)) amortized time to either. Space is O(E+V) for the stored edges and disjoint set; radix needs an additional O(E) buffer.">
 <div class="eyebrow">02 · The greedy rule</div><h2>Take the lightest safe edge</h2><p class="lead">Process edges by weight. Add an edge when it joins two components; skip it when it would create a cycle.</p><img class="chart" src="__MST__" alt="Kruskal example: selected tree edges are teal and rejected edges are dashed"><div class="steps"><div class="step"><strong>1 · Order</strong>Consider edges from least to greatest weight.</div><div class="step"><strong>2 · Check</strong>Are the endpoints already connected?</div><div class="step"><strong>3 · Keep or skip</strong>Join different components; avoid cycles.</div><div class="step"><strong>4 · Finish</strong>Stop at V−1 accepted edges for a connected graph.</div></div><div class="formula"><b>Time:</b> vanilla O(E log E) · radix O(E) for fixed-width weights · DSU adds O(E α(V)) to both. &nbsp; <b>Space:</b> both O(E+V); radix has an extra O(E) buffer.</div>
 <div class="foot"><span>Disjoint-set union tracks connected components</span><span>0:25–0:48</span></div>
</section>
<section class="slide" data-notes="Describe a controlled comparison: same five inputs, single-threaded C implementations, three repetitions per data set. Only the edge-ordering method changes. The reported algorithm time excludes file parsing and disjoint-set initialization; it includes sorting and scanning. It is not end-to-end runtime.">
 <div class="eyebrow">03 · Experiment</div><h2>Same algorithm; different edge ordering</h2><p class="lead">Compare the original qsort-based implementation with a radix-sort variant. Both are single-threaded C programs and use the same Kruskal scan and union-find.</p><div class="cards"><div class="card"><b>Vanilla Kruskal</b><p>Comparison-sort all edges, then scan in ascending order.</p></div><div class="card"><b>Radix Kruskal</b><p>Stable four-pass radix sort for signed 32-bit integer weights, then the same scan.</p></div><div class="card"><b>Fair measurement</b><p>Five data sets · 3 runs each · report average sort + scan time.</p></div></div><div class="stats"><div class="stat"><strong>59.8k → 28.9m</strong><span>edges across the input sets</span></div><div class="stat"><strong>1 thread</strong><span>both variants</span></div><div class="stat"><strong>same results</strong><span>forest weights and component counts match</span></div></div>
 <div class="foot"><span>Input parsing and disjoint-set initialization excluded from timer</span><span>0:48–1:08</span></div>
</section>
<section class="slide analysis-slide" data-notes="The theory predicts O(E log E) sorting for vanilla comparison sort and O(E) for radix with fixed 32-bit integer weights. Both add the same near-linear disjoint-set work. The curves rise with input size and radix remains faster, consistent with those predictions. However, only five benchmark inputs cannot establish asymptotic complexity or isolate a precise exponent; they show empirical behavior for these datasets.">
 <div class="eyebrow">04 · Runtime trend</div><h2>Does measured time fit the theory?</h2><p class="lead">The time curves rise with graph size, and radix stays faster. That is consistent with the expected sorting costs:</p><div class="formula"><b>Vanilla:</b> O(E log E) &nbsp; · &nbsp; <b>Radix:</b> O(E) for fixed 32-bit weights &nbsp; · &nbsp; both include O(E α(V)) DSU work.</div><img class="chart" src="__RUNTIME__" alt="Log-log runtime chart comparing vanilla Kruskal with radix-sort Kruskal across five graph sizes"><div class="tagline"><i class="dot"></i> Consistent with theory on these 5 inputs; measurements do not prove asymptotic bounds.</div>
 <div class="foot"><span>Average of 3 runs per data set</span><span>1:08–1:27</span></div>
</section>
<section class="slide analysis-slide" data-notes="Both variants have O(E+V) explicit storage for the edge and disjoint-set arrays. Radix adds a second edge array, also O(E), so the asymptotic order stays O(E+V) while the constant factor increases. The measured curves grow with input size, as expected. USA-t uses about 444 MiB for vanilla and 775 MiB for radix. These are explicit arrays, not process peak RSS; five sizes are evidence of the trend, not proof of the asymptotic formula.">
 <div class="eyebrow">05 · Memory trend</div><h2>Does measured space fit the theory?</h2><p class="lead">Both implementations store edges and disjoint-set arrays, so their expected storage is linear in graph size. Radix adds another edge buffer.</p><div class="formula"><b>Vanilla:</b> O(E+V) &nbsp; · &nbsp; <b>Radix:</b> O(E+V), with a larger constant from its O(E) auxiliary buffer.</div><img class="chart" src="__MEMORY__" alt="Log-log memory chart comparing explicit array storage for vanilla and radix Kruskal across five graph sizes"><div class="tagline"><i class="dot"></i> Measured storage grows as expected; five inputs support the trend, not prove the bound.</div>
 <div class="foot"><span>Explicit array storage, not process peak RSS</span><span>1:27–1:45</span></div>
</section>
<section class="slide" data-notes="Conclude with the evidence. Radix is faster on all five tested inputs, with about 2.4x improvement on USA-t. The cost is additional memory for the radix buffer. These results are specific to the tested integer-weight graph data and this implementation; further work could examine other weight ranges and graph families.">
 <div class="eyebrow">06 · Result and discovery</div><h2>When is the optimization worth it?</h2><p class="lead">Across these five graph inputs, radix ordering reduced the measured Kruskal phase time every time.</p><img class="chart" src="__SPEEDUP__" alt="Speedup of radix sort over vanilla comparison sorting for five graph datasets"><div class="stats"><div class="stat"><strong>__SPEEDUP_LARGEST__× faster</strong><span>USA-t: __VANILLA_LARGEST__ s → __RADIX_LARGEST__ s</span></div><div class="stat"><strong>__MEM_RATIO__× storage</strong><span>USA-t explicit arrays: __VANILLA_MIB__ → __RADIX_MIB__ MiB</span></div></div><p class="lead" style="font-size:17px;margin-top:7px">Discovery: for these integer-weight graphs, radix sort substantially improved runtime at the cost of extra array memory.</p>
 <div class="foot"><span>Measured over 3 runs; single-threaded implementations</span><span>1:45–2:00</span></div>
</section></main><div class="nav"><button id="prev" aria-label="Previous slide">←</button><button id="next" aria-label="Next slide">→</button></div>
<script>
const deck=document.getElementById('deck'),slides=[...document.querySelectorAll('.slide')],progress=document.getElementById('progress'),notes=document.getElementById('notes');let index=0;
function show(i){index=Math.max(0,Math.min(slides.length-1,i));slides[index].scrollIntoView({behavior:'smooth',inline:'start'});notes.textContent=slides[index].dataset.notes;progress.style.width=((index+1)/slides.length*100)+'%'}
document.getElementById('prev').onclick=()=>show(index-1);document.getElementById('next').onclick=()=>show(index+1);
deck.addEventListener('scroll',()=>{const i=Math.round(deck.scrollLeft/innerWidth);if(i!==index){index=i;notes.textContent=slides[i].dataset.notes;progress.style.width=((i+1)/slides.length*100)+'%'}});
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(index+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(index-1)}if(e.key.toLowerCase()==='n')notes.classList.toggle('show')});
notes.textContent=slides[0].dataset.notes;progress.style.width=(100/slides.length)+'%';
</script></body></html>'''

html = (html.replace("__MST__", mst_img).replace("__RUNTIME__", runtime_img)
        .replace("__SPEEDUP__", speedup_img)
        .replace("__MEMORY__", memory_img)
        .replace("__SPEEDUP_LARGEST__", f"{largest_speedup:.2f}")
        .replace("__VANILLA_LARGEST__", f"{largest_vanilla:.2f}")
        .replace("__RADIX_LARGEST__", f"{largest_radix:.2f}")
        .replace("__MEM_RATIO__", f"{largest_mem_ratio:.2f}")
        .replace("__VANILLA_MIB__", f"{vanilla_mib[edges.index(max(edges))]:.1f}")
        .replace("__RADIX_MIB__", f"{radix_mib[edges.index(max(edges))]:.1f}"))
(ROOT / "presentation.html").write_text(html, encoding="utf-8")
print("Created presentation.html and runtime_comparison.png, memory_comparison.png, speedup_comparison.png, mst_example.png")
