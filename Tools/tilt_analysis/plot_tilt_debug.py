#!/usr/bin/env python3
import argparse
import sys

import numpy as np
from pyulog import ULog

ROTOR_COLORS = ["#4269d0", "#efb118", "#ff725c", "#6cc5b0", "#3ca951", "#a463f2"]

def load(path, topic):
    try:
        ulog = ULog(path, [topic])
    except Exception as exc:
        print(f"erreur de lecture de {path}: {exc}", file=sys.stderr)
        sys.exit(1)

    return ulog.data_list[0] if ulog.data_list else None

def airborne_intervals(path, t0):
    land = load(path, "vehicle_land_detected")

    if land is None or "landed" not in land.data:
        return []

    t = (land.data["timestamp"].astype(np.int64) - np.int64(t0)) / 1e6
    flag = ~land.data["landed"].astype(bool)
    edges = np.diff(flag.astype(np.int8))
    starts = list(t[1:][edges == 1])
    stops = list(t[1:][edges == -1])

    if flag[0]:
        starts.insert(0, t[0])

    if len(stops) < len(starts):
        stops.append(t[-1])

    return list(zip(starts, stops))

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ulog", help="chemin du fichier .ulg")
    ap.add_argument("-o", "--output", help="enregistre en PNG au lieu d'afficher")
    ap.add_argument("-n", "--rotors", type=int, default=6, help="nombre de rotors (defaut 6)")
    ap.add_argument("--airborne-only", action="store_true",
                    help="limite l'axe temps a la phase en vol")
    args = ap.parse_args()

    if args.output:
        import matplotlib
        matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    dbg = load(args.ulog, "debug_array")

    if dbg is None:
        print("debug_array absent de ce log: le control allocator n'a rien publie, "
              "ou le topic n'est pas enregistre.", file=sys.stderr)
        sys.exit(1)

    n = args.rotors
    t0 = dbg.data["timestamp"][0]
    t = (dbg.data["timestamp"] - t0) / 1e6

    def col(j):
        return dbg.data[f"data[{j}]"]

    vert = [col(3 * i) for i in range(n)]
    lat = [col(3 * i + 1) for i in range(n)]
    servo = [np.degrees(col(3 * i + 2)) for i in range(n)]
    k = col(3 * n)

    fig, axes = plt.subplots(4, 1, figsize=(14, 11), sharex=True)
    fig.suptitle(f"Allocation tilting — {args.ulog}", fontsize=13)

    ax = axes[0]
    ax.plot(t, k, color="#c73e3e", lw=0.9)
    ax.axhline(1.0, color="grey", ls="--", lw=0.8)
    ax.set_ylabel("torque_scale K*")
    ax.set_ylim(-0.05, 1.15)
    ax.set_title("K* < 1 : couple sacrifie pour eviter une poussee verticale negative",
                 fontsize=9, loc="left", color="#555")

    ax = axes[1]
    for i in range(n):
        ax.plot(t, vert[i], lw=0.8, color=ROTOR_COLORS[i % len(ROTOR_COLORS)], label=f"rotor {i+1}")
    ax.axhline(0.0, color="grey", ls="--", lw=0.8)
    ax.set_ylabel("composante verticale")
    ax.legend(ncol=n, fontsize=8, loc="upper right")

    ax = axes[2]
    for i in range(n):
        ax.plot(t, lat[i], lw=0.8, color=ROTOR_COLORS[i % len(ROTOR_COLORS)])
    ax.axhline(0.0, color="grey", ls="--", lw=0.8)
    ax.set_ylabel("composante laterale")

    ax = axes[3]
    for i in range(n):
        ax.plot(t, servo[i], lw=0.8, color=ROTOR_COLORS[i % len(ROTOR_COLORS)])
    ax.set_ylabel("consigne servo [deg]")
    ax.set_xlabel("temps depuis debut du log [s]")

    spans = airborne_intervals(args.ulog, t0)

    for ax in axes:
        ax.grid(alpha=0.25, lw=0.5)

        for start, stop in spans:
            ax.axvspan(start, stop, color="#2e7d32", alpha=0.08, lw=0)

    if args.airborne_only and spans:
        axes[0].set_xlim(min(s for s, _ in spans), max(e for _, e in spans))
    else:
        axes[0].set_xlim(t[0], t[-1])

    fig.tight_layout(rect=(0, 0, 1, 0.97))

    print(f"{len(t)} echantillons sur {t[-1] - t[0]:.1f} s")

    mask = np.zeros_like(t, dtype=bool)

    for start, stop in spans:
        mask |= (t >= start) & (t <= stop)

    if mask.any():
        k_air = k[mask]
        label = "en vol"
    else:
        k_air = k
        label = "tout le log (phase de vol non identifiee)"

    below = np.count_nonzero(k_air < 0.999)
    print(f"K* {label}: min={k_air.min():.4f}  moyenne={k_air.mean():.4f}  "
          f"sous 1.0 sur {100.0 * below / len(k_air):.1f}% des echantillons")

    if args.output:
        fig.savefig(args.output, dpi=130)
        print(f"ecrit dans {args.output}")
    else:
        plt.show()

if __name__ == "__main__":
    main()
