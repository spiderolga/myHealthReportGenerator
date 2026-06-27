from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
FIG = ROOT / 'figures'
OUT = ROOT / 'output'
for p in [FIG, OUT]: p.mkdir(exist_ok=True)

INPUT_MAIN = DATA / 'Health_Analytics_Database_DailySummary.xlsx'
INPUT_MFP = DATA / 'MyFitnessPal_parsed_data.xlsx'
EVENTS = DATA / 'events.csv'
PERIOD_START = pd.Timestamp('2025-09-01')
PERIOD_END = pd.Timestamp('2026-06-25')

# Fonts
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('DejaVu', font_path))
if os.path.exists(bold_path):
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', bold_path))


def load_data() -> pd.DataFrame:
    df = pd.read_excel(INPUT_MAIN, sheet_name='Daily Summary')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[(df['Date'] >= PERIOD_START) & (df['Date'] <= PERIOD_END)].copy()
    # force numeric
    for c in ['Weight kg','Fat mass kg','Lean mass kg','Body fat %','Weight 7d avg','Calories In','Protein g','Fat g','Fiber g']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    df['Fat_7d'] = df['Fat mass kg'].rolling(7, min_periods=3).mean()
    df['Lean_7d'] = df['Lean mass kg'].rolling(7, min_periods=3).mean()
    df['Weight_7d_calc'] = df['Weight kg'].rolling(7, min_periods=3).mean()
    df['Delta_Fat_from_start'] = df['Fat_7d'] - df['Fat_7d'].dropna().iloc[0]
    df['Delta_Weight_from_start'] = df['Weight_7d_calc'] - df['Weight_7d_calc'].dropna().iloc[0]
    df['Fat_28d_change'] = df['Fat_7d'] - df['Fat_7d'].shift(28)
    df['Fat_g_per_week_28d'] = df['Fat_28d_change'] / 4.0 * 1000
    return df


def load_events() -> pd.DataFrame:
    ev = pd.read_csv(EVENTS)
    ev['start'] = pd.to_datetime(ev['start'])
    ev['end'] = pd.to_datetime(ev['end'])
    ev = ev[(ev['end'] >= PERIOD_START) & (ev['start'] <= PERIOD_END)].copy()
    return ev





def style_time_axis(ax):
    """Shared compact styling for longitudinal plots."""
    ax.grid(True, alpha=.22)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', rotation=35, labelsize=8.8)
    ax.tick_params(axis='y', labelsize=8.8)


def save_compact(fig, out):
    """Save figures with less unused whitespace and larger plot area."""
    fig.subplots_adjust(left=0.075, right=0.985, top=0.90, bottom=0.18)
    fig.savefig(out, dpi=220)
    plt.close(fig)
    return out


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    x = df.set_index('Date').resample('MS').agg({
        'Weight kg':'mean', 'Fat mass kg':'mean', 'Lean mass kg':'mean'
    }).dropna(how='all')
    x.index = x.index.strftime('%Y-%m')
    x = x.rename(columns={'Weight kg':'Weight', 'Fat mass kg':'Fat Mass', 'Lean mass kg':'Lean Mass'})
    return x.round(2)


def first_last_metrics(df: pd.DataFrame) -> pd.DataFrame:
    cols = [('Weight kg','Weight'), ('Fat mass kg','Fat Mass'), ('Lean mass kg','Lean Mass')]
    rows=[]
    months = ((df['Date'].max() - df['Date'].min()).days) / 30.4375
    for col, name in cols:
        s = df[['Date',col]].dropna()
        start = float(s.iloc[0][col])
        end = float(s.iloc[-1][col])
        delta = end - start
        rows.append({
            'Metric': name,
            'Start': start,
            'End': end,
            'Delta kg': delta,
            'Delta %': delta/start*100,
            'kg/month': delta/months,
            'g/week': delta/((df['Date'].max()-df['Date'].min()).days/7)*1000
        })
    return pd.DataFrame(rows).round({'Start':2,'End':2,'Delta kg':2,'Delta %':1,'kg/month':3,'g/week':1})


def phase_summary(df: pd.DataFrame) -> pd.DataFrame:
    # phases chosen from observed monthly pattern and clinical timeline
    phases=[
        ('Phase I: early drift / lean-dominant adaptation','2025-09-01','2026-01-31'),
        ('Phase II: mixed transition','2026-02-01','2026-04-30'),
        ('Phase III: fat-dominant period','2026-05-01','2026-06-25'),
    ]
    rows=[]
    for name, start, end in phases:
        sub=df[(df['Date']>=pd.Timestamp(start))&(df['Date']<=pd.Timestamp(end))]
        row={'Phase':name,'Start':'','End':'','Days':len(sub)}
        for col,label in [('Weight kg','Weight'),('Fat mass kg','Fat'),('Lean mass kg','Lean')]:
            s=sub[['Date',col]].dropna()
            if len(s)>=2:
                if row['Start']=='': row['Start']=str(s.iloc[0]['Date'].date())
                row['End']=str(s.iloc[-1]['Date'].date())
                row[f'{label} start']=float(s.iloc[0][col])
                row[f'{label} end']=float(s.iloc[-1][col])
                row[f'{label} Δ kg']=float(s.iloc[-1][col]-s.iloc[0][col])
        rows.append(row)
    return pd.DataFrame(rows).round(2)


def plot_weight(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2,4.8))
    ax.plot(df['Date'], df['Weight kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Weight_7d_calc'], linewidth=2.2, label='7-day mean')
    ax.set_title('Weight trajectory', pad=8, fontsize=12)
    ax.set_ylabel('kg')
    style_time_axis(ax)
    ax.legend(frameon=False, fontsize=8.8)
    out=FIG/'fig_4_1_weight_trajectory.png'
    return save_compact(fig, out)


def plot_fat(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2,4.8))
    ax.plot(df['Date'], df['Fat mass kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Fat_7d'], linewidth=2.2, label='7-day mean')
    ax.set_title('Fat Mass trajectory', pad=8, fontsize=12)
    ax.set_ylabel('kg')
    style_time_axis(ax); ax.legend(frameon=False, fontsize=8.8)
    out=FIG/'fig_4_2_fat_trajectory.png'
    return save_compact(fig, out)


def plot_lean(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2,4.8))
    ax.plot(df['Date'], df['Lean mass kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Lean_7d'], linewidth=2.2, label='7-day mean')
    ax.set_title('Lean Mass trajectory', pad=8, fontsize=12)
    ax.set_ylabel('kg')
    style_time_axis(ax); ax.legend(frameon=False, fontsize=8.8)
    out=FIG/'fig_4_3_lean_trajectory.png'
    return save_compact(fig, out)


def plot_delta(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2,4.8))
    ax.plot(df['Date'], df['Delta_Weight_from_start'], linewidth=2, label='Weight Δ from Sep baseline')
    ax.plot(df['Date'], df['Delta_Fat_from_start'], linewidth=2, label='Fat Mass Δ from Sep baseline')
    ax.axhline(0, color='black', linewidth=.8, alpha=.5)
    ax.set_title('Weight and Fat Mass change from baseline', pad=8, fontsize=12)
    ax.set_ylabel('kg change')
    style_time_axis(ax); ax.legend(frameon=False, fontsize=8.8)
    out=FIG/'fig_4_4_delta_weight_fat.png'
    return save_compact(fig, out)


def plot_timeline(df: pd.DataFrame, ev: pd.DataFrame):
    """Fat mass timeline with intervention periods, clinical events, and travel areas."""
    import matplotlib.gridspec as gridspec
    import textwrap

    fig = plt.figure(figsize=(13.2, 5.55))
    # Event reference column is intentionally narrow (~18%).
    gs = gridspec.GridSpec(1, 2, width_ratios=[5.55, 1.20], wspace=0.06)
    ax = fig.add_subplot(gs[0, 0])
    ax_ref = fig.add_subplot(gs[0, 1])
    ax_ref.axis('off')

    # Main Fat Mass line.
    ax.plot(df['Date'], df['Fat_7d'], linewidth=2.45, color='#111827', zorder=6)

    # Curated timeline. Dates mirrored from data/events.csv and discussion notes.
    intervention_bands = [
        ('Ozempic (0.5 mg -> taper -> stop)', 'Sep-Dec 2025', pd.Timestamp('2025-09-01'), pd.Timestamp('2025-12-31'), '#4F46E5'),
        ('HRT 0.5 mg', 'from 06.01.2026', pd.Timestamp('2026-01-06'), pd.Timestamp('2026-03-31'), '#86EFAC'),
        ('HRT 1.0 mg', 'from 20.04.2026', pd.Timestamp('2026-04-20'), pd.Timestamp('2026-06-25'), '#047857'),
    ]
    event_markers = [
        ('Strength training started', 'Nov 2025', pd.Timestamp('2025-11-01'), '#7C3AED', '-'),
        ('RA flare (Mar-Apr 2026)', 'Mar-Apr 2026', pd.Timestamp('2026-03-16'), '#DC2626', '-'),
        ('Medrol course', 'Mar-Apr 2026', pd.Timestamp('2026-03-30'), '#B91C1C', '--'),
    ]
    travel_periods = [
        ('Winter Trip', '', pd.Timestamp('2026-02-06'), pd.Timestamp('2026-02-23'), '#F59E0B'),
        ('Italy Trip April', '', pd.Timestamp('2026-04-19'), pd.Timestamp('2026-05-02'), '#F59E0B'),
        ('Italy Trip May', '', pd.Timestamp('2026-05-12'), pd.Timestamp('2026-05-30'), '#F59E0B'),
    ]

    # Draw interventions first, then travel, then vertical event markers.
    for label, note, start, end, color in intervention_bands:
        alpha = 0.16 if 'HRT 1.0' not in label else 0.20
        ax.axvspan(start, end, color=color, alpha=alpha, linewidth=0, zorder=1)
    for label, note, start, end, color in travel_periods:
        ax.axvspan(start, end, color=color, alpha=0.19, linewidth=0, zorder=2)
    for label, note, date, color, linestyle in event_markers:
        ax.axvline(date, color=color, linewidth=1.75, linestyle=linestyle, alpha=0.90, zorder=4)

    ax.set_title('Fat Mass trajectory with intervention and event timeline', pad=8, fontsize=12)
    ax.set_ylabel('Fat Mass, kg')
    style_time_axis(ax)

    # Compact right-side reference table.
    ax_ref.text(0.00, 0.985, 'Event reference', transform=ax_ref.transAxes, fontsize=10.1, fontweight='bold', va='top', color='#111827')

    def ref_header(y, text):
        ax_ref.text(0.00, y, text, transform=ax_ref.transAxes, fontsize=8.4, fontweight='bold', va='top', color='#374151')
        return y - 0.046

    def label_text(label, note):
        return label if not note else f'{label}\n{note}'

    def ref_band(y, color, label, note='', alpha=0.25):
        ax_ref.add_patch(plt.Rectangle((0.00, y-0.030), 0.060, 0.028,
                                       transform=ax_ref.transAxes,
                                       facecolor=color, alpha=alpha,
                                       edgecolor=color, linewidth=0.7))
        wrapped = '\n'.join(textwrap.wrap(label_text(label, note), width=24, break_long_words=False))
        ax_ref.text(0.075, y-0.016, wrapped, transform=ax_ref.transAxes,
                    fontsize=7.25, va='center', color='#111827', linespacing=1.13)
        return y - (0.043 + 0.022 * max(0, wrapped.count('\n')))

    def ref_line(y, color, label, note='', linestyle='-'):
        ax_ref.plot([0.00, 0.060], [y-0.016, y-0.016], transform=ax_ref.transAxes,
                    color=color, linewidth=1.75, linestyle=linestyle, solid_capstyle='butt')
        wrapped = '\n'.join(textwrap.wrap(label_text(label, note), width=24, break_long_words=False))
        ax_ref.text(0.075, y-0.016, wrapped, transform=ax_ref.transAxes,
                    fontsize=7.25, va='center', color='#111827', linespacing=1.13)
        return y - (0.043 + 0.022 * max(0, wrapped.count('\n')))

    y = 0.92
    y = ref_header(y, 'Interventions')
    for label, note, _, _, color in intervention_bands:
        y = ref_band(y, color, label, note, alpha=0.30 if 'HRT 1.0' in label else 0.25)
    y = ref_line(y, '#7C3AED', 'Strength training started', 'Nov 2025')

    y -= 0.016
    y = ref_header(y, 'Clinical events')
    y = ref_line(y, '#DC2626', 'RA flare (Mar-Apr 2026)')
    y = ref_line(y, '#B91C1C', 'Medrol course', 'Mar-Apr 2026', linestyle='--')

    y -= 0.016
    y = ref_header(y, 'Travel')
    # Travel labels intentionally stay short.
    for label, note, _, _, color in travel_periods:
        y = ref_band(y, color, label, alpha=0.30)

    out = FIG / 'fig_4_5_fat_timeline_events.png'
    fig.subplots_adjust(left=0.065, right=0.99, top=0.91, bottom=0.17)
    fig.savefig(out, dpi=250)
    plt.close(fig)
    return out

def plot_growth_rate(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11.2,4.8))
    ax.plot(df['Date'], df['Fat_g_per_week_28d'], linewidth=2)
    ax.axhline(0, color='black', linewidth=.8, alpha=.5)
    ax.set_title('Fat Mass growth rate estimated over rolling 28-day windows', pad=8, fontsize=12)
    ax.set_ylabel('g/week')
    style_time_axis(ax)
    out=FIG/'fig_4_6_fat_growth_rate.png'
    return save_compact(fig, out)


def table_from_df(df, widths=None):
    body=[]
    for row in df.values.tolist():
        out=[]
        for v in row:
            # Preserve ReportLab Flowables such as Paragraph; stringify ordinary values.
            if hasattr(v, 'wrap') and hasattr(v, 'drawOn'):
                out.append(v)
            else:
                out.append(str(v))
        body.append(out)
    data=[list(df.columns)] + body
    t=Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E5E7EB')),
        ('FONTNAME',(0,0),(-1,0),'DejaVu-Bold' if 'DejaVu-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
        ('FONTNAME',(0,1),(-1,-1),'DejaVu' if 'DejaVu' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F9FAFB')])
    ]))
    return t


def build_pdf(df, metrics, monthly, phases, figs):
    styles=getSampleStyleSheet()
    normal_font='DejaVu' if 'DejaVu' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
    bold_font='DejaVu-Bold' if 'DejaVu-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'
    for s in ['Normal','BodyText']:
        styles[s].fontName=normal_font
    for s in ['Heading1','Heading2','Heading3']:
        styles[s].fontName=bold_font
    styles.add(ParagraphStyle(name='Small', fontName=normal_font, fontSize=8, leading=10))
    styles.add(ParagraphStyle(name='Caption', fontName=normal_font, fontSize=8, leading=10, textColor=colors.HexColor('#4B5563')))
    pdf=OUT/'Personal_Weight_Regulation_Model_v0.6.pdf'
    doc=SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=1.4*cm, leftMargin=1.4*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    els=[]
    els.append(Paragraph('Draft v0.6 - Chapter 4: Body Composition Analysis', styles['Heading1']))
    els.append(Paragraph('Personal Weight Regulation Model / N-of-1 Longitudinal Case Study', styles['Small']))
    els.append(Spacer(1,0.35*cm))
    els.append(Paragraph('4.1 Dataset', styles['Heading2']))
    data=pd.DataFrame([
        ['Observation period', f'{df["Date"].min().date()} to {df["Date"].max().date()}'],
        ['Duration', f'{(df["Date"].max()-df["Date"].min()).days} days'],
        ['Source', 'Health_Analytics_Database_DailySummary.xlsx / Daily Summary'],
        ['Primary variables', 'Weight kg; Fat mass kg; Lean mass kg'],
        ['Smoothing used for figures', '7-day rolling mean'],
    ], columns=['Item','Value'])
    els.append(table_from_df(data, widths=[5*cm, 12*cm])); els.append(Spacer(1,0.35*cm))

    els.append(Paragraph('4.2 Initial vs Final Body Composition', styles['Heading2']))
    els.append(table_from_df(metrics, widths=[3.1*cm,2.2*cm,2.2*cm,2.2*cm,2.1*cm,2.5*cm,2.3*cm])); els.append(Spacer(1,0.2*cm))
    els.append(Paragraph('Result: total weight increased while both Fat Mass and Lean Mass increased. Fat Mass accounted for the larger share of total weight change.', styles['Normal']))
    els.append(Spacer(1,0.4*cm))

    els.append(Paragraph('4.3 Monthly Body Composition', styles['Heading2']))
    monthly2=monthly.reset_index().rename(columns={'index':'Month'})
    els.append(table_from_df(monthly2, widths=[3*cm,3*cm,3*cm,3*cm])); els.append(PageBreak())

    els.append(Paragraph('4.4 Trajectories', styles['Heading2']))
    for i,(caption,path) in enumerate(figs[:4], start=1):
        els.append(Image(str(path), width=17*cm, height=7.7*cm))
        els.append(Paragraph(f'Figure 4.{i}. {caption}', styles['Caption']))
        els.append(Spacer(1,0.2*cm))
        if i==2: els.append(PageBreak())

    els.append(PageBreak())
    els.append(Paragraph('4.5 Phase Analysis', styles['Heading2']))
    keep=['Phase','Start','End','Days','Weight Δ kg','Fat Δ kg','Lean Δ kg']
    phases2=phases[keep].copy()
    phases2['Phase'] = phases2['Phase'].apply(lambda x: Paragraph(str(x), styles['Small']))
    els.append(table_from_df(phases2, widths=[5.2*cm,2.0*cm,2.0*cm,1.2*cm,2.55*cm,1.65*cm,1.9*cm])); els.append(Spacer(1,0.25*cm))
    els.append(Paragraph('Interpretation: the body composition trajectory is not uniform across the study period. Early change was more lean-mass associated; later change was more fat-mass associated.', styles['Normal']))
    els.append(Spacer(1,0.4*cm))

    for i,(caption,path) in enumerate(figs[4:], start=5):
        if i == 5:
            els.append(Image(str(path), width=17*cm, height=8.8*cm))
            els.append(Paragraph(f'Figure 4.{i}. {caption}', styles['Caption']))
            els.append(PageBreak())
        else:
            els.append(Image(str(path), width=17*cm, height=7.7*cm))
            els.append(Paragraph(f'Figure 4.{i}. {caption}', styles['Caption']))
            els.append(Spacer(1,0.25*cm))

    els.append(PageBreak())
    els.append(Paragraph('4.6 Evidence Summary', styles['Heading2']))
    evd=pd.DataFrame([
        ['Fat Mass increased','Withings trend, daily data','High for direction; moderate for exact kg'],
        ['Lean Mass increased','Withings trend, daily data','High for direction; moderate for exact kg'],
        ['Weight change is mixed composition','Fat and Lean both increased','High'],
        ['Later period became more fat-dominant','Phase analysis','Moderate'],
    ], columns=['Finding','Evidence','Confidence'])
    for col in evd.columns:
        evd[col] = evd[col].apply(lambda x: Paragraph(str(x), styles['Small']))
    els.append(table_from_df(evd, widths=[5.0*cm,6.6*cm,5.2*cm]))
    doc.build(els)
    return pdf


def main():
    df=load_data(); ev=load_events()
    metrics=first_last_metrics(df)
    monthly=monthly_summary(df)
    phases=phase_summary(df)
    # export tables
    metrics.to_csv(OUT/'body_composition_metrics.csv', index=False)
    monthly.to_csv(OUT/'monthly_body_composition.csv')
    phases.to_csv(OUT/'phase_summary.csv', index=False)
    figs=[
        ('Weight trajectory, daily values and 7-day rolling mean.', plot_weight(df)),
        ('Fat Mass trajectory, daily values and 7-day rolling mean.', plot_fat(df)),
        ('Lean Mass trajectory, daily values and 7-day rolling mean.', plot_lean(df)),
        ('Weight and Fat Mass change relative to September baseline.', plot_delta(df)),
        ('Fat Mass with major events and intervention periods. Intervention bands show long-running medication/HRT intervals; vertical markers show discrete clinical/training events; translucent areas show travel periods. The Event reference maps symbols to event names.', plot_timeline(df, ev)),
        ('Rolling 28-day Fat Mass growth rate, expressed as g/week.', plot_growth_rate(df)),
    ]
    pdf=build_pdf(df, metrics, monthly, phases, figs)
    print(f'Generated: {pdf}')

if __name__ == '__main__':
    main()
