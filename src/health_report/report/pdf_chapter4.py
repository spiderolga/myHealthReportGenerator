from __future__ import annotations
import os
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from health_report.common.paths import OUTPUT
from health_report.common.config import REPORT_VERSION


def register_fonts():
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if os.path.exists(font_path) and "DejaVu" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu", font_path))
    if os.path.exists(bold_path) and "DejaVu-Bold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold_path))


def get_styles():
    register_fonts()
    styles = getSampleStyleSheet()
    normal_font = "DejaVu" if "DejaVu" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    bold_font = "DejaVu-Bold" if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    for s in ["Normal", "BodyText"]:
        styles[s].fontName = normal_font
    for s in ["Heading1", "Heading2", "Heading3"]:
        styles[s].fontName = bold_font
    styles.add(ParagraphStyle(name="Small", fontName=normal_font, fontSize=8, leading=10))
    styles.add(ParagraphStyle(name="Caption", fontName=normal_font, fontSize=8, leading=10, leftIndent=1.2 * cm, firstLineIndent=0, textColor=colors.HexColor("#4B5563")))
    return styles


def table_from_df(df, widths=None):
    body = []
    for row in df.values.tolist():
        out = []
        for v in row:
            if hasattr(v, "wrap") and hasattr(v, "drawOn"):
                out.append(v)
            else:
                out.append(str(v))
        body.append(out)
    data = [list(df.columns)] + body
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
        ("FONTNAME", (0, 0), (-1, 0), "DejaVu-Bold" if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "DejaVu" if "DejaVu" in pdfmetrics.getRegisteredFontNames() else "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
    ]))
    return t


def build_pdf(df, metrics, monthly, phases, figs):
    styles = get_styles()
    pdf = OUTPUT / f"Personal_Weight_Regulation_Model_{REPORT_VERSION}.pdf"
    doc = SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=1.4 * cm, leftMargin=1.4 * cm, topMargin=1.2 * cm, bottomMargin=1.2 * cm)
    els = []
    els.append(Paragraph(f"Draft {REPORT_VERSION} - Chapter 4: Body Composition Analysis", styles["Heading1"]))
    els.append(Paragraph("Personal Weight Regulation Model / N-of-1 Longitudinal Case Study", styles["Small"]))
    els.append(Spacer(1, 0.35 * cm))

    els.append(Paragraph("4.1 Dataset", styles["Heading2"]))
    body = df.dropna(subset=["Weight kg", "Fat mass kg", "Lean mass kg"], how="all")
    data = pd.DataFrame([
        ["Observation period", f"{df['Date'].min().date()} to {df['Date'].max().date()}"],
        ["Body composition period", f"{body['Date'].min().date()} to {body['Date'].max().date()}"],
        ["Duration", f"{(df['Date'].max() - df['Date'].min()).days} days"],
        ["Master dataset", "data/processed/master_dataframe.csv"],
        ["Primary variables", "Weight kg; Fat mass kg; Lean mass kg"],
        ["Smoothing used for figures", "7-day rolling mean"],
    ], columns=["Item", "Value"])
    els.append(table_from_df(data, widths=[5 * cm, 12 * cm])); els.append(Spacer(1, 0.35 * cm))

    els.append(Paragraph("4.2 Initial vs Final Body Composition", styles["Heading2"]))
    els.append(table_from_df(metrics, widths=[3.1 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.1 * cm, 2.5 * cm, 2.3 * cm])); els.append(Spacer(1, 0.2 * cm))
    els.append(Paragraph("Result: total weight increased while both Fat Mass and Lean Mass increased. Fat Mass accounted for the larger share of total weight change.", styles["Normal"]))
    els.append(Spacer(1, 0.4 * cm))

    els.append(Paragraph("4.3 Monthly Body Composition", styles["Heading2"]))
    monthly2 = monthly.reset_index().rename(columns={"index": "Month"})
    els.append(table_from_df(monthly2, widths=[3 * cm, 3 * cm, 3 * cm, 3 * cm])); els.append(PageBreak())

    els.append(Paragraph("4.4 Trajectories", styles["Heading2"]))
    for i, (caption, path) in enumerate(figs[:4], start=1):
        els.append(Image(str(path), width=17 * cm, height=7.7 * cm))
        els.append(Paragraph(f"Figure 4.{i}. {caption}", styles["Caption"]))
        els.append(Spacer(1, 0.2 * cm))
        if i == 2:
            els.append(PageBreak())

    els.append(PageBreak())
    els.append(Paragraph("4.5 Phase Analysis", styles["Heading2"]))
    keep = ["Phase", "Start", "End", "Days", "Weight Δ kg", "Fat Δ kg", "Lean Δ kg"]
    phases2 = phases[keep].copy()
    phases2["Phase"] = phases2["Phase"].apply(lambda x: Paragraph(str(x), styles["Small"]))
    els.append(table_from_df(phases2, widths=[5.2 * cm, 2.0 * cm, 2.0 * cm, 1.2 * cm, 2.55 * cm, 1.65 * cm, 1.9 * cm])); els.append(Spacer(1, 0.25 * cm))
    els.append(Paragraph("Interpretation: the body composition trajectory is not uniform across the study period. Early change was more lean-mass associated; later change was more fat-mass associated.", styles["Normal"]))
    els.append(Spacer(1, 0.4 * cm))

    for i, (caption, path) in enumerate(figs[4:], start=5):
        if i == 5:
            els.append(Image(str(path), width=17 * cm, height=8.8 * cm))
            els.append(Paragraph(f"Figure 4.{i}. {caption}", styles["Caption"]))
            els.append(PageBreak())
        else:
            els.append(Image(str(path), width=17 * cm, height=7.7 * cm))
            els.append(Paragraph(f"Figure 4.{i}. {caption}", styles["Caption"]))
            els.append(Spacer(1, 0.25 * cm))

    els.append(PageBreak())
    els.append(Paragraph("4.6 Evidence Summary", styles["Heading2"]))
    evd = pd.DataFrame([
        ["Fat Mass increased", "Withings trend, daily data", "High for direction; moderate for exact kg"],
        ["Lean Mass increased", "Withings trend, daily data", "High for direction; moderate for exact kg"],
        ["Weight change is mixed composition", "Fat and Lean both increased", "High"],
        ["Later period became more fat-dominant", "Phase analysis", "Moderate"],
    ], columns=["Finding", "Evidence", "Confidence"])
    for col in evd.columns:
        evd[col] = evd[col].apply(lambda x: Paragraph(str(x), styles["Small"]))
    els.append(table_from_df(evd, widths=[5.0 * cm, 6.6 * cm, 5.2 * cm]))
    doc.build(els)
    return pdf
