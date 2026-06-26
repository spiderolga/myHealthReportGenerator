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
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.plot(df['Date'], df['Weight kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Weight_7d_calc'], linewidth=2.2, label='7-day mean')
    ax.set_title('Weight trajectory')
    ax.set_ylabel('kg')
    ax.grid(True, alpha=.25)
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    out=FIG/'fig_4_1_weight_trajectory.png'
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig); return out


def plot_fat(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.plot(df['Date'], df['Fat mass kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Fat_7d'], linewidth=2.2, label='7-day mean')
    ax.set_title('Fat Mass trajectory')
    ax.set_ylabel('kg')
    ax.grid(True, alpha=.25); ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    out=FIG/'fig_4_2_fat_trajectory.png'
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig); return out


def plot_lean(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.plot(df['Date'], df['Lean mass kg'], alpha=.25, linewidth=.8, label='Daily')
    ax.plot(df['Date'], df['Lean_7d'], linewidth=2.2, label='7-day mean')
    ax.set_title('Lean Mass trajectory')
    ax.set_ylabel('kg')
    ax.grid(True, alpha=.25); ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    out=FIG/'fig_4_3_lean_trajectory.png'
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig); return out


def plot_delta(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.plot(df['Date'], df['Delta_Weight_from_start'], linewidth=2, label='Weight Δ from Sep baseline')
    ax.plot(df['Date'], df['Delta_Fat_from_start'], linewidth=2, label='Fat Mass Δ from Sep baseline')
    ax.axhline(0, color='black', linewidth=.8, alpha=.5)
    ax.set_title('Weight and Fat Mass change from baseline')
    ax.set_ylabel('kg change')
    ax.grid(True, alpha=.25); ax.legend(frameon=False)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    out=FIG/'fig_4_4_delta_weight_fat.png'
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig); return out


def plot_timeline(df: pd.DataFrame, ev: pd.DataFrame):
    """Fat mass timeline with event spans and a readable side legend.

    The legend is a compact table placed outside the plotting area. It is kept
    intentionally short because full event labels are documented in events.csv.
    """
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(12.2, 5.8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[4.9, 1.55], wspace=0.12)
    ax = fig.add_subplot(gs[0, 0])
    ax_leg = fig.add_subplot(gs[0, 1])
    ax_leg.axis('off')

    ax.plot(df['Date'], df['Fat_7d'], linewidth=2.5, color='#111827', label='Fat Mass 7-day mean', zorder=5)

    category_colors = {
        'Medication': '#4F46E5',
        'Nutrition': '#059669',
        'Training': '#7C3AED',
        'HRT': '#10B981',
        'RA': '#DC2626',
        'Travel': '#F59E0B',
    }
    short_labels = {
        'Medication': 'Medication',
        'Nutrition': 'Nutrition',
        'Training': 'Training',
        'HRT': 'HRT',
        'RA': 'RA / Medrol',
        'Travel': 'Travel',
    }

    used_categories = []
    for _, r in ev.iterrows():
        cat = str(r['category'])
        color = category_colors.get(cat, '#6B7280')
        ax.axvspan(r['start'], r['end'], color=color, alpha=0.16, linewidth=0, zorder=1)
        if cat not in used_categories:
            used_categories.append(cat)

    ax.set_title('Fat Mass trajectory with event timeline')
    ax.set_ylabel('Fat Mass, kg')
    ax.grid(True, alpha=.25, zorder=0)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.tick_params(axis='x', rotation=35, labelsize=8.5)
    ax.tick_params(axis='y', labelsize=8.5)

    # Side legend table with readable spacing.
    ax_leg.text(0.02, 0.98, 'Event legend', fontsize=11, fontweight='bold', va='top', color='#111827')
    y = 0.88
    row_gap = 0.115
    for cat in ['Medication', 'Nutrition', 'Training', 'HRT', 'RA', 'Travel']:
        if cat not in used_categories:
            continue
        ax_leg.add_patch(plt.Rectangle((0.02, y-0.025), 0.10, 0.052,
                                       transform=ax_leg.transAxes,
                                       facecolor=category_colors[cat],
                                       alpha=0.35,
                                       edgecolor=category_colors[cat],
                                       linewidth=0.8))
        ax_leg.text(0.17, y, short_labels.get(cat, cat),
                    transform=ax_leg.transAxes,
                    fontsize=9.2,
                    va='center',
                    color='#111827')
        y -= row_gap

    ax_leg.text(0.02, 0.11,
                'Bands indicate\nperiods, not exact\npoint events.',
                fontsize=8.1,
                color='#4B5563',
                va='bottom',
                linespacing=1.35)

    out = FIG / 'fig_4_5_fat_timeline_events.png'
    fig.savefig(out, dpi=240, bbox_inches='tight')
    plt.close(fig)
    return out

def plot_growth_rate(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10,4.5))
    ax.plot(df['Date'], df['Fat_g_per_week_28d'], linewidth=2)
    ax.axhline(0, color='black', linewidth=.8, alpha=.5)
    ax.set_title('Fat Mass growth rate estimated over rolling 28-day windows')
    ax.set_ylabel('g/week')
    ax.grid(True, alpha=.25)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate()
    out=FIG/'fig_4_6_fat_growth_rate.png'
    fig.tight_layout(); fig.savefig(out, dpi=200); plt.close(fig); return out


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
    pdf=OUT/'Personal_Weight_Regulation_Model_v0.4.pdf'
    doc=SimpleDocTemplate(str(pdf), pagesize=A4, rightMargin=1.4*cm, leftMargin=1.4*cm, topMargin=1.2*cm, bottomMargin=1.2*cm)
    els=[]
    els.append(Paragraph('Draft v0.4 - Chapter 4: Body Composition Analysis', styles['Heading1']))
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
        ('Fat Mass with major events and intervention periods. Colored vertical bands indicate event/intervention periods; the right-side legend table maps colors to categories.', plot_timeline(df, ev)),
        ('Rolling 28-day Fat Mass growth rate, expressed as g/week.', plot_growth_rate(df)),
    ]
    pdf=build_pdf(df, metrics, monthly, phases, figs)
    print(f'Generated: {pdf}')

if __name__ == '__main__':
    main()
