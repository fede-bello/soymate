"""Build docs/soymate_viability_brief.pdf from the desk research in research/viability/.

Run:  uv run --no-project --with reportlab --with matplotlib python scripts/docs/build_viability_brief.py
Every figure in the PDF comes from research/viability/*.md or CONTEXT.md; numbers in brackets point to the
source list at the end of the PDF. Tags: [V] read on the primary source, [F] secondary or snippet,
[NV] own calculation or inference (inputs given), [A] assumption.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "soymate_viability_brief.pdf"
FIG = ROOT / "docs" / "figures" / "viability"
LOGO = ROOT / "assets" / "logo.png"

GREEN = colors.HexColor("#2E7D32")
GREEN_HEX = "#2E7D32"
GREEN_LIGHT_HEX = "#A5D6A7"
INK = colors.HexColor("#212121")
MUTED = colors.HexColor("#616161")
BOX = colors.HexColor("#EEF6EE")
HEAD = colors.HexColor("#E0E0E0")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=20, leading=24,
                    alignment=TA_LEFT, textColor=INK, spaceAfter=4)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=17,
                    textColor=GREEN, spaceBefore=10, spaceAfter=4, keepWithNext=1)
H3 = ParagraphStyle("H3", parent=ss["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                    textColor=INK, spaceBefore=6, spaceAfter=2, keepWithNext=1)
BODY = ParagraphStyle("B", parent=ss["BodyText"], fontName="Helvetica", fontSize=9, leading=11.5, textColor=INK)
SMALL = ParagraphStyle("S", parent=BODY, fontSize=7.5, leading=9.5)
CELL = ParagraphStyle("C", parent=BODY, fontSize=7.8, leading=9.6)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold")
CAP = ParagraphStyle("Cap", parent=BODY, fontSize=7.8, leading=9.5, textColor=MUTED, fontName="Helvetica-Oblique")
BUL = ParagraphStyle("Bul", parent=BODY, leftIndent=10, bulletIndent=2)


def P(text, style=BODY):
    return Paragraph(text, style)


def bullets(items, style=BUL):
    return [Paragraph(t, style, bulletText="•") for t in items]


def table(rows, widths, header=True, bold_first_col=False):
    data = []
    for i, r in enumerate(rows):
        row = []
        for j, c in enumerate(r):
            st = CELLB if (header and i == 0) or (bold_first_col and j == 0) else CELL
            row.append(Paragraph(str(c), st))
        data.append(row)
    t = Table(data, colWidths=[w * cm for w in widths], repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#BDBDBD")),
             ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
             ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), HEAD))
    t.setStyle(TableStyle(style))
    return t


def box(flowables):
    t = Table([[flowables]], colWidths=[17.4 * cm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BOX),
                           ("BOX", (0, 0), (-1, -1), 0.6, GREEN),
                           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def figure(path, caption, width_cm=16.0):
    img = Image(str(path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth, img.drawHeight = width_cm * cm, width_cm * cm * ratio
    return KeepTogether([img, Spacer(1, 2), P(caption, CAP), Spacer(1, 6)])


# ---------------------------------------------------------------- charts

def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#9E9E9E")
    ax.spines["bottom"].set_color("#9E9E9E")
    ax.tick_params(colors="#424242", labelsize=8)
    ax.grid(axis="x" if ax.get_ylabel() == "" else "y", color="#E0E0E0", linewidth=0.6)
    ax.set_axisbelow(True)


def make_charts():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "Helvetica", "font.size": 8})

    # 1. Food vs feed price gap, EUR/t (low and high estimate)
    crops = ["Soybean", "Yellow pea", "Lentil"]
    low = [20, 30, 556]
    high = [70, 30, 623]
    fig, ax = plt.subplots(figsize=(7.2, 2.0), dpi=200)
    y = range(len(crops))
    ax.barh(y, high, color=GREEN_LIGHT_HEX, height=0.5, label="high estimate")
    ax.barh(y, low, color=GREEN_HEX, height=0.5, label="low estimate")
    for i, (lo, hi) in enumerate(zip(low, high)):
        txt = f"{lo} €/t" if lo == hi else f"{lo} to {hi} €/t"
        ax.text(hi + 8, i, txt, va="center", fontsize=8, color="#212121")
    ax.set_yticks(list(y), crops)
    ax.set_xlim(0, 720)
    ax.set_xlabel("Price gap between food and feed outlet (€ per tonne)", fontsize=8, color="#424242")
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    _style(ax)
    ax.grid(axis="x", color="#E0E0E0", linewidth=0.6)
    fig.tight_layout()
    fig.savefig(FIG / "price_gap.png")
    plt.close(fig)

    # 2. Lentil bruchid damage, mean % per lot, 2021-2025
    years = ["2021", "2022", "2023", "2024", "2025"]
    vals = [11.6, 15.3, 10.3, 14.5, 24.4]
    fig, ax = plt.subplots(figsize=(3.5, 2.3), dpi=200)
    ax.bar(years, vals, color=GREEN_HEX, width=0.6)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.5, f"{v}", ha="center", fontsize=7.5, color="#212121")
    ax.set_ylabel("% bruchid-damaged grains", fontsize=7.5, color="#424242")
    ax.set_ylim(0, 28)
    _style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "lentil_bruchid.png")
    plt.close(fig)

    # 3. Lentil net trade deficit, t
    camp = ["20/21", "21/22", "22/23", "23/24", "24/25"]
    deficit = [22030, 32934, 34606, 33682, 38282]
    fig, ax = plt.subplots(figsize=(3.5, 2.3), dpi=200)
    ax.bar(camp, [d / 1000 for d in deficit], color=GREEN_HEX, width=0.6)
    for i, d in enumerate(deficit):
        ax.text(i, d / 1000 + 0.6, f"{d / 1000:.1f}", ha="center", fontsize=7.5, color="#212121")
    ax.set_ylabel("Net lentil imports (kt)", fontsize=7.5, color="#424242")
    ax.set_ylim(0, 44)
    _style(ax)
    fig.tight_layout()
    fig.savefig(FIG / "lentil_deficit.png")
    plt.close(fig)


# ---------------------------------------------------------------- page decoration

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.8 * cm, 1.0 * cm, "SoyMate · Hack the Fork Paris 2026 · Viability brief")
    canvas.drawRightString(A4[0] - 1.8 * cm, 1.0 * cm, str(doc.page))
    canvas.restoreState()


# ---------------------------------------------------------------- content

def build():
    make_charts()
    s = []

    # Title block
    logo = Image(str(LOGO), width=2.6 * cm, height=2.6 * cm)
    title = [P("SoyMate: viability brief", H1),
             P("Is a phone-photo seed grader worth building for France, what would make it work, and where "
               "it should go after the soybean proof of concept. Market research done 31/10/2026, during the "
               "event; the dataset audits it cites were done before the event and are declared as prior "
               "resources. No model results yet: those come from the hackathon build. Detailed notes: "
               "<font name='Courier'>research/viability/</font>; adversarial review: "
               "<font name='Courier'>research/critique.md</font>.", BODY)]
    head = Table([[logo, title]], colWidths=[3.0 * cm, 14.4 * cm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    s += [head, Spacer(1, 6)]

    s.append(P("How to read the numbers", H3))
    s.append(P("Each figure carries a source number <b>[n]</b> (list at the end) and a tag: <b>[V]</b> read on the "
               "primary source; <b>[F]</b> secondary source or snippet; <b>[NV]</b> our own calculation or inference "
               "(inputs given); <b>[A]</b> an assumption, listed in section 8 and varied in the scenario "
               "table.", SMALL))

    s.append(P("In one page", H2))
    s.append(box([
        P("<b>What we build at the hackathon.</b> A proof of concept on soybean, the only legume with public "
          "labelled seed-defect data: segment every seed in a photo, classify it, give the % of each defect with a "
          "confidence interval, and a pass/fail against a selectable food-grade threshold.", BODY),
        Spacer(1, 3),
        P("<b>Soybean alone is a weak business.</b> French food soy is ~45 kt/yr out of ~400 kt [2] [V], and the "
          "food vs feed price gap is \"très faible\": under 25 €/t in 2019/20 and 2022/23 [10] [V] [11] [F] "
          "(~70 €/t quoted for 2021 [6] [V]).", BODY),
        Spacer(1, 3),
        P("<b>Lentil is where a tonne is worth defending.</b> Food lentil sells for 806 to 873 €/t [24] [V] "
          "against ~250 €/t for feed protein crops [23] [V]: ~550 to 620 €/t at stake [NV]. In 2025 the "
          "mean bruchid damage per lot was 24.4 %, the highest of the survey's 2021-2025 series (40 lots measured) "
          "[15] [V]. An estimated 45 to 55 % of the lentils eaten in France are imported [13] [V] [NV, production "
          "is estimated].", BODY),
        Spacer(1, 3),
        P("<b>The market exists.</b> Cropify already sells AI lentil and chickpea grading in Australia; Grain "
          "Trade Australia's Trading Standards Committee judged it worth \"commercial consideration\" in August 2026 "
          "[26] [V]. Nobody publicly covers French soy or pulses: Inarix, present in ~600 silos, covers cereals "
          "only [28] [29] [V].", BODY),
        Spacer(1, 3),
        P("<b>Where the value is, and where it is not.</b> A better grade mostly moves money between farmer and "
          "collector; it creates value only when it <b>changes a decision</b> (sort or not, which contract or "
          "storage cell, accept or contest a lot) or <b>removes a dispute</b>. And one photo is noisy: at 25 % "
          "damage a 200-grain count is ±6 points [NV, binomial]. So the product is <b>a fast, repeatable, "
          "documented grade that the farmer can check</b>, built from enough grains, not a \"€ per point\" "
          "saving.", BODY),
        Spacer(1, 3),
        P("<b>Money (section 6, illustrative).</b> At 1,500 € per site per year [A4], a collector breaks "
          "even with any one of: ~11 avoided lab arbitrations, 375 to 750 replaced manual counts, or one 28 t "
          "lentil lot correctly kept in the food outlet every ~10 years. Customer return: 0.3x without "
          "allocation gains, ~1.9x in our base case, 7.2x optimistic [NV, A10-A12]. Our marginal cost per "
          "analysis is near zero (phone, CPU model); the fixed cost is French data and a pilot.", BODY),
        Spacer(1, 3),
        P("<b>Impact.</b> In 2025 the lentil sorting loss was up to ~5 to 8 M€ [NV, upper bound], carried by "
          "farmers through deductions they cannot verify today. A grade they can check before and at delivery "
          "supports their income, the Track 3 question [1]. It does not raise demand or acreage, and we do not "
          "claim it does.", BODY),
        Spacer(1, 3),
        P("<b>Honest limit.</b> France alone is a small market (a few M€ of value per year across soy and "
          "pulses [NV]). The viable route is a phone-only soy and pulse module for a tool already at the intake "
          "desk, or EU expansion, with lentil first.", BODY),
    ]))

    # 1. Why soybean for the PoC
    s.append(P("1. What the hackathon proof of concept is, and why soybean", H2))
    s += bullets([
        "<b>Only soybean has the data.</b> We found no public RGB photo dataset of damaged pea, lentil, faba bean, "
        "chickpea or beans after two searches (Mendeley, Zenodo, figshare, Kaggle, Hugging Face, GitHub, Data in "
        "Brief, Scientific Data) [43] [NV, negative search]. The closest French data is Radio_lentille (Terres "
        "Inovia): 807 X-rays of bruchid-damaged lentils with count spreadsheets (MIT licence) [43]. X-rays, not "
        "phone photos, but its counts give a real distribution of lot damage.",
        "<b>Data we use:</b> Indian soybean beetle-damage set (audited before the event, declared as a prior "
        "resource: 80 to 84 % of the published validation and test images leak from train, so the split is "
        "regenerated at the event), Chinese 5-class Soybean Seeds (intact, spotted, immature, "
        "broken, skin-damaged), and three sets of real multi-seed photos: Ghana phone photos (~150 seeds each), "
        "mechanical-harvest images with intact/crushed/impurity masks, Indonesian flatbed scans. All CC BY 4.0 [43].",
        "<b>What the PoC will measure</b> (results come during the event): R1 leaky vs clean split; R2 per-class "
        "F1 on the clean test set; R3 transfer from one dataset to another with 0, 5, 10, 25, 50 labelled grains "
        "per class (the cost of a new capture setup); R4 seed-count error on real multi-seed photos and lot-level "
        "error on simulated lots (declared synthetic).",
        "<b>What R3 does and does not show:</b> it measures how much labelled data a new capture setup costs "
        "within one species. It says nothing direct about lentil, whose shape and seed coat differ (a \"stained\" "
        "class trained on soy may fire on naturally speckled lentils). Everything about lentil below is a "
        "hypothesis until it is tested on French lentil photos.",
        "<b>Soy classes that matter in France:</b> green/immature seeds (the 2025 food-limiting defect [3]), "
        "broken, stained. The \"insect hole\" class comes from an Indian storage pest that is not a French soy "
        "problem [CONTEXT.md §3]; it is kept only as a method demo for the lentil route, where bruchid exit "
        "holes are the main defect.",
    ])

    # 2. Market picture
    s.append(P("2. The French market in numbers", H2))
    s.append(table([
        ["", "Soybean", "Lentil", "Pea", "Faba bean"],
        ["Area", "150 kha (2025), down from 187 kha in 2020 [5] [V]", "34,216 ha (2024) [13] [V]",
         "123.5 kha (2024) [13] [V]", "83.4 kha (2024) [13] [V]"],
        ["Production", "~392 kt (2025) [5] [V]; 298 kt forecast for 2026 [9] [F]",
         "40 to 59 kt (2024), no official figure [NV, A5]", "350 kt (2024) [13] [V]", "224 kt (2024) [13] [V]"],
        ["Human food", "45 kt/yr, ~11 %, almost all French, under contract [2] [8] [V]",
         "Almost all; an estimated 45 to 55 % of consumption imported [13] [V] [NV, A5]",
         "136 kt food and non-food ingredients (2024/25), mostly fractionation [13] [V]",
         "11 kt (2024/25) [13] [V]"],
        ["Producer price", "596 to 617 €/t conventional (2022/23) [11] [F]", "806 to 873 €/t [24] [V]",
         "250 feed vs 280 food €/t, indicative [25] [V]", "200 to 260 €/t (feed range) [23] [V]"],
        ["Quality problem", "2025: 37 % of lots >1 % green (immature) seeds vs 11 % in 2024, \"pénalisant\" "
         "for food; protein 39.8 % DM, a 10-year low [3] [V]",
         "2025: mean 24.4 % bruchid-damaged grains per lot (40 lots), highest of 2021-2025; 36.8 % in "
         "Centre-Ouest [15] [V]",
         "2025: only 55 % of lots under 1 % broken grains, the most limiting food criterion [44] [V]",
         "Egypt food exports fell from 245 kt to 87 kt, mainly over bruchids [21] [F]"],
        ["Visible in a photo?", "Green seeds yes; protein no (needs NIR)", "Exit holes yes; larvae inside no",
         "Broken yes", "Holes yes; larvae no"],
    ], [2.4, 4.0, 3.9, 3.6, 3.5], bold_first_col=True))
    s.append(Spacer(1, 6))
    s.append(figure(FIG / "price_gap.png",
                    "Figure 1. Food minus feed price per tonne. Soybean: observatory gap 2019-2023 (low) [10] [11] "
                    "and the 2021 contract premium (high) [6]. Pea: indicative prices 280 vs 250 €/t [25]. "
                    "Lentil: producer price 806 to 873 €/t [24] minus a 250 €/t feed proxy [23] [A2], "
                    "because no feed-lentil price is published [NV]."))

    # 3. Why soy alone is weak
    s.append(P("3. Why soybean alone is not a business", H2))
    s += bullets([
        "<b>Thin premium.</b> The interprofession's producer-price observatory calls the soy food vs feed gap "
        "\"très faible\" [10] [V]: 343 vs 326 €/t (2019/20), 617 vs 596 €/t (2022/23) [11] [F]. The whole "
        "French food-soy premium is ~0.9 to 3.2 M€/yr [NV: 45 kt x 20 to 70 €/t]. A 28 t lot wrongly sent "
        "to feed would lose ~560 to 1,960 € [NV, A1, A6], but food soy is grown under contract with set "
        "varieties and we found no record of how often that happens.",
        "<b>Few buyers, who already control quality.</b> Six soyfood plants [6] [V]; Olga alone buys 8 to 9 kt/yr "
        "[12] [V]. They use variety lists, contracts and their own sorting [6] [12] [V].",
        "<b>No public French food spec</b> for broken, split or stained soy; contracts set operator-specific "
        "limits on green, black, broken and half seeds and hilum colour [7] [V]. The national survey does not "
        "measure broken or stained soy [3] [V].",
        "<b>Shrinking supply:</b> area -20 % since 2020 [5] [V]; 2026 forecast 298 kt (-25 %) [9] [F].",
        "<b>What still works for soy:</b> green (immature) seeds were the visible defect that hurt the food outlet "
        "in 2025 [3] [V], and \"immature\" is one of our classes. That makes soy a credible first use, not a "
        "business on its own.",
    ])

    # 4. Lentil
    s.append(P("4. Why lentil is the extension worth building", H2))
    charts = Table([[Image(str(FIG / "lentil_bruchid.png"), width=8.4 * cm, height=5.5 * cm),
                     Image(str(FIG / "lentil_deficit.png"), width=8.4 * cm, height=5.5 * cm)]],
                   colWidths=[8.7 * cm, 8.7 * cm])
    s.append(KeepTogether([charts, P("Figure 2. Left: mean % bruchid-damaged grains per lentil lot, national "
                                     "quality survey (2025: 40 lots measured) [15] [V, 2021-2024 read from the "
                                     "survey chart]. Right: France's net lentil imports, campaigns July-June "
                                     "[13] [V].", CAP), Spacer(1, 6)]))
    s += bullets([
        "<b>High value per tonne:</b> ~550 to 620 €/t between food and feed [NV, 24, 23, A2], about 10 to 30 "
        "times the soy gap.",
        "<b>A growing problem with no field fix:</b> 2025 had the highest mean damage of the survey's 2021-2025 "
        "series [15] [V]; \"la lutte chimique préventive est actuellement dans une impasse\" [20] [V].",
        "<b>Far outside export grades:</b> under Canadian Grain Commission grades, total damage above 10 % "
        "already falls below grade No. 3 [41] [V], so a 24 % lot is far from any food grade before sorting [NV].",
        "<b>Import substitution:</b> net imports grew from 22,030 t (2020/21) to 38,282 t (2024/25), about half "
        "of them from Canada [13] [V]. Policy names local légumes secs as a priority [19] [V].",
        "<b>The decision is sorting and pricing, not food vs feed.</b> Damaged lentil is cleaned or optically "
        "sorted back to standard [20] [V], and the sorter's reject fraction tells the collector the loss by "
        "weight, after the fact [NV]. The tool's role is earlier: before unloading and before sorting, to decide "
        "whether to sort, which cell or contract the lot goes to, and to give the farmer the same number. At "
        "24 % damage the sorting loss is ~136 € per harvested tonne, ~5 to 8 M€ nationally in 2025 "
        "(upper bound) [NV].",
        "<b>Proof that buyers pay:</b> Cropify grades lentils for GrainCorp, Louis Dreyfus, ETG Wimpak and Shannon "
        "Bros, plans up to 25 units for the 2026 harvest, adds chickpea, then faba in 2027; Grain Trade "
        "Australia's Trading Standards Committee judged it worth \"commercial consideration\" [26] [27] [V].",
    ])

    # 5. Value model
    s.append(P("5. Value model: where value is created, and where it is not", H2))
    s.append(P("A grade is a price. Correcting a grade moves money between farmer and collector, and if manual "
               "grading is noisy but unbiased the corrections cancel out across trucks [NV]. So \"€ per "
               "point of correction\" is not a value model. Value is created only in these places:", BODY))
    s.append(Spacer(1, 3))
    s.append(table([
        ["Source of value", "Mechanism", "Evidence", "Status"],
        ["Decisions that change", "Sort or not; which cell or contract; accept or contest a lot before "
         "unloading", "Lentil diverted from food loses ~550 to 620 €/t [NV, 24, 23]", "How often a decision "
         "changes is unknown [A3]"],
        ["Fewer disputes, same grade everywhere", "One method across staff and sites, with stored images as "
         "evidence", "Australian receival grading varies \"from person to person\" and between sites [45] [V]; "
         "lab arbitration is 130 € HT per lot [37] [V]", "Dispute frequency unknown"],
        ["Speed at the harvest peak", "Shorter queues when trucks arrive together", "Cropify: ~5.3 min per "
         "sample [27] [V]; manual pulse grading \"up to 20 minutes\" in Australia [46] [F]", "Partly sourced"],
        ["A grade the farmer can check (impact)", "Same photo method before delivery and at reception",
         "Track 3 asks how farmers earn from plant protein [1]", "Design hypothesis"],
    ], [3.4, 4.6, 5.6, 3.8], bold_first_col=True))
    s.append(Spacer(1, 6))
    s.append(P("How many grains a grade needs [NV, binomial 95 % half-width, in percentage points]", H3))
    ns = (150, 200, 500, 1000, 2000)
    rows = [["True damage"] + [f"{n} grains" for n in ns]]
    for p_ in (0.02, 0.05, 0.15, 0.25):
        rows.append([f"{p_ * 100:.0f} %"] + [f"±{1.96 * (p_ * (1 - p_) / n) ** 0.5 * 100:.1f}" for n in ns])
    s.append(table(rows, [3.4, 2.8, 2.8, 2.8, 2.8, 2.8]))
    s.append(Spacer(1, 4))
    s += bullets([
        "At realistic lentil damage (15 to 25 %), even 1,000 grains leave ±2.2 to ±2.7 points. No method, "
        "human or photo, can resolve a 1-point difference on one sample. Phone grading earns its place by "
        "counting many grains quickly and the same way every time, not by precision on one photo.",
        "Certifying a strict threshold is harder still: with zero defects found, the Wilson upper bound is "
        "~2.5 % for 150 grains; showing ≤1 % needs ~380 clean grains [NV]. Classifier errors add bias: a 2 % "
        "false-positive rate makes a clean lot read ~3 %, so reported % must be corrected with the measured "
        "sensitivity and specificity, and the app must say \"inconclusive, add grains\" near the threshold.",
    ])
    s.append(P("Scale check, France only [NV]", H3))
    s.append(table([
        ["Quantity", "Value", "Inputs"],
        ["Lentil trucks per year", "~1,430 to 2,110", "40 to 59 kt [A5] / 28 t [A1]"],
        ["Lentil sorting loss at stake, 2025", "~5 to 8 M€ (upper bound)",
         "24.4 % damage [15] x production x ~556 €/t"],
        ["Food-soy premium pool", "~0.9 to 3.2 M€/yr", "45 kt [2] x 20 to 70 €/t [10] [6]"],
        ["Protein-crop collectors", "477 (2024/25)", "[14] [V]; they handle pea and faba; the number "
         "handling lentil was not found"],
        ["Illustrative revenue if all 477 paid 1,500 €/yr", "~0.72 M€/yr", "[A4]"],
    ], [6.4, 4.0, 7.0]))
    s.append(Spacer(1, 4))
    s.append(P("<b>Reading:</b> France alone cannot support a standalone company, and the value per site rests "
               "on decisions and disputes we have not measured yet [A3]. Viability needs a channel (a module in "
               "an existing intake tool) or more markets (EU pulses, more crops), and a pilot that counts how "
               "often a grade changes a decision.", BODY))

    # 6. Money
    s.append(P("6. Money: customer ROI, our revenue, price benchmarks", H2))
    s.append(P("All figures below are illustrative calculations [NV] on the assumptions in section 8; each input is "
               "named so a reader can change it.", SMALL))
    s.append(P("6.1 Break-even for a collector paying 1,500 €/yr [A4]", H3))
    s.append(P("Instead of claiming an ROI we cannot measure yet, we ask: <b>what would the tool have to do, per "
               "season and per site, to pay for itself?</b> Any one of these is enough:", BODY))
    s.append(Spacer(1, 3))
    be = [["The tool avoids...", "Value of one", "Needed per season to break even", "Inputs"]]
    for what, lo, hi, inputs in [
        ("a manual defect count (labour)", 2, 4, "10-20 min at ~12 €/h gross [38] [F] [NV]"),
        ("an arbitration-lab analysis", 140, 140, "130 € HT analysis + 10 € handling [37] [V]"),
        ("a food-soy lot wrongly sent to feed (28 t)", 560, 1960, "28 t [A1] x 20-70 €/t [A6]"),
        ("a sortable lentil lot wrongly kept out of food (28 t)", 15568, 17444,
         "28 t [A1] x 556-623 €/t [24] [A2]"),
    ]:
        val = f"{lo:,} €" if lo == hi else f"{lo:,} to {hi:,} €"
        need_lo, need_hi = 1500 / hi, 1500 / lo
        if need_lo >= 0.5:
            need = f"{need_lo:.0f}" if round(need_lo) == round(need_hi) else f"{need_lo:.0f} to {need_hi:.0f}"
        else:
            need = f"{need_lo:.2f} to {need_hi:.2f} (one every ~{1 / need_hi:.0f} to {1 / need_lo:.0f} years)"
        be.append([what, val, need, inputs])
    s.append(table(be, [4.6, 3.0, 4.6, 5.2]))
    s.append(Spacer(1, 4))
    s.append(P("<b>Reading:</b> labour alone needs hundreds of counts per site, which only large intake sites "
               "reach. The case is made by <b>allocation</b>: one lentil lot routed wrongly in ten years pays the "
               "subscription. Whether that happens is exactly what a pilot must count [A3] [A12].", BODY))

    s.append(P("6.2 Customer ROI in three scenarios (one lentil-receiving site, one season)", H3))
    lot = 16500  # midpoint of the 28 t lentil lot value above
    sc_in = {"Conservative": (150, 0, 0.0), "Base": (300, 2, 0.1), "Optimistic": (600, 5, 0.5)}
    sc = [[""] + list(sc_in), ["Manual counts replaced x 3 € [A10]"], ["Arbitrations avoided x 140 € [A11]"],
          ["Wrong lentil allocations avoided x 16,500 € [A12]"], ["Value per season"],
          ["Cost (subscription [A4])"], ["Return per € spent"]]
    for counts, arb, alloc in sc_in.values():
        v = [counts * 3, arb * 140, alloc * lot]
        sc[1].append(f"{counts} = {v[0]:,} €")
        sc[2].append(f"{arb} = {v[1]:,} €")
        sc[3].append(f"{alloc:g} = {v[2]:,.0f} €")
        sc[4].append(f"{sum(v):,.0f} €")
        sc[5].append("1,500 €")
        sc[6].append(f"{sum(v) / 1500:.1f}x")
    s.append(table(sc, [6.2, 3.7, 3.7, 3.8], bold_first_col=True))
    s.append(Spacer(1, 4))
    s.append(P("<b>Reading:</b> without allocation gains the tool does not pay for itself; with one avoided lentil "
               "misallocation every ten years it roughly pays twice over. The base column is our working "
               "hypothesis, not a result. 16,500 € is the midpoint of the 28 t lentil lot value above.", BODY))

    s.append(P("6.3 Our side: price, cost, revenue", H3))
    s += bullets([
        "<b>Price:</b> 1,500 € per site per year [A4], or credits per analysis as Inarix sells [28] [V]. Per "
        "sample we would sit between a manual count (~2-4 € labour [NV]) and imaging competitors (ZoomAgri "
        "~$15 [47] [F]; Nebulaa Rs 150-200 [48] [F]).",
        "<b>Marginal cost:</b> near zero per analysis: the model is frozen features plus a linear layer and runs "
        "on a CPU in seconds [NV, our design]; no hardware to ship, unlike Cropify's units [26] and Ground Truth "
        "Ag's ~CAD 15k benchtop [31].",
        "<b>Real costs are fixed:</b> two harvests of labelled French photos, calibration against a visual "
        "reference count, a pilot with 1-2 collectors, sales. Public calls fund this kind of work: the 2025 "
        "legume-chain call gave 11.7 M€ to 10 projects, ~1.2 M€ each on average [42] [V] [NV].",
        "<b>France revenue:</b> 10 % of the 477 protein-crop collectors at 1,500 € = ~72 k€/yr; all of "
        "them = ~0.72 M€/yr [NV, A4]. Plus the six soyfood plants as an early, concentrated market [6].",
        "<b>So the business is not France alone:</b> it is (a) licensing a soy and pulse module to an "
        "intake-desk incumbent that already sells per site and per credit (Inarix [28] [29]), or (b) the same "
        "product in other EU pulse markets, following Cropify's Australia-to-North-America path [26].",
    ])

    s.append(P("6.4 Price benchmarks: what a grade costs today", H3))
    s.append(table([
        ["Option", "Hardware", "Price", "Soy / pulses", "Source"],
        ["Manual count by the intake technician", "None", "~2-4 € labour, 10-20 min", "Yes", "[38] [F] [NV]"],
        ["Arbitration lab (Incograin)", "Lab", "130 € HT + 10 € handling", "Yes", "[37] [V]"],
        ["Ground Truth Ag", "Benchtop unit", "~CAD 15k + 1.5k/yr", "In development", "[31] [V]"],
        ["ZoomAgri", "Scanner", "~$15 per sample", "Soy claimed", "[47] [F]"],
        ["Nebulaa MATT", "Device", "Rs 150-200 per sample", "Pulses (India)", "[48] [F]"],
        ["Cropify", "Unit at sample stand", "Not public", "Lentil, chickpea", "[26] [V]"],
        ["Inarix", "Phone", "Licence + credits, on quote", "Cereals only", "[28] [V]"],
        ["<b>SoyMate</b>", "<b>Phone</b>", "<b>~1,500 €/yr per site [A4]</b>", "<b>Soy, then lentil</b>",
         "Our proposal"],
    ], [4.4, 2.8, 4.0, 3.0, 3.2]))

    # 7. Competition
    s.append(P("7. Competition and market proof", H2))
    s.append(table([
        ["Player", "What it does", "Soy or pulses?", "Price / model"],
        ["Cropify (AU)", "AI grading at receival: defective and discoloured grain, foreign material; digital "
         "record per load [26] [V]", "Lentil (2025), chickpea (2026), faba 2027; Canada and US next [26] [27] [V]",
         "Not public"],
        ["Inarix (FR)", "Phone photo: variety, protein, broken grains, TKW; ~600 silos, ~40 % of French "
         "barley [29] [V]", "Cereals only publicly [28] [V]; soybean variety R&D in Canada [29] [V]",
         "Licence per user + credits [28] [V]"],
        ["Ground Truth Ag (CA)", "Benchtop vision + NIR, 1-2 kg sample [30] [V]",
         "Peas, lentils, soy, faba \"in development\" [30] [V]", "~CAD 15k + 1.5k/yr [31] [V]"],
        ["Cgrain, FOSS EyeFoss", "Lab or intake imaging of grains [32] [33] [V]", "Small grains only",
         "Quote"],
        ["SeedCount", "Flatbed seed imaging [34] [V]", "Old lentil module", "Quote"],
        ["ZoomAgri (AR)", "Scanner imaging: barley purity, physical quality of grains [47] [V]",
         "Soy claimed in press, not verified [47] [F]", "~$15 per sample (press) [47] [F]"],
        ["Nebulaa MATT (IN)", "Image analysis of grains and pulses, ~1 min [48] [F]", "Pulses (India)",
         "Rs 150-200 per sample [48] [F]"],
        ["Optical sorters (Bühler, TOMRA)", "Sort pulses at packers", "Yes, but they sort, not grade",
         "Capital sale"],
    ], [3.2, 6.0, 5.0, 3.2], bold_first_col=True))
    s.append(Spacer(1, 4))
    s.append(P("<b>Threats:</b> Cropify is the same product, already recognised, expanding abroad. In France, "
               "Inarix already has the silos, phone capture, the licence-plus-credits model and the same DINOv2 "
               "backbone [29]; adding pulses would be a small step. <b>No technical moat:</b> \"not in France yet\" "
               "is a timing gap. <b>Differentiator:</b> phone only, no hardware, where Cropify installs units at "
               "sample stands [26] and Ground Truth Ag sells a benchtop unit [31]. <b>Realistic channel:</b> a "
               "pulse and soy defect module licensed to, or built with, an intake-desk incumbent.", BODY))

    # 8. Assumptions
    s.append(P("8. Assumptions register", H2))
    s.append(table([
        ["Id", "Assumption", "Value used", "Basis", "How to check"],
        ["A1", "Truck size", "28 t", "Common French semi-trailer load [A]", "Ask a collector"],
        ["A2", "Value of a lentil tonne outside the food outlet", "~250 €/t",
         "Feed protein-crop range 200 to 260 €/t [23] [V]; no feed-lentil price published",
         "Collector or packer price for downgraded lentil"],
        ["A3", "A faster, repeatable grade changes some decisions (sort, cell, contract) or prevents some "
         "disputes", "Not quantified",
         "Manual grading varies between people and sites [45] [V]; no French figure on how often a grade "
         "changes a decision or is contested", "Pilot: count decisions changed and disputes per 100 lots"],
        ["A4", "Subscription price per site", "1,500 \u20ac/yr (illustrative)",
         "Order of magnitude of Ground Truth Ag's CAD 1,500/yr fee [31] [V]; Cropify price not public; no "
         "payback is claimed", "Interviews with 3 collectors"],
        ["A5", "Lentil production", "40 to 59 kt",
         "34,216 ha [13] x 1.16 to 1.71 t/ha [18] [15] [NV]", "Official tonnage (none found for 2024-25)"],
        ["A6", "Soy food premium", "20 to 70 €/t", "[10] [11] [6]", "Current contracts"],
        ["A7", "% of damaged grains = % of lot weight lost to sorting", "1:1",
         "Simplification: holed grains weigh less, so the 5 to 8 M\u20ac sorting loss is an upper bound [NV]",
         "Weigh sorted fractions"],
        ["A8", "Contracts price visible damage", "Yes",
         "Visual counts are the reference method [36] [V]; infestation needs dissection",
         "Read Incograin addendum 7 bis (members only) [40]"],
        ["A9", "Transfer cost measured on soy (R3) predicts French lentil", "Hypothesis",
         "No public lentil defect data to test it", "Label ~500 French lentil grains per class"],
        ["A10", "Manual defect counts per lentil site per season", "150 / 300 / 600",
         "Not found; scales with trucks received", "Ask a collector"],
        ["A11", "Arbitrations avoided per site per season", "0 / 2 / 5",
         "Not found; arbitration costs 130 \u20ac HT + 10 \u20ac [37] [V]", "Ask a collector"],
        ["A12", "Wrong lentil allocations avoided per site per season", "0 / 0.1 / 0.5",
         "Not found; the key unknown behind A3", "Pilot: compare decisions with and without the tool"],
    ], [0.9, 3.6, 2.5, 6.0, 4.4]))

    # 9. Extensions
    s.append(P("9. Future extensions, ranked by evidence", H2))
    s.append(P("\"Strong\" means market data and a paying precedent exist; \"medium\" means a documented problem "
               "but a thin premium or no precedent; \"weak\" means plausible only. None is certain until tested "
               "on French photos.", SMALL))
    s.append(Spacer(1, 3))
    s.append(table([
        ["Extension", "Evidence", "Why", "What it needs"],
        ["Lentil reception grading: bruchid holes, broken, foreign material, pricing the sorting loss",
         "Strong", "~550 to 620 \u20ac/t at stake [NV]; highest damage of 2021-2025 in 2025 [15]; Cropify sells the same "
         "thing [26]",
         "French lentil photos labelled by graders; calibration against visual counts [36]"],
        ["Chickpea grading", "Medium-strong", "Cropify added chickpea in 2026 [26]; France grows 27,494 ha "
         "(2024) [13] [V] and is a net exporter", "Calibre and defect classes; export specs"],
        ["Food-soy intake check (green seeds, broken, stained, foreign seeds) for the six soyfood plants",
         "Medium", "Green seeds hurt the food outlet in 2025 [3]; concentrated buyers [6]; thin premium [10]",
         "Buyer specs; a pilot with one plant"],
        ["Faba bean for food export (Egypt <1 % bruchid)", "Medium", "Lost food export market 245 to 87 kt "
         "[21] [F]; strict thresholds [20] [V]", "Photo undercounts hidden larvae: pair with X-ray or "
         "dissection sampling"],
        ["Pea purity for fractionation (colour, broken, foreign seeds such as soy)", "Weak-medium",
         "Roquette grades colour, broken and purity [22] [F]; only ~30 €/t premium [25]",
         "Purity classes, not holes"],
        ["Producer-side check before delivery (our impact story: income and trust)", "Medium",
         "A grade the farmer can verify supports a fair r\u00e9faction [NV]; Track 3 asks about farmer income [1]",
         "Same model; a farmer app flow; the farmer needs ~1,000 grains too"],
        ["Packer QC before and after optical sorting", "Weak-medium", "Sorting is the standard fix [20] [V]; "
         "measures sorter efficiency [NV]", "Access to a packing line"],
        ["EU and other markets with the same crops", "Medium", "Cropify's own path: Australia, then Canada and "
         "the US [26] [V]", "Local standards and data per market"],
    ], [4.5, 2.4, 5.3, 5.2]))

    # 10. What we need
    s.append(P("10. What it takes to make it really useful", H2))
    s.append(P("From what incumbents and regulators already require [35] [39] [28]:", BODY))
    s += bullets([
        "<b>French data:</b> photos from intake desks, several sites and at least two harvests, labelled by graders "
        "(agréeurs). R3 tells us how many grains per class.",
        "<b>Enough grains per sample</b> (table in section 5): about 1,000 grains, i.e. several photos, gives "
        "\u00b12 to \u00b13 points at lentil damage levels; plus a correction for the classifier's own errors.",
        "<b>Calibration against the reference method:</b> LABOSEM-style visual counts, daily check samples, "
        "monthly comparisons, as the USDA grain inspection service requires for Cgrain [35] [V].",
        "<b>Fixed capture:</b> a cheap tray or light box and a short list of phones. Inarix restricts its "
        "broken-wheat analysis to two phone models [28] [V].",
        "<b>Traceability and integration:</b> sample ID, stored images, results on the intake ticket; otherwise "
        "it stays a side app [NV].",
        "<b>Industry recognition:</b> Incograin certified an Inarix barley method [29] [V]; GTA judged Cropify worth "
        "\"commercial consideration\" [26] [V]. Arbitration still goes to a handpick reference [35] [V], so the tool starts as a pre-screen "
        "and evidence record.",
        "<b>Public funding for pilots:</b> the 2025 \"Projets territoriaux fili\u00e8res l\u00e9gumineuses\" call "
        "funded 10 projects for 11.7 M\u20ac [42] [V]; France Relance put ~150 M\u20ac into plant proteins [18] [V].",
        "<b>A channel:</b> partnership with an intake-desk incumbent, or the six soyfood plants as a first "
        "concentrated customer base.",
    ])

    # 11. Critiques
    s.append(P("11. Critiques we must answer", H2))
    s.append(table([
        ["Critique", "Evidence", "Our answer"],
        ["\"Grading is not what holds French pulses back.\"", "Sources cite price vs imports, yield risk, "
         "missing sorting tools and low demand (1.6 kg/adult/yr vs ~5 kg for the PNNS guideline) [16] [17] [18] [V]",
         "True. We claim fairer pricing and trust at reception, not more demand. It supports farmer income "
         "(Track 3), not consumption."],
        ["\"Labour savings are tiny.\"", "Manual count ~2 to 4 \u20ac of labour [NV, 38]; lab impurity analysis "
         "130 \u20ac HT per lot [37] [V]", "Agreed. The value is decisions, disputes and speed (section 5), not "
         "labour."],
        ["\"A better grade just moves money from farmer to collector.\"", "If manual grading is unbiased, "
         "corrections cancel across trucks [NV]", "Agreed. We do not sell \u20ac per point. Value comes from "
         "decisions that change and disputes avoided, and must be measured in a pilot [A3]."],
        ["\"One photo is too noisy for a 1 % threshold.\"", "\u00b16 points at 25 % damage with 200 grains; "
         "~380 clean grains to show \u22641 % [NV]", "Agreed: the product asks for several photos (~1,000 "
         "grains) and says \"inconclusive\" near the threshold."],
        ["\"A photo misses bruchid larvae.\"", "Pea: 3.8 to 4.1 % visual vs 11.8 to 13.5 % by dissection [36] [V]",
         "We measure visible damage, the same thing the visual reference method counts, and say so."],
        ["\"Food soy barely pays more.\"", "<25 \u20ac/t gap [10] [11]", "Correct. Soy is where public data "
         "exists to build and audit the method; lentil is the target, still untested on real lentils."],
        ["\"Cropify already does it; Inarix could next season.\"", "[26] [27] [29]", "Proof that buyers pay. "
         "No technical moat: our edge is phone-only capture and being first on French soy and pulses, "
         "ideally with an incumbent as channel."],
        ["\"2025 was an extreme year.\"", "Lentil damage ~10 to 15 % in 2021-2024 [15]; soy green seeds 11 % "
         "in 2024 [3]", "The 5 to 8 M\u20ac figure is 2025 and an upper bound; a normal year is roughly half."],
        ["\"Soy is animal feed.\"", "~89 % of French soy is not food [2] [V]", "We target the food-grade "
         "channel only; the guide excludes feed projects [1]."],
    ], [4.2, 6.6, 6.6]))

    # 12. Open questions
    s.append(P("12. Still open (ask mentors or collectors)", H2))
    s += bullets([
        "Current food-grade thresholds in Incograin addenda 7 bis (pulses for food) and 9 (soybean); members only [40].",
        "A price for downgraded or feed lentil, and any réfaction grid for bruchid-damaged or broken grains.",
        "How intake grading is really done for pulses: per truck or composite, by whom, how long.",
        "Official 2024-2025 lentil and chickpea tonnage.",
        "Whether Inarix plans pulse or soy defect analyses.",
    ])

    # Sources
    s.append(PageBreak())
    s.append(P("Sources", H2))
    s.append(P("Opened on or before 31/10/2026. Full detail (what was read on each) in "
               "<font name='Courier'>research/viability/*.md</font> and <font name='Courier'>CONTEXT.md</font> §17.",
               SMALL))
    s.append(Spacer(1, 4))
    for i, (txt, url) in enumerate(SOURCES, 1):
        s.append(P(f"<b>[{i}]</b> {txt}" + (f" <font color='#616161'>{url}</font>" if url else ""), SMALL))
        s.append(Spacer(1, 1.5))

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.6 * cm, title="SoyMate: viability brief",
                            author="SoyMate team, Hack the Fork Paris 2026")
    doc.build(s, onFirstPage=on_page, onLaterPages=on_page)
    print("wrote", OUT)


SOURCES = [
    ("Hack the Fork, Participant Guide, Paris 2026 (event document).", ""),
    ("FranceAgriMer, Fiche filière Oléagineux 2026 (Feb. 2026).",
     "https://www.franceagrimer.fr/sites/default/files/2026-02/18_FICHE_FILIERE_OLEAGINEUX_2026.pdf"),
    ("Terres Inovia, Fiche qualité des graines soja, récolte 2025 (Apr. 2026).",
     "https://www.terresinovia.fr/sites/default/files/2026-04/fiche_qualite_graines-soja_2025.pdf"),
    ("Terres Univia, Chiffres clés 2024 (2025).", "https://www.terresunivia.fr/fichiers/publications/chiffres-cles-2024.pdf"),
    ("Eurostat, apro_cpsh1 (soya, France), queried 31/10/2026.",
     "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1?geo=FR&crops=I1130"),
    ("Ortega (Terres Univia) and Lecomte (Terres Inovia), \"Le marché français du soja\", Spécial Soja 2024.",
     "https://www.terresinovia.fr/sites/default/files/document_library/20126/437704/726505/special-soja-2024_vf.pdf"),
    ("Terres Inovia / ITAB, Guide de culture soja bio 2023, p. 21.",
     "https://www.terresinovia.fr/sites/default/files/2025-06/guide-de-culture-soja-bio-2023.pdf"),
    ("Institut Veblen, FNH, Terres Univia, Mesures miroirs, cas d'étude soja (~2024).",
     "https://www.veblen-institute.org/IMG/pdf/fiche_soja_vf.pdf"),
    ("Réussir, Marché des oléagineux du 30/9 au 7/10/2026 (quotes Agreste 2026 forecast), 9/10/2026.",
     "https://www.reussir.fr/articles/marche-des-oleagineux-et-coproduits-du-30-septembre-au-7-octobre-2026-les-prix-en-colza"),
    ("Terres Univia, Point éco 05-2025, Observatoire des prix payés aux producteurs de légumineuses.",
     "https://www.terresunivia.fr/fichiers/publications/PE[05-2025]_web.pdf"),
    ("La France Agricole, \"Les prix payés aux producteurs de légumineuses à graines ont progressé\", 12/5/2025 (paywall, visible part).",
     "https://www.lafranceagricole.fr/conjoncture-cultures/article/882292/les-prix-payes-aux-producteurs-de-legumineuses-a-graine-ont-progresse"),
    ("RAGT Seeds, interview of Y.-M. Milbeau (Olga), 17/1/2023.",
     "https://ragt-seeds.com/fr/soja-interview-de-m-yves-marie-milbeau-olga/"),
    ("Terres Univia, Statistiques Oléagineux & Plantes Riches en Protéines (2024 data).",
     "https://www.terresunivia.fr/fichiers/publications/recueil-statistiques-2024-3.pdf"),
    ("FranceAgriMer, Fiche filière Protéagineux 2026 (Jan. 2026).",
     "https://www.franceagrimer.fr/sites/default/files/2026-02/19_FICHE_FILIERE_PROTEAGINEUX_2026.pdf"),
    ("Terres Univia / Terres Inovia, Lentille, fiche qualité des graines, récolte 2025 (erratum).",
     "https://www.terresunivia.fr/fichiers/publications/qualite-graines-lentille-2025-erratum.pdf"),
    ("Terres Univia, Consommation de légumineuses des Français: résultats Nutrimétrie (27/5/2026).",
     "https://www.terresunivia.fr/l-interprofession/actualites/consommation-de-legumineuses-des-francais-resultats-de-letude-nutrimetrie"),
    ("Solagro / Réseau Action Climat, Les légumes secs: quelles initiatives territoriales? (c. 2015-2016).",
     "https://agriculture.gouv.fr/sites/minagri/files/f77_publi-legumes-secs-web-2.pdf"),
    ("France Stratégie, évaluation France Relance, fiche Protéines végétales, Jan. 2024.",
     "https://www.strategie-plan.gouv.fr/files/files/Publications/Rapport/fs-2024-rapport-france_relance_vol_ii_10_proteines_vegetales_0.pdf"),
    ("FranceAgriMer, communiqué 6/7/2026, appel à projets obtention variétale légumineuses.",
     "https://www.franceagrimer.fr/sites/default/files/2026-07/06072026_CP_FranceAgriMer_AAP_Obtention_vari%C3%A9tale_l%C3%A9gumineuses_2026.pdf"),
    ("Perspectives Agricoles n°467, June 2019, \"Lutter contre les bruches des légumineuses\" (Terres Inovia).",
     "https://ecophytopic.fr/sites/default/files/2021-03/2019_06_PA467-68-bruches-legumineuses.pdf"),
    ("Réussir / La Dépêche, \"Terres Inovia: le salut de la féverole passe par les OS\", 8/9/2015.",
     "https://www.reussir.fr/ladepeche/terres-inovia-le-salut-de-la-feverole-passe-par-les-os"),
    ("Réussir, \"Les pois jaunes, une culture exigeante mais rentable\", 4/1/2021.",
     "https://www.reussir.fr/les-pois-jaunes-une-culture-exigeante-mais-rentable"),
    ("CRIT Grand Est, Référentiel de prix et de charges 2025 (DRAAF Grand Est), 16/4/2025.",
     "https://draaf.grand-est.agriculture.gouv.fr/IMG/pdf/crit_16_avril_2025___annexe_2___referentiel_des_prix_crit_2025.pdf"),
    ("FranceAgriMer, prix payés aux producteurs trimestriels (lentil 873 €/t 2024/25, 806 €/t 2025/26). Source : FranceAgriMer.",
     "https://visionet.franceagrimer.fr (SCR-CER-HISTOPRIXTRIMESTRIELS-C25-26.xlsx)"),
    ("Terres Inovia, Pois protéagineux, guide de culture 2025 (indicative prices 250 / 280 €/t).",
     "https://www.germineo.com/storage/cms/FT%20-%20Semences%20Ol%C3%A9agineux,%20prot%C3%A9agineux/POIS-PROTEAG.-2025-Guide-culture-TERRES-INOVIA.pdf"),
    ("ChannelLife, \"Cropify AI lentil grading to go commercial this harvest\", 20/8/2026.",
     "https://channellife.com.au/story/cropify-ai-lentil-grading-to-go-commercial-this-harvest"),
    ("Stock Journal, \"Cropify Opal AI tool grades grain in 5.3 minutes\", 4/9/2026.",
     "https://www.stockjournal.com.au/story/9341950/cropify-opal-ai-tool-grades-grain-in-53-minutes-boosts-farm-pay/"),
    ("Inarix, home, get-started and product pages, read 31/10/2026.", "https://inarix.com/"),
    ("Meta AI blog, \"Inarix... DINOv2\", 6/12/2024.",
     "https://ai.meta.com/blog/inarix-agricultural-supply-chain-meta-dino-v2/"),
    ("Ground Truth Ag, home page, read 31/10/2026.", "https://www.groundtruth.ag/"),
    ("The Western Producer, \"High-tech grain grader wins people's choice award\", 30/11/2023.",
     "https://www.producer.com/crops/high-tech-grain-grader-wins-peoples-choice-award/"),
    ("Cgrain, applications page, read 31/10/2026.", "https://www.cgrain.ai/applications"),
    ("FOSS, EyeFoss product page, read 31/10/2026.", "https://www.fossanalytics.com/en/products/eyefoss"),
    ("Next Instruments, SeedCount brochure (undated).",
     "https://cdn.labwrench.com/eMan/manualNo/10873/seedcount%20image%20analyzer%20brochure.pdf"),
    ("USDA AMS FGIS, Program Notice PN-26-03, Cgrain Value for whole kernels, 27/4/2026.",
     "https://www.ams.usda.gov/sites/default/files/media/PN2603_CgrainforWholeKernels.pdf"),
    ("F. Pavy (LABOSEM), \"Analyse de grains bruchés\", JIT Céréales et protéagineux, 10/3/2022.",
     "https://www.semae.fr/uploads/10-2022-jitcerpro_methode-grains-bruches_FP_CEK_MB.pdf"),
    ("Syndicat de Paris (Incograin), tarif des analyses (file 2021, linked in 2026).",
     "https://www.incograin.com/wp-content/uploads/2021/05/TARIF-SP.pdf"),
    ("France Travail job offers for seasonal silo agents (~2025), search snippets [F].", ""),
    ("Inarix help centre, \"Data Enrichment: Master Sites\", updated 24/4/2026.",
     "https://inarix.zendesk.com/hc/en-001/articles/32424124861213-Data-Enrichment-Master-Sites"),
    ("Incograin, Syndicat page (contract forms RUFRA, RULEGS; addenda 7, 7 bis, 9 members only).",
     "https://www.incograin.com/index.php/syndicat-incograin/"),
    ("Canadian Grain Commission, Official Grain Grading Guide, lentils, grade determination tables.",
     "https://www.canada.ca/en/grain-commission/services/grain-quality/official-grain-grading-guide/18-lentils/primary-export-grade-determination-tables.html"),
    ("Ministère de l'Agriculture, communiqué \"11,7 M€... souveraineté protéique\", 2/7/2025.",
     "https://agriculture.gouv.fr/telecharger/150164"),
    ("SoyMate dataset audits: CONTEXT.md §6, research/soybean_bruchid/findings.md, "
     "research/other_datasets/findings.md and new_candidates.md (Mendeley d97rjyk2tz, v6vzvfszj6, t94nzy4ptz, "
     "hwdtghttp7, c733bjz4m3; Radio_lentille on Hugging Face, JeanEudesH/Radio_lentille).", ""),
    ("Terres Inovia / Terres Univia, Pois, qualit\u00e9 des graines 2025 (Jan. 2026).",
     "https://www.terresinovia.fr/sites/default/files/2026-01/fiche_terres_inovia_qual_graines_pois2025.pdf"),
    ("Farm Online, \"AI revolutionises pulse sampling with better accuracy on colour\", 20/3/2025.",
     "https://www.farmonline.com.au/story/8921581/ai-revolutionises-pulse-sampling-with-better-accuracy-on-colour/"),
    ("Grain Central, Cropify endorsement article, 20/8/2026 (search snippet only, site blocked automated access) [F].",
     "https://www.graincentral.com/?p=251800"),
    ("ZoomAgri: Grains West 2/9/2025 and press on pricing (snippets) [F].",
     "https://grainswest.com/2025/09/ai-revolution-improves-analysis/"),
    ("Nebulaa MATT: Outlook Business and Business Today (~2018, snippets) [F].",
     "https://www.outlookbusiness.com/big-idea/quality-check-4792"),
]

if __name__ == "__main__":
    build()
