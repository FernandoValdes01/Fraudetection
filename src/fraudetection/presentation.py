"""Genera gráficos y una presentación PowerPoint desde los resultados guardados."""

import argparse
import json
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from sklearn.metrics import confusion_matrix

from fraudetection.config import FINAL_SEEDS, SEARCH_SAMPLE_SIZE
from fraudetection.data import (
    inspect_dataset,
    load_dataset,
    remove_exact_duplicates,
    split_dataset,
)
from fraudetection.experiments import MODEL_LABELS, save_plots, sha256

BG = RGBColor(255, 255, 255)
PANEL = RGBColor(241, 245, 249)
TEXT = RGBColor(38, 50, 56)
MUTED = RGBColor(100, 116, 139)
BLUE = RGBColor(46, 111, 158)
ORANGE = RGBColor(168, 180, 192)
TEAL = RGBColor(46, 111, 158)
FONT = "Arial"


def add_text(
    slide,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    size: float = 18,
    color: RGBColor = TEXT,
    bold: bool = False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.02)
    frame.margin_right = Inches(0.02)
    frame.margin_top = Inches(0.02)
    frame.margin_bottom = Inches(0.02)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    paragraph.space_after = Pt(0)
    run = paragraph.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_background(slide):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    shape.fill.solid()
    shape.fill.fore_color.rgb = BG
    shape.line.fill.background()
    slide.shapes._spTree.remove(shape._element)
    slide.shapes._spTree.insert(2, shape._element)


def new_slide(prs: Presentation, title: str, section: str, number: int, *, subtitle: str = ""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_text(slide, section.upper(), 0.55, 0.28, 6.0, 0.28, size=10, color=TEAL, bold=True)
    add_text(slide, title, 0.55, 0.68, 12.1, 0.5, size=26, bold=True)
    if subtitle:
        add_text(slide, subtitle, 0.58, 1.25, 12.0, 0.38, size=12, color=MUTED)
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.18), Inches(12.2), Inches(0.018)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = PANEL
    line.line.fill.background()
    add_text(
        slide,
        "INFO1185 · Detección de fraude",
        0.55,
        7.12,
        8.0,
        0.2,
        size=9,
        color=MUTED,
    )
    add_text(
        slide,
        f"{number:02d}",
        12.1,
        7.08,
        0.6,
        0.26,
        size=10,
        color=MUTED,
        align=PP_ALIGN.RIGHT,
    )
    return slide


def add_card(slide, x, y, width, height, value, label, *, color=TEAL, detail=""):
    card = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height),
    )
    card.fill.solid()
    card.fill.fore_color.rgb = PANEL
    card.line.fill.background()
    add_text(
        slide,
        value,
        x + 0.2,
        y + 0.2,
        width - 0.4,
        0.48,
        size=25,
        color=color,
        bold=True,
    )
    add_text(
        slide,
        label,
        x + 0.2,
        y + 0.78,
        width - 0.4,
        0.34,
        size=12,
        color=TEXT,
        bold=True,
    )
    if detail:
        add_text(
            slide,
            detail,
            x + 0.2,
            y + 1.18,
            width - 0.4,
            height - 1.3,
            size=10,
            color=MUTED,
        )


def add_bullets(slide, items, x, y, width, *, line_height=0.72, size=16):
    for index, item in enumerate(items):
        top = y + index * line_height
        dot = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(x), Inches(top + 0.12), Inches(0.11), Inches(0.11)
        )
        dot.fill.solid()
        dot.fill.fore_color.rgb = ORANGE if index == 0 else TEAL
        dot.line.fill.background()
        add_text(slide, item, x + 0.26, top, width - 0.26, line_height - 0.04, size=size)


def add_image(slide, path: Path, x, y, width, height=None):
    if height is None:
        slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(width))
    else:
        slide.shapes.add_picture(
            str(path), Inches(x), Inches(y), width=Inches(width), height=Inches(height)
        )


def fmt(value, digits=1):
    return f"{100 * float(value):.{digits}f}%"


def metric_with_std(row, name):
    digits = 3 if name == "specificity" else 2 if name == "accuracy" else 1
    return (
        f"{100 * float(row[f'{name}_mean']):.{digits}f}% ± "
        f"{100 * float(row[f'{name}_std']):.{digits}f} pp"
    )


def add_table(slide, headers, rows, x, y, width, height, *, font_size=12, widths=None):
    table_shape = slide.shapes.add_table(
        len(rows) + 1,
        len(headers),
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height),
    )
    table = table_shape.table
    if widths:
        for index, cell_width in enumerate(widths):
            table.columns[index].width = Inches(cell_width)
    for row_index, values in enumerate([headers, *rows]):
        for column_index, value in enumerate(values):
            cell = table.cell(row_index, column_index)
            cell.text = str(value)
            cell.margin_left = Inches(0.06)
            cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.025)
            cell.margin_bottom = Inches(0.025)
            cell.fill.solid()
            cell.fill.fore_color.rgb = PANEL if row_index else RGBColor(220, 232, 241)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.LEFT
                for run in paragraph.runs:
                    run.font.name = FONT
                    run.font.size = Pt(font_size)
                    run.font.bold = row_index == 0
                    run.font.color.rgb = TEXT if row_index == 0 else MUTED
    return table_shape


def create_deck(cv, test, results_dir: Path, deck_path: Path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    prs.core_properties.title = "Detección de fraude con aprendizaje supervisado"
    prs.core_properties.subject = "INFO1185 · Problema 2"
    prs.core_properties.author = "Equipo INFO1185"
    plots = results_dir / "graficos"
    selected = cv.loc[cv["selected_by_cv"]].iloc[0]
    chosen_result = test.loc[test["experiment"] == selected["experiment"]].iloc[0]
    selected_label = MODEL_LABELS[selected["model"]]
    raw_test = pd.read_csv(results_dir / "predicciones_configuracion_cv.csv")
    tn, fp, fn, tp = confusion_matrix(
        raw_test["class_true"], raw_test["class_predicted"], labels=[0, 1]
    ).ravel()

    # 1. Portada
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide)
    add_text(
        slide,
        "INFO1185 · INTELIGENCIA ARTIFICIAL",
        0.8,
        0.65,
        7.5,
        0.3,
        size=11,
        color=TEAL,
        bold=True,
    )
    add_text(slide, "Detección\nde fraude", 0.8, 1.45, 8.5, 1.8, size=38, bold=True)
    add_text(
        slide,
        "Comparación de clasificadores supervisados",
        0.85,
        3.55,
        8.0,
        0.55,
        size=20,
        color=MUTED,
    )
    add_text(
        slide,
        "Prioridad: detectar fraudes y reducir falsos negativos",
        0.85,
        4.35,
        8.5,
        0.5,
        size=17,
        color=ORANGE,
        bold=True,
    )
    add_text(
        slide,
        "Integrantes: Fernando Valdés Gomez · Juan Muñoz Veloso",
        0.85,
        6.35,
        7.0,
        0.35,
        size=13,
        color=MUTED,
    )
    add_card(slide, 9.6, 1.5, 2.8, 1.7, "4", "clasificadores", color=TEAL)
    add_card(slide, 9.6, 3.5, 2.8, 1.7, "8", "condiciones", color=ORANGE)
    add_text(
        slide,
        "k-NN · árbol · SVM · Random Forest propio",
        8.8,
        5.7,
        3.8,
        0.7,
        size=12,
        color=MUTED,
        align=PP_ALIGN.CENTER,
    )

    # 2. Dataset
    slide = new_slide(prs, "El fraude es poco frecuente", "01 · Datos", 2)
    add_image(slide, plots / "distribucion_clases.png", 0.55, 1.65, 7.0, 4.4)
    add_card(slide, 8.0, 1.8, 2.0, 1.75, "284.807", "transacciones", color=BLUE)
    add_card(slide, 10.25, 1.8, 2.0, 1.75, "492", "fraudes · 0,173 %", color=ORANGE)
    add_card(slide, 8.0, 3.9, 2.0, 1.75, "1.081", "duplicados exactos", color=ORANGE)
    add_card(slide, 10.25, 3.9, 2.0, 1.75, "0", "valores faltantes", color=TEAL)
    add_text(
        slide,
        "Se quitaron duplicados antes de separar los datos. Quedaron 283.726 filas y 473 fraudes.",
        8.05,
        6.0,
        4.1,
        0.65,
        size=12,
        color=MUTED,
    )

    # 3. Data split and leakage prevention
    slide = new_slide(prs, "Partición fija y prueba reservada", "02 · Diseño", 3)
    add_card(slide, 0.7, 1.75, 3.2, 1.75, "198.608", "entrenamiento completo", color=BLUE)
    add_card(
        slide,
        4.15,
        1.75,
        3.2,
        1.75,
        "50.000",
        "submuestra estratificada para búsqueda",
        color=TEAL,
    )
    add_card(slide, 7.6, 1.75, 3.2, 1.75, "85.118", "prueba reservada", color=ORANGE)
    add_bullets(
        slide,
        [
            (
                "Partición estratificada 70/30, semilla 42; los ocho experimentos comparten la "
                "misma partición."
            ),
            "Cinco pliegues estratificados y compartidos para comparar los modelos.",
            "Tras la búsqueda, cada ganador se reajusta con todo el entrenamiento.",
            "El test conserva la prevalencia natural y no participa en ajustes.",
        ],
        0.9,
        4.0,
        11.4,
        line_height=0.58,
        size=14,
    )

    # 4. Models and pipeline
    slide = new_slide(prs, "Ocho experimentos, una misma validación", "03 · Método", 4)
    add_table(
        slide,
        ["Modelo", "Sin compensación", "Con submuestreo"],
        [[MODEL_LABELS[name], "✓", "✓"] for name in ("knn", "tree", "svm", "forest")],
        0.7,
        1.7,
        6.0,
        3.1,
        font_size=14,
        widths=[3.2, 1.4, 1.4],
    )
    add_text(
        slide,
        "Dentro de cada pliegue",
        7.35,
        1.75,
        4.5,
        0.35,
        size=17,
        color=TEAL,
        bold=True,
    )
    add_bullets(
        slide,
        [
            "Escalado para k-NN y SVM.",
            "ANOVA F-test: se seleccionan las 20 mejores variables.",
            "RandomUnderSampler 1:10 solo en entrenamiento.",
            "Validación y prueba mantienen su distribución original.",
        ],
        7.35,
        2.3,
        5.0,
        line_height=0.72,
        size=14,
    )

    # 5. Custom random forest
    slide = new_slide(prs, "Random Forest implementado por la dupla", "04 · Ensamble", 5)
    steps = [
        ("01", "Bootstrap", "n extracciones con reemplazo"),
        ("02", "Árbol independiente", "max_features = √p por división"),
        ("03", "Votación", "mayoría; empate a favor del fraude"),
    ]
    for index, (number, heading, detail) in enumerate(steps):
        x = 0.75 + index * 4.15
        add_card(
            slide,
            x,
            2.0,
            3.55,
            2.0,
            number,
            heading,
            color=ORANGE if index == 2 else TEAL,
            detail=detail,
        )
        if index < 2:
            add_text(
                slide,
                "→",
                x + 3.65,
                2.65,
                0.4,
                0.5,
                size=24,
                color=MUTED,
                align=PP_ALIGN.CENTER,
            )
    forest_cv = cv.loc[cv["experiment"] == "forest_submuestreo"].iloc[0]
    add_text(
        slide,
        f"Configuración elegida en CV: {forest_cv['best_parameters']}",
        0.8,
        4.65,
        11.5,
        0.45,
        size=17,
        color=TEXT,
        bold=True,
    )
    add_text(
        slide,
        (
            "Las semillas de árboles derivan de una semilla general y son distintas entre sí. El "
            "código no usa RandomForestClassifier ni BaggingClassifier."
        ),
        0.8,
        5.35,
        11.5,
        0.8,
        size=14,
        color=MUTED,
    )

    # 6. Search
    slide = new_slide(prs, "Selección por sensibilidad y precisión", "05 · Ajuste", 6)
    add_card(slide, 0.8, 1.8, 3.2, 1.7, "5", "pliegues estratificados", color=TEAL)
    add_card(
        slide,
        4.15,
        1.8,
        3.2,
        1.7,
        "50.000",
        "filas de entrenamiento para CV",
        color=BLUE,
    )
    add_card(
        slide,
        7.5,
        1.8,
        3.2,
        1.7,
        "20 / 30",
        "variables conservadas por ANOVA",
        color=ORANGE,
    )
    add_bullets(
        slide,
        [
            "Primero se maximiza la sensibilidad media de Class = 1.",
            "Si empatan, se elige la configuración con mayor precisión media del fraude.",
            (
                f"Elegida: {selected_label} con {selected['compensation']}, sensibilidad "
                f"{fmt(selected['cv_sensitivity_mean'])} ± {fmt(selected['cv_sensitivity_std'])} "
                f"y precisión {fmt(selected['cv_precision_mean'])} en CV."
            ),
            (
                "Los hiperparámetros finales se ajustan de nuevo con las 198.608 filas de "
                "entrenamiento."
            ),
        ],
        0.9,
        4.0,
        11.4,
        line_height=0.62,
        size=14,
    )

    # 7. CV chart
    slide = new_slide(prs, "La compensación eleva la sensibilidad en CV", "06 · Validación", 7)
    add_image(slide, plots / "sensibilidad_validacion.png", 0.9, 1.65, 11.6, 4.7)
    add_text(
        slide,
        "Barras: media de cinco pliegues. Líneas: una desviación estándar entre pliegues.",
        1.0,
        6.42,
        11.0,
        0.3,
        size=11,
        color=MUTED,
    )

    # 8. Test sensitivity/FNR
    slide = new_slide(
        prs, "Prueba reservada: sensibilidad y falsos negativos", "07 · Resultados", 8
    )
    add_image(slide, plots / "sensibilidad_fnr_prueba.png", 0.75, 1.55, 11.8, 4.9)
    add_text(
        slide,
        (
            "Media ± desviación estándar entre cinco semillas; el mismo test se usa en todas las "
            "repeticiones."
        ),
        0.9,
        6.55,
        11.5,
        0.28,
        size=11,
        color=MUTED,
    )

    # 9. Test precision/specificity
    slide = new_slide(prs, "Detectar más fraudes genera más alertas", "08 · Costos", 9)
    add_image(slide, plots / "precision_especificidad_prueba.png", 0.75, 1.55, 11.8, 4.9)
    add_text(
        slide,
        (
            "El submuestreo mejora la sensibilidad, pero reduce la precisión: una mayor "
            "proporción de alertas es falsa."
        ),
        0.9,
        6.55,
        11.5,
        0.3,
        size=12,
        color=MUTED,
    )

    # 10. Confusion matrix
    slide = new_slide(prs, "Matriz de confusión de la configuración elegida", "09 · Prueba", 10)
    add_image(slide, plots / "matriz_confusion_seleccion_cv.png", 1.0, 1.55, 5.5, 4.6)
    add_card(slide, 7.0, 1.8, 2.1, 1.6, f"{tp}", "fraudes detectados", color=TEAL)
    add_card(slide, 9.45, 1.8, 2.1, 1.6, f"{fn}", "fraudes omitidos", color=ORANGE)
    add_card(slide, 7.0, 3.75, 2.1, 1.6, f"{fp:,}", "falsas alarmas", color=ORANGE)
    add_card(slide, 9.45, 3.75, 2.1, 1.6, f"{tn:,}", "legítimas reconocidas", color=TEAL)
    add_text(
        slide,
        (
            f"{selected_label} · {selected['compensation']} · semilla 42. La selección se hizo "
            f"con CV; la matriz usa el primer ajuste en test."
        ),
        7.0,
        5.8,
        4.7,
        0.75,
        size=12,
        color=MUTED,
    )

    # 11. Critical analysis
    slide = new_slide(prs, "Lectura crítica de los resultados", "10 · Análisis", 11)
    baseline_accuracy = 100 * (1 - y_true_fraud_count(raw_test) / len(raw_test))
    forest_plain = test.loc[test["experiment"] == "forest_sin_compensacion"].iloc[0]
    forest_balanced = test.loc[test["experiment"] == "forest_submuestreo"].iloc[0]
    add_card(
        slide,
        0.8,
        1.75,
        3.4,
        1.85,
        f"{baseline_accuracy:.3f}%",
        "exactitud si todo se predice legítimo",
        color=ORANGE,
        detail="Sensibilidad: 0 %. FNR: 100 %.",
    )
    add_card(
        slide,
        4.65,
        1.75,
        3.4,
        1.85,
        f"{fmt(forest_plain['sensitivity_mean'])} → {fmt(forest_balanced['sensitivity_mean'])}",
        "sensibilidad del bosque",
        color=TEAL,
        detail="Sin compensación → con submuestreo.",
    )
    add_card(
        slide,
        8.5,
        1.75,
        3.4,
        1.85,
        f"{fmt(forest_balanced['precision_mean'])}",
        "precisión del bosque compensado",
        color=ORANGE,
        detail="La parte restante de alertas son falsas alarmas.",
    )
    add_bullets(
        slide,
        [
            "La exactitud sola oculta los fraudes que el modelo deja pasar.",
            (
                "Clasificar todo como fraude daría sensibilidad 100 %, pero marcaría como falsas "
                "alarmas las 84.976 transacciones legítimas del test."
            ),
            (
                "El bosque con submuestreo detecta algo menos que el árbol compensado, pero "
                "eleva la precisión de 0,336 a 0,675."
            ),
        ],
        0.9,
        4.35,
        11.7,
        line_height=0.68,
        size=14,
    )

    # 12. Conclusions
    slide = new_slide(prs, "Conclusiones y límites", "11 · Cierre", 12)
    add_card(
        slide,
        0.8,
        1.8,
        3.4,
        1.8,
        fmt(chosen_result["sensitivity_mean"]),
        "sensibilidad en prueba",
        color=TEAL,
        detail=(
            f"FNR {fmt(chosen_result['fnr_mean'])} · precisión "
            f"{fmt(chosen_result['precision_mean'])}"
        ),
    )
    add_bullets(
        slide,
        [
            f"CV eligió {selected_label} con submuestreo por obtener la mayor sensibilidad media.",
            "El submuestreo aumentó la detección de fraudes y también produjo más falsas alarmas.",
            (
                "El test contiene solo 142 fraudes; las métricas de sensibilidad cambian con "
                "pocos casos."
            ),
            (
                "El dataset no trae identificador de transacción; algunas filas idénticas "
                "podrían ser operaciones reales repetidas."
            ),
            (
                "SVM lineal y ANOVA son decisiones acotadas para esta comparación; se podrían "
                "ampliar los espacios de búsqueda."
            ),
        ],
        4.65,
        1.8,
        7.8,
        line_height=0.82,
        size=14,
    )
    add_text(
        slide,
        (
            "Siguiente paso: ambos integrantes deben poder explicar la implementación, las "
            "métricas y el costo operativo de las falsas alarmas."
        ),
        0.85,
        6.25,
        11.5,
        0.42,
        size=13,
        color=MUTED,
    )

    # Backup. Exact CV winners and metrics for all eight experiments.
    slide = new_slide(
        prs,
        "Configuraciones y resultados de validación",
        "Respaldo · Validación",
        13,
        subtitle="Cinco pliegues compartidos · sensibilidad y precisión de fraude",
    )
    cv_rows = []
    for _, row in cv.iterrows():
        parameters = json.loads(row["best_parameters"])
        parameter_text = ", ".join(f"{key}={value}" for key, value in parameters.items())
        label = row["model_label"]
        if row["selected_by_cv"]:
            label = f"✓ {label}"
        cv_rows.append(
            [
                label,
                "submuestreo" if row["compensated"] else "sin compensación",
                parameter_text,
                f"{fmt(row['cv_sensitivity_mean'])} ± {fmt(row['cv_sensitivity_std'])}",
                fmt(row["cv_precision_mean"]),
            ]
        )
    add_table(
        slide,
        ["Modelo", "Condición", "Mejores parámetros", "Sensibilidad ± DE", "Precisión"],
        cv_rows,
        0.45,
        1.8,
        12.45,
        4.5,
        font_size=10,
        widths=[2.0, 1.7, 3.5, 2.7, 2.1],
    )
    add_text(
        slide,
        (
            "Rangos evaluados: k-NN n_neighbors={3, 5, 7}; árbol max_depth={5, 10, None} y "
            "min_samples_leaf={1, 5}; SVM C={0.1, 1, 10}; bosque n_estimators={11, 21} y "
            "max_depth={6, 12}. El bosque usa max_features=√p."
        ),
        0.6,
        6.38,
        12.0,
        0.47,
        size=9,
        color=MUTED,
    )

    # Backup. Full metric table required by the assignment.
    slide = new_slide(
        prs,
        "Resultados completos de prueba",
        "Respaldo · Métricas",
        14,
        subtitle=(
            "Media ± desviación estándar entre semillas; resultados de CV y prueba se reportan "
            "por separado."
        ),
    )
    rows = []
    for _, row in test.iterrows():
        rows.append(
            [
                row["model_label"],
                "submuestreo" if row["compensated"] else "sin comp.",
                metric_with_std(row, "sensitivity"),
                metric_with_std(row, "specificity"),
                metric_with_std(row, "precision"),
                metric_with_std(row, "f1"),
                metric_with_std(row, "accuracy"),
                metric_with_std(row, "fnr"),
            ]
        )
    add_table(
        slide,
        [
            "Modelo",
            "Condición",
            "Sensibilidad",
            "Especificidad",
            "Precisión",
            "F1",
            "Exactitud",
            "FNR",
        ],
        rows,
        0.45,
        1.8,
        12.45,
        4.25,
        font_size=8.5,
        widths=[2.0, 1.35, 1.55, 1.6, 1.45, 1.3, 1.45, 1.25],
    )
    add_text(
        slide,
        (
            "Las desviaciones reflejan cinco semillas sobre el mismo test fijo; no son cinco "
            "muestras independientes."
        ),
        0.6,
        6.25,
        11.5,
        0.35,
        size=10,
        color=MUTED,
    )

    deck_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(deck_path)
    return selected, chosen_result


def y_true_fraud_count(frame: pd.DataFrame) -> int:
    return int((frame["class_true"] == 1).sum())


def build_report(dataset: Path, results_dir: Path, deck_path: Path):
    raw = load_dataset(dataset)
    raw_report = inspect_dataset(raw)
    clean = remove_exact_duplicates(raw)
    clean_report = inspect_dataset(clean)
    _, X_test, _, _ = split_dataset(clean)
    cv = pd.read_csv(results_dir / "cv_resumen.csv")
    test = pd.read_csv(results_dir / "test_resumen.csv")
    test["compensated"] = test["compensation"] != "ninguna"
    prediction_frame = pd.read_csv(results_dir / "predicciones_configuracion_cv.csv")
    selected = str(cv.loc[cv["selected_by_cv"], "experiment"].iloc[0])
    predictions = {selected: prediction_frame["class_predicted"].to_numpy()}
    save_plots(
        raw_report,
        clean_report,
        cv,
        test,
        pd.Series(prediction_frame["class_true"].to_numpy()),
        predictions,
        results_dir,
    )
    selected_row, selected_test = create_deck(cv, test, results_dir, deck_path)
    metadata = {
        "dataset": str(dataset),
        "dataset_sha256": sha256(dataset),
        "rows_raw": raw_report.records,
        "duplicates_removed": raw_report.duplicate_rows,
        "rows_after_cleaning": clean_report.records,
        "train_rows": len(clean) - len(X_test),
        "test_rows": len(X_test),
        "search_sample_rows": SEARCH_SAMPLE_SIZE,
        "cv_folds": 5,
        "final_seeds": list(FINAL_SEEDS),
        "selected_by_cv": str(selected_row["experiment"]),
        "selected_test_sensitivity_mean": float(selected_test["sensitivity_mean"]),
        "selected_test_fnr_mean": float(selected_test["fnr_mean"]),
    }
    (results_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera gráficos y PowerPoint desde resultados guardados"
    )
    parser.add_argument("--dataset", type=Path, default=Path("data/raw/creditcard.csv"))
    parser.add_argument("--results-dir", type=Path, default=Path("resultados"))
    parser.add_argument(
        "--deck",
        type=Path,
        default=Path("documentacion/presentacion/defensa_fraude.pptx"),
    )
    args = parser.parse_args()
    metadata = build_report(args.dataset, args.results_dir, args.deck)
    print("Presentación guardada en", args.deck)
    print("Configuración seleccionada en CV:", metadata["selected_by_cv"])
    print(
        f"Sensibilidad en prueba: {metadata['selected_test_sensitivity_mean']:.3f}; "
        f"FNR: {metadata['selected_test_fnr_mean']:.3f}"
    )


if __name__ == "__main__":
    main()
