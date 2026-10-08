#!/usr/bin/env python3
import argparse
import glob
import os
import sys
import webbrowser

import numpy as np
from bokeh.layouts import column
from bokeh.models import (BoxAnnotation, ColumnDataSource, CrosshairTool, Div,
                          HoverTool, Label, Span)
from bokeh.plotting import figure, output_file, save
from pyulog import ULog

ROTOR_COLORS = ["#1f77b4", "#e8a33d", "#d62728", "#17becf", "#2ca02c", "#9467bd"]

NAV_STATES = {
    0: "Manual", 1: "Altitude", 2: "Position", 3: "Mission", 4: "Loiter",
    5: "RTL", 10: "Acro", 12: "Descend", 13: "Termination", 14: "Offboard",
    15: "Stabilized", 17: "Takeoff", 18: "Land", 19: "Follow Target",
    20: "Precland", 21: "Orbit", 22: "VTOL Takeoff",
    24: "PRISMA 1", 25: "PRISMA Manual",
}

MODE_COLORS = ["#e8f0fb", "#fdf3e0", "#eaf6ea", "#fdeaea", "#f2ecf9", "#e6f6f8"]

TOOLS = "xpan,xwheel_zoom,box_zoom,reset,save"

DEFAULT_LOG_DIR = os.environ.get(
    "TILT_LOG_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                 "Px4_Tilting_Custom_Control", "build", "px4_sitl_default",
                 "rootfs", "log"))

def resolve_ulog(arg):
    target = arg or DEFAULT_LOG_DIR

    if os.path.isfile(target):
        return target

    if not os.path.isdir(target):
        print(f"introuvable: {target}", file=sys.stderr)
        sys.exit(1)

    candidates = glob.glob(os.path.join(target, "**", "*.ulg"), recursive=True)

    if not candidates:
        print(f"aucun .ulg sous {target}", file=sys.stderr)
        sys.exit(1)

    newest = os.path.normpath(max(candidates, key=os.path.getmtime))
    print(f"dernier vol: {newest}")

    return newest

def load(path, topic):
    try:
        ulog = ULog(path, [topic])
    except Exception as exc:
        print(f"erreur de lecture de {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return ulog.data_list[0] if ulog.data_list else None

def rel_time(data, t0):
    return (data["timestamp"].astype(np.int64) - np.int64(t0)) / 1e6

def flight_mode_bands(path, t0):
    status = load(path, "vehicle_status")

    if status is None or "nav_state" not in status.data:
        return []

    t = rel_time(status.data, t0)
    nav = status.data["nav_state"].astype(int)
    changes = np.flatnonzero(np.diff(nav)) + 1
    starts = np.concatenate(([0], changes))
    stops = np.concatenate((changes, [len(nav) - 1]))

    return [(t[a], t[b], NAV_STATES.get(nav[a], f"mode {nav[a]}"))
            for a, b in zip(starts, stops) if t[b] > t[a]]

def airborne_edges(path, t0):
    land = load(path, "vehicle_land_detected")

    if land is None or "landed" not in land.data:
        return [], []

    t = rel_time(land.data, t0)
    flying = ~land.data["landed"].astype(bool)
    edges = np.diff(flying.astype(np.int8))

    return list(t[1:][edges == 1]), list(t[1:][edges == -1])

def make_plot(title, y_label, t, series, bands, takeoffs, landings, x_range=None):

    shared = {"x_range": x_range} if x_range is not None else {}

    p = figure(title=title, height=260, sizing_mode="stretch_width", tools=TOOLS,
               active_scroll="xwheel_zoom", x_axis_label="temps [s]",
               y_axis_label=y_label, background_fill_color="#fcfcfc", **shared)

    p.title.text_font_size = "12pt"
    p.title.text_font_style = "bold"
    p.grid.grid_line_alpha = 0.35

    for i, (start, stop, name) in enumerate(bands):
        p.add_layout(BoxAnnotation(left=start, right=stop, fill_alpha=1.0,
                                   fill_color=MODE_COLORS[i % len(MODE_COLORS)],
                                   level="underlay"))

        if x_range is None:
            p.add_layout(Label(x=start, y=8, y_units="screen", text=f" {name}",
                               text_font_size="9pt", text_color="#888",
                               level="underlay"))

    for t_edge, color in [(takeoffs, "#2e7d32"), (landings, "#c62828")]:
        for x in t_edge:
            p.add_layout(Span(location=x, dimension="height", line_color=color,
                              line_dash="dashed", line_width=1.5, line_alpha=0.7))

    source = ColumnDataSource({"t": t, **{name: v for name, v, _ in series}})
    tooltips = [("temps", "@t{0.000} s")]

    for name, _, color in series:
        p.line("t", name, source=source, line_width=1.4, color=color,
               legend_label=name, muted_alpha=0.12)
        tooltips.append((name, f"@{{{name}}}{{0.0000}}"))

    p.add_tools(HoverTool(tooltips=tooltips, mode="vline", attachment="right"))
    p.add_tools(CrosshairTool(dimensions="height", line_alpha=0.3))

    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"
    p.legend.click_policy = "mute"
    p.legend.label_text_font_size = "8pt"
    p.legend.background_fill_alpha = 0.75
    p.legend.padding = 4
    p.legend.spacing = 6

    return p

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ulog", nargs="?",
                    help="fichier .ulg, ou dossier dont on prend le vol le plus "
                         "recent. Par defaut: dernier vol SITL (voir TILT_LOG_DIR)")
    ap.add_argument("-o", "--output", help="fichier HTML de sortie (defaut: <vol>.html)")
    ap.add_argument("-n", "--rotors", type=int, default=6, help="nombre de rotors (defaut 6)")
    ap.add_argument("--no-browser", action="store_true", help="n'ouvre pas le navigateur")
    ap.add_argument("--cdn", action="store_true",
                    help="charge Bokeh depuis le CDN (page ~4x plus legere, "
                         "mais necessite une connexion pour s'afficher)")
    args = ap.parse_args()
    args.ulog = resolve_ulog(args.ulog)

    dbg = load(args.ulog, "debug_array")

    if dbg is None:
        print("debug_array absent de ce log: le control allocator n'a rien publie, "
              "ou le topic n'est pas enregistre.", file=sys.stderr)
        sys.exit(1)

    n = args.rotors
    t0 = dbg.data["timestamp"][0]
    t = rel_time(dbg.data, t0)

    def col(j):
        return dbg.data[f"data[{j}]"]

    bands = flight_mode_bands(args.ulog, t0)
    takeoffs, landings = airborne_edges(args.ulog, t0)

    def rotor_series(offset, scale=1.0):
        return [(f"rotor {i + 1}", col(3 * i + offset) * scale,
                 ROTOR_COLORS[i % len(ROTOR_COLORS)]) for i in range(n)]

    top = make_plot("torque_scale K*  —  <1 : couple sacrifie pour eviter une "
                    "poussee verticale negative", "K*", t,
                    [("K*", col(3 * n), "#c73e3e")], bands, takeoffs, landings)
    top.y_range.start, top.y_range.end = -0.05, 1.15

    plots = [top]

    for title, y_label, offset, scale in [
            ("Composante verticale par rotor", "vertical", 0, 1.0),
            ("Composante laterale par rotor", "lateral", 1, 1.0),
            ("Consigne servo de tilt", "angle [deg]", 2, 180.0 / np.pi)]:
        plots.append(make_plot(title, y_label, t, rotor_series(offset, scale),
                               bands, takeoffs, landings, x_range=top.x_range))

    k = col(3 * n)
    mask = np.zeros_like(t, dtype=bool)

    for start, stop in zip(takeoffs, landings + [t[-1]] * (len(takeoffs) - len(landings))):
        mask |= (t >= start) & (t <= stop)

    k_air = k[mask] if mask.any() else k
    scope = "en vol" if mask.any() else "tout le log"
    below = 100.0 * np.count_nonzero(k_air < 0.999) / len(k_air)

    stale = not np.any(k != 0.0)
    warning = ("<b style='color:#c62828'>K* est nul sur tout le log</b> : ce vol "
               "est anterieur au scaling de couple, le graphe K* n'a pas de sens ici.<br>"
               if stale else "")

    if stale:
        print("attention: K* identiquement nul, log anterieur au scaling de couple")

    header = Div(text=(
        f"<h2 style='margin:0 0 4px 0;font-family:sans-serif'>Allocation tilting "
        f"&mdash; {os.path.basename(args.ulog)}</h2>"
        f"<p style='margin:0 0 12px 0;color:#555;font-family:sans-serif;font-size:13px'>"
        f"{len(t)} echantillons sur {t[-1] - t[0]:.1f} s &nbsp;&middot;&nbsp; "
        f"{n} rotors &nbsp;&middot;&nbsp; K* {scope}: min "
        f"<b>{k_air.min():.4f}</b>, moyenne <b>{k_air.mean():.4f}</b>, "
        f"sous 1.0 sur <b>{below:.1f}%</b> des echantillons<br>{warning}"
        f"Molette = zoom sur le temps &middot; clic sur une entree de legende = "
        f"estomper la courbe &middot; trait vert = decollage, rouge = pos&eacute;"
        f"</p>"), sizing_mode="stretch_width")

    out = args.output or os.path.splitext(args.ulog)[0] + ".html"
    output_file(out, title=f"Allocation tilting - {os.path.basename(args.ulog)}",
                mode="cdn" if args.cdn else "inline")
    save(column(header, *plots, sizing_mode="stretch_width"))

    print(f"{len(t)} echantillons sur {t[-1] - t[0]:.1f} s")
    print(f"K* {scope}: min={k_air.min():.4f}  moyenne={k_air.mean():.4f}  "
          f"sous 1.0 sur {below:.1f}% des echantillons")
    print(f"modes de vol: {', '.join(name for _, _, name in bands) or 'inconnus'}")
    print(f"ecrit dans {out}")

    if not args.no_browser:
        webbrowser.open(f"file://{os.path.abspath(out)}")

if __name__ == "__main__":
    main()
