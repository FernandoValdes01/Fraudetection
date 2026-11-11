"""Genera las figuras del README a partir de los CSV de `resultados/`.

No necesita el dataset ni vuelve a entrenar: lee `cv_resumen.csv`, `test_resumen.csv`
y `test_repeticiones.csv`. Los diagramas se escriben como SVG; los gráficos de
resultados, como PNG. Salida en `documentacion/figuras/`.

    uv run --locked python scripts/build_figures.py
"""

import math
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "resultados"
OUT = ROOT / "documentacion" / "figuras"

INK = "#1F2A37"
MUTED = "#64748B"
BLUE = "#2E6F9E"
BLUE_LIGHT = "#E6F0F8"
GRAY = "#A8B4C0"
PANEL = "#F1F5F9"
LINE = "#CBD5E1"
AMBER = "#B45309"
AMBER_LIGHT = "#FEF3E2"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

MODEL_COLORS = {
    "knn": "#6C8EBF",
    "tree": "#7A9E7E",
    "svm": "#B08968",
    "forest": BLUE,
}
MODEL_NAMES = {
    "knn": "k-NN",
    "tree": "Árbol de decisión",
    "svm": "SVM lineal",
    "forest": "Random Forest propio",
}


# --------------------------------------------------------------------------- SVG


class Svg:
    """Constructor mínimo de SVG con las piezas que usan los diagramas."""

    def __init__(self, width: int, height: int, title: str, description: str) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.description = description
        self.parts: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(
        self,
        x: float,
        y: float,
        content: str,
        *,
        size: int = 14,
        weight: int = 400,
        fill: str = INK,
        anchor: str = "start",
        style: str = "",
    ) -> None:
        self.add(
            f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{style}>{escape(content)}</text>'
        )

    def rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        *,
        fill: str = "#FFFFFF",
        stroke: str = LINE,
        radius: int = 10,
        dash: str = "",
        stroke_width: float = 1.5,
    ) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_width}"{dash_attr}/>'
        )

    def card(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        title: str,
        lines: list[str],
        *,
        badge: str = "",
        fill: str = "#FFFFFF",
        stroke: str = LINE,
        accent: str = BLUE,
    ) -> None:
        self.rect(x, y, w, h, fill=fill, stroke=stroke)
        self.add(f'<rect x="{x}" y="{y + 10}" width="4" height="{h - 20}" rx="2" fill="{accent}"/>')
        left = x + 24
        if badge:
            self.add(f'<circle cx="{x + 28}" cy="{y + 28}" r="13" fill="{accent}"/>')
            self.text(x + 28, y + 33, badge, size=14, weight=700, fill="#FFFFFF", anchor="middle")
            left = x + 52
        self.text(left, y + 33, title, size=16, weight=700)
        for i, line in enumerate(lines):
            self.text(x + 24, y + 62 + 22 * i, line, size=13.5, fill=MUTED)

    def arrow(
        self,
        points: list[tuple[float, float]],
        *,
        color: str = MUTED,
        dash: str = "",
        head: bool = True,
    ) -> None:
        path = " ".join(f"{'M' if i == 0 else 'L'}{px} {py}" for i, (px, py) in enumerate(points))
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        marker = f'marker-end="url(#head-{color[1:]})"' if head else ""
        self.add(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" {marker}{dash_attr}/>'
        )

    def render(self) -> str:
        colors = {MUTED, AMBER, BLUE}
        markers = "".join(
            f'<marker id="head-{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
            f'markerHeight="6" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" '
            f'fill="{c}"/></marker>'
            for c in colors
        )
        body = "\n  ".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" role="img" font-family="{FONT}">\n'
            f"  <title>{escape(self.title)}</title>\n"
            f"  <desc>{escape(self.description)}</desc>\n"
            f"  <defs>{markers}</defs>\n"
            f'  <rect width="{self.width}" height="{self.height}" fill="#FFFFFF"/>\n'
            f"  {body}\n</svg>\n"
        )


def figure_protocol() -> str:
    svg = Svg(
        1230,
        730,
        "Protocolo experimental",
        "Siete etapas: limpieza, partición 70/30, muestra de búsqueda, validación cruzada de "
        "cinco pliegues, selección, reajuste con cinco semillas y evaluación en el test reservado.",
    )
    svg.text(40, 46, "Protocolo experimental", size=24, weight=700)
    svg.text(
        40,
        72,
        "El test reservado queda fuera de la búsqueda y se evalúa al fijar la configuración.",
        size=14,
        fill=MUTED,
    )

    c1, c2, c3 = 40, 440, 820
    w, h = 320, 118
    r1, r2, r3 = 105, 290, 475

    svg.card(
        c1,
        r1,
        w,
        h,
        "Dataset original",
        ["284.807 transacciones", "492 fraudes (0,173 %)", "30 predictores, sin faltantes"],
    )
    svg.card(
        c2,
        r1,
        w,
        h,
        "Limpieza",
        ["1.081 duplicados exactos eliminados", "283.726 transacciones", "473 fraudes (0,167 %)"],
        badge="1",
    )
    svg.card(
        c3,
        r1,
        w,
        h,
        "Partición 70/30",
        ["Estratificada, semilla 42", "Se aplica antes de cualquier", "ajuste o selección"],
        badge="2",
    )
    svg.card(
        c3,
        r2,
        w,
        h,
        "Entrenamiento",
        ["198.608 filas", "331 fraudes", "Única fuente de toda decisión"],
        fill=BLUE_LIGHT,
        stroke=BLUE,
    )
    svg.card(
        c2,
        r2,
        w,
        h,
        "Muestra de búsqueda",
        ["50.000 filas del entrenamiento", "83 fraudes", "Acota el costo de la rejilla"],
        badge="3",
    )
    svg.card(
        c1,
        r2,
        w,
        h,
        "Validación cruzada",
        ["5 pliegues estratificados", "8 experimentos: 4 modelos", "con y sin submuestreo 1:10"],
        badge="4",
    )
    svg.card(
        c1,
        r3,
        w,
        h,
        "Selección",
        ["Máxima sensibilidad media", "Desempate por precisión", "Ganador: Random Forest, 1:10"],
        badge="5",
    )
    svg.card(
        c2,
        r3,
        w,
        h,
        "Reajuste final",
        ["Entrenamiento completo", "5 semillas: 42, 101, 202,", "303 y 404"],
        badge="6",
    )
    svg.card(
        c3,
        r3,
        w,
        h,
        "Evaluación en test",
        ["85.118 filas, 142 fraudes", "Prevalencia original intacta", "Sin reuso para ajustar"],
        badge="7",
        fill=AMBER_LIGHT,
        stroke=AMBER,
        accent=AMBER,
    )

    mid = h / 2
    svg.arrow([(c1 + w + 4, r1 + mid), (c2 - 6, r1 + mid)])
    svg.arrow([(c2 + w + 4, r1 + mid), (c3 - 6, r1 + mid)])
    svg.arrow([(c3 + w / 2, r1 + h + 4), (c3 + w / 2, r2 - 6)])
    svg.arrow([(c3 - 4, r2 + mid), (c2 + w + 6, r2 + mid)])
    svg.arrow([(c2 - 4, r2 + mid), (c1 + w + 6, r2 + mid)])
    svg.arrow([(c1 + w / 2, r2 + h + 4), (c1 + w / 2, r3 - 6)])
    svg.arrow([(c1 + w + 4, r3 + mid), (c2 - 6, r3 + mid)])
    svg.arrow([(c2 + w + 4, r3 + mid), (c3 - 6, r3 + mid)])
    svg.arrow(
        [(c3 + w + 4, r1 + mid), (1172, r1 + mid), (1172, r3 + mid), (c3 + w + 6, r3 + mid)],
        color=AMBER,
        dash="6 5",
    )
    svg.add(
        f'<text transform="translate(1196 {r2 + mid}) rotate(-90)" font-size="12" '
        f'font-weight="600" fill="{AMBER}" text-anchor="middle">test reservado</text>'
    )

    svg.rect(40, 625, 1150, 80, fill=PANEL, stroke=PANEL)
    svg.text(64, 655, "Controles contra fuga de información", size=14, weight=700)
    svg.text(
        64,
        683,
        "Duplicados eliminados antes de partir   ·   Escalado, selección de variables y "
        "submuestreo ajustados dentro de cada pliegue   ·   Test fuera de la búsqueda",
        size=13,
        fill=MUTED,
    )
    return svg.render()


def figure_cv() -> str:
    svg = Svg(
        1200,
        580,
        "Validación cruzada estratificada de cinco pliegues",
        "La muestra de 50.000 filas se divide en cinco bloques de 10.000. En cada ronda un "
        "bloque valida y cuatro entrenan una tubería nueva.",
    )
    svg.text(40, 46, "Validación cruzada estratificada", size=24, weight=700)
    svg.text(
        40,
        72,
        "Cinco rondas sobre 50.000 filas. Cada tubería se ajusta de cero con cuatro bloques.",
        size=14,
        fill=MUTED,
    )

    x0, y0, bw, bh, gap = 150, 120, 96, 44, 8
    for fold in range(5):
        y = y0 + fold * (bh + gap)
        svg.text(x0 - 18, y + 28, f"Ronda {fold + 1}", size=14, weight=600, anchor="end")
        for block in range(5):
            x = x0 + block * (bw + gap)
            is_val = block == fold
            svg.rect(
                x,
                y,
                bw,
                bh,
                fill=AMBER_LIGHT if is_val else BLUE_LIGHT,
                stroke=AMBER if is_val else BLUE,
                radius=6,
            )
            svg.text(
                x + bw / 2,
                y + 28,
                "Validación" if is_val else "Entrena",
                size=13,
                weight=600,
                fill=AMBER if is_val else BLUE,
                anchor="middle",
            )
    svg.text(x0, y0 + 5 * (bh + gap) + 18, "Cada bloque: 10.000 filas", size=13, fill=MUTED)

    px = 770
    svg.rect(px, 120, 390, 318, fill=PANEL, stroke=PANEL, radius=12)
    svg.text(px + 24, 152, "Tubería ajustada en cada ronda", size=16, weight=700)
    steps = [
        ("Escalado z", "solo k-NN y SVM"),
        ("Submuestreo 1:10", "solo régimen compensado"),
        ("ANOVA F, 20 variables", "selección univariada"),
        ("Clasificador", "k-NN, árbol, SVM o bosque"),
    ]
    for i, (name, note) in enumerate(steps):
        y = 172 + i * 64
        svg.rect(px + 24, y, 342, 44, fill="#FFFFFF", stroke=LINE, radius=8)
        svg.text(px + 40, y + 19, name, size=14, weight=600)
        svg.text(px + 40, y + 36, note, size=12, fill=MUTED)
        if i < len(steps) - 1:
            svg.arrow([(px + 195, y + 46), (px + 195, y + 62)])

    svg.rect(40, 470, 1120, 90, fill="#FFFFFF", stroke=LINE)
    svg.text(64, 500, "Lectura del esquema", size=14, weight=700)
    svg.text(
        64,
        526,
        "Un bloque valida una vez y entrena cuatro. Ninguna transformación aprende del bloque "
        "de validación de su ronda.",
        size=13,
        fill=MUTED,
    )
    svg.text(
        64,
        547,
        "Se promedia la sensibilidad de las cinco rondas y se informa con su desviación estándar.",
        size=13,
        fill=MUTED,
    )
    return svg.render()


def figure_forest() -> str:
    svg = Svg(
        1200,
        520,
        "Random Forest propio",
        "El conjunto de entrenamiento genera T muestras bootstrap; cada una entrena un árbol de "
        "decisión con características aleatorias por división. El voto mayoritario decide, con "
        "empate a favor del fraude.",
    )
    svg.text(40, 46, "Random Forest implementado en el proyecto", size=24, weight=700)
    svg.text(
        40,
        72,
        "Bootstrap, características aleatorias por división y voto mayoritario. "
        "Sin RandomForestClassifier ni BaggingClassifier.",
        size=14,
        fill=MUTED,
    )

    svg.card(
        40, 130, 220, 150, "Entrenamiento", ["n filas, p variables", "Clases 0 y 1"], accent=BLUE
    )
    svg.arrow([(264, 205), (296, 205)], head=False)
    svg.arrow([(296, 153), (296, 393)], head=False)
    for ty in (153, 273, 393):
        svg.arrow([(296, ty), (326, ty)])

    for i, label in enumerate(("1", "2", "T")):
        y = 110 + i * 120
        if i == 2:
            svg.text(560, y - 8, "⋮", size=22, fill=MUTED, anchor="middle")
        svg.rect(330, y + 8, 190, 70, fill=PANEL, stroke=LINE, radius=8)
        svg.text(345, y + 34, f"Bootstrap {label}", size=14, weight=600)
        svg.text(345, y + 56, "n filas con reemplazo", size=12.5, fill=MUTED)
        svg.arrow([(524, y + 43), (590, y + 43)])
        svg.rect(594, y + 8, 220, 70, fill=BLUE_LIGHT, stroke=BLUE, radius=8)
        svg.text(609, y + 34, f"Árbol {label}", size=14, weight=600, fill=BLUE)
        svg.text(609, y + 56, "√p variables por división", size=12.5, fill=MUTED)
        svg.arrow([(818, y + 43), (934, y + 43)], color=BLUE)
        svg.text(876, y + 35, "voto", size=13, fill=MUTED, anchor="middle")

    svg.rect(940, 130, 220, 310, fill=AMBER_LIGHT, stroke=AMBER, radius=12)
    svg.text(1050, 168, "Voto mayoritario", size=16, weight=700, fill=AMBER, anchor="middle")
    svg.text(1050, 204, "fraude si", size=13.5, fill=INK, anchor="middle")
    svg.text(1050, 228, "votos ≥ T / 2", size=15, weight=700, anchor="middle")
    svg.text(1050, 268, "El empate se resuelve", size=13, fill=MUTED, anchor="middle")
    svg.text(1050, 288, "a favor del fraude", size=13, fill=MUTED, anchor="middle")
    svg.text(1050, 340, "Configuración elegida", size=12.5, weight=600, anchor="middle")
    svg.text(1050, 362, "T = 21 árboles", size=13, fill=MUTED, anchor="middle")
    svg.text(1050, 384, "profundidad máxima 6", size=13, fill=MUTED, anchor="middle")
    svg.text(1050, 406, "submuestreo 1:10", size=13, fill=MUTED, anchor="middle")

    svg.rect(40, 330, 220, 110, fill=PANEL, stroke=PANEL, radius=10)
    svg.text(58, 360, "Cada árbol es", size=13, weight=700)
    svg.text(58, 382, "DecisionTreeClassifier,", size=13, fill=MUTED)
    svg.text(58, 402, "con semilla propia y única", size=13, fill=MUTED)
    svg.text(58, 422, "por árbol.", size=13, fill=MUTED)
    return svg.render()


# ------------------------------------------------------------------------ gráficos


def load_results() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cv = pd.read_csv(RESULTS / "cv_resumen.csv")
    test = pd.read_csv(RESULTS / "test_resumen.csv")
    repeats = pd.read_csv(RESULTS / "test_repeticiones.csv")
    return cv, test, repeats


def style_axes(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(LINE)
    ax.tick_params(colors=MUTED, labelsize=10)
    ax.set_axisbelow(True)


def chart_validation_vs_test(test: pd.DataFrame, path: Path) -> None:
    order = [(m, c) for m in ("knn", "tree", "svm", "forest") for c in (False, True)]
    frame = test.set_index(["model", "compensated"])
    fig, ax = plt.subplots(figsize=(10, 5.6), dpi=170)
    for i, (model, comp) in enumerate(order):
        row = frame.loc[(model, comp)]
        y = len(order) - 1 - i
        ax.plot(
            [row.sensitivity_mean, row.cv_sensitivity_mean],
            [y, y],
            color=LINE,
            lw=3,
            zorder=1,
        )
        ax.errorbar(
            row.cv_sensitivity_mean,
            y,
            xerr=row.cv_sensitivity_std,
            fmt="o",
            color=GRAY,
            ecolor=GRAY,
            capsize=3,
            ms=9,
            zorder=2,
            label="Validación cruzada (media ± DE)" if i == 0 else None,
        )
        ax.scatter(
            row.sensitivity_mean,
            y,
            marker="D",
            s=70,
            color=MODEL_COLORS[model],
            zorder=3,
            label="Prueba (media de 5 semillas)" if i == 0 else None,
        )
        ax.text(
            row.cv_sensitivity_mean,
            y + 0.2,
            f"{row.cv_sensitivity_mean * 100:.1f}".replace(".", ","),
            fontsize=9,
            color=MUTED,
            ha="center",
            va="bottom",
        )
        ax.text(
            row.sensitivity_mean,
            y - 0.34,
            f"{row.sensitivity_mean * 100:.1f}".replace(".", ","),
            fontsize=9,
            color=INK,
            ha="center",
            weight="bold" if row.selected_by_cv else "normal",
        )
    labels = [
        f"{MODEL_NAMES[m]}\n{'submuestreo 1:10' if c else 'sin compensación'}" for m, c in order
    ]
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(labels[::-1], fontsize=9.5, color=INK)
    ax.set_xlim(0.40, 1.02)
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_xlabel("Sensibilidad (recall de fraude)", color=MUTED, fontsize=10.5)
    ax.xaxis.set_major_formatter(lambda v, _: f"{v * 100:.0f} %")
    ax.grid(axis="x", color="#EEF2F6")
    style_axes(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False, fontsize=9.5)
    ax.set_title(
        "Sensibilidad en validación y en prueba",
        loc="left",
        fontsize=14,
        color=INK,
        weight="bold",
        pad=26,
    )
    ax.text(
        0,
        1.025,
        "El modelo seleccionado en validación pierde 7,5 pp al pasar al test reservado.",
        transform=ax.transAxes,
        fontsize=10,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def chart_tradeoff(test: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.6, 6.4), dpi=170)
    grid = np.linspace(0.01, 1, 400)
    for f1 in (0.4, 0.6, 0.8):
        valid = grid > f1 / 2
        recall = f1 * grid[valid] / (2 * grid[valid] - f1)
        ax.plot(grid[valid], recall, color="#E2E8F0", lw=1, ls="--", zorder=0)
        label_x = f1 * 0.885 / (2 * 0.885 - f1)
        ax.text(
            label_x,
            0.89,
            f"F1 = {f1:.1f}".replace(".", ","),
            fontsize=8.5,
            color=GRAY,
            ha="center",
            va="center",
            bbox=dict(fc="white", ec="none", pad=1.5),
        )

    frame = test.set_index(["model", "compensated"])
    for model in ("knn", "tree", "svm", "forest"):
        a = frame.loc[(model, False)]
        b = frame.loc[(model, True)]
        color = MODEL_COLORS[model]
        ax.annotate(
            "",
            xy=(b.precision_mean, b.sensitivity_mean),
            xytext=(a.precision_mean, a.sensitivity_mean),
            arrowprops=dict(arrowstyle="->", color=color, lw=1.4, alpha=0.7),
            zorder=1,
        )
        ax.scatter(
            a.precision_mean,
            a.sensitivity_mean,
            s=95,
            facecolor="white",
            edgecolor=color,
            lw=2,
            zorder=3,
        )
        ax.scatter(
            b.precision_mean,
            b.sensitivity_mean,
            s=95,
            color=color,
            zorder=3,
            label=MODEL_NAMES[model],
        )
    sel = frame.loc[("forest", True)]
    ax.scatter(
        sel.precision_mean,
        sel.sensitivity_mean,
        s=330,
        facecolor="none",
        edgecolor=AMBER,
        lw=2,
        zorder=4,
    )
    ax.annotate(
        "Seleccionado por validación",
        xy=(sel.precision_mean, sel.sensitivity_mean),
        xytext=(0.47, 0.855),
        fontsize=9.5,
        color=AMBER,
        arrowprops=dict(arrowstyle="-", color=AMBER, lw=1),
    )
    ax.set_xlim(0.2, 1.0)
    ax.set_ylim(0.45, 0.9)
    ax.set_xlabel("Precisión (fraudes reales entre las alertas)", color=MUTED, fontsize=10.5)
    ax.set_ylabel("Sensibilidad (fraudes detectados)", color=MUTED, fontsize=10.5)
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(lambda v, _: f"{v * 100:.0f} %")
    ax.grid(color="#EEF2F6")
    style_axes(ax)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="lower left",
        frameon=False,
        fontsize=9.5,
        title="Modelo",
        title_fontsize=9.5,
    )
    ax.set_title(
        "Costo de compensar el desbalance",
        loc="left",
        fontsize=14,
        color=INK,
        weight="bold",
        pad=26,
    )
    ax.text(
        0,
        1.025,
        "Círculo vacío: sin compensación. Círculo lleno: submuestreo 1:10. Datos de prueba.",
        transform=ax.transAxes,
        fontsize=10,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


def wilson(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return center - half, center + half


def chart_confusion(repeats: pd.DataFrame, path: Path) -> tuple[float, float]:
    row = repeats[(repeats.experiment == "forest_submuestreo") & (repeats.seed == 42)].iloc[0]
    tn, fp, fn, tp = (int(row[c]) for c in ("tn", "fp", "fn", "tp"))
    counts = np.array([[tn, fp], [fn, tp]])
    rates = counts / counts.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(6.4, 5.6), dpi=170)
    ax.imshow(rates, cmap="Blues", vmin=0, vmax=1.15)
    for i in range(2):
        for j in range(2):
            dark = rates[i, j] > 0.55
            ax.text(
                j,
                i - 0.08,
                f"{counts[i, j]:,}".replace(",", "."),
                ha="center",
                va="center",
                fontsize=17,
                weight="bold",
                color="white" if dark else INK,
            )
            ax.text(
                j,
                i + 0.18,
                f"{rates[i, j] * 100:.1f} %".replace(".", ","),
                ha="center",
                va="center",
                fontsize=10.5,
                color="white" if dark else MUTED,
            )
    ax.set_xticks([0, 1], ["Legítima", "Fraude"], fontsize=11, color=INK)
    ax.set_yticks([0, 1], ["Legítima", "Fraude"], fontsize=11, color=INK, rotation=90, va="center")
    ax.set_xlabel("Predicción", color=MUTED, fontsize=10.5, labelpad=8)
    ax.set_ylabel("Clase real", color=MUTED, fontsize=10.5, labelpad=8)
    ax.xaxis.set_label_position("bottom")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    low, high = wilson(tp, tp + fn)
    ax.set_title(
        "Random Forest propio, submuestreo 1:10",
        loc="left",
        fontsize=13,
        color=INK,
        weight="bold",
        pad=34,
    )
    ax.text(
        0,
        1.045,
        "Test reservado, semilla 42. "
        + f"Sensibilidad {tp / (tp + fn) * 100:.1f} % "
        f"(IC 95 % de Wilson: {low * 100:.1f} a {high * 100:.1f} %)".replace(".", ","),
        transform=ax.transAxes,
        fontsize=9.5,
        color=MUTED,
    )
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return low, high


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, build in (
        ("protocolo.svg", figure_protocol),
        ("validacion_cruzada.svg", figure_cv),
        ("random_forest.svg", figure_forest),
    ):
        (OUT / name).write_text(build(), encoding="utf-8")
    cv, test, repeats = load_results()
    del cv
    chart_validation_vs_test(test, OUT / "validacion_vs_prueba.png")
    chart_tradeoff(test, OUT / "sensibilidad_vs_precision.png")
    low, high = chart_confusion(repeats, OUT / "matriz_confusion.png")
    print(f"Figuras en {OUT.relative_to(ROOT)} (IC 95 % sensibilidad: {low:.3f} a {high:.3f})")


if __name__ == "__main__":
    main()
