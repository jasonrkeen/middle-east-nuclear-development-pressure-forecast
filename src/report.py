from __future__ import annotations

from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from . import __version__


NAVY = colors.HexColor("#17324D")
BLUE = colors.HexColor("#2E6F95")
LIGHT = colors.HexColor("#EAF0F4")
GOLD = colors.HexColor("#E9C46A")
RED = colors.HexColor("#D65A4A")
GRAY = colors.HexColor("#657786")


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleNavy", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=27, textColor=NAVY, alignment=TA_LEFT, spaceAfter=10))
    styles.add(ParagraphStyle(name="Deck", parent=styles["Normal"], fontName="Helvetica", fontSize=11.5, leading=16, textColor=GRAY, spaceAfter=14))
    styles.add(ParagraphStyle(name="H1Navy", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=8, spaceAfter=8))
    styles.add(ParagraphStyle(name="H2Blue", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.5, leading=16, textColor=BLUE, spaceBefore=7, spaceAfter=5))
    styles.add(ParagraphStyle(name="Body9", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13, textColor=colors.HexColor("#263238"), spaceAfter=7))
    styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5, leading=10, textColor=GRAY, spaceAfter=4))
    styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=12.2, leading=17, textColor=NAVY, backColor=LIGHT, borderPadding=10, spaceBefore=5, spaceAfter=12))
    return styles


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#D5DEE5"))
    canvas.line(0.65 * inch, 0.55 * inch, width - 0.65 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawString(0.65 * inch, 0.36 * inch, f"Middle East Nuclear Development Pressure Forecast | v{__version__}")
    canvas.drawRightString(width - 0.65 * inch, 0.36 * inch, f"Page {doc.page}")
    canvas.restoreState()


def _table(data, widths, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.6),
        ("LEADING", (0, 0), (-1, -1), 9.5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8D2DA")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        commands.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    table.setStyle(TableStyle(commands))
    return table


def build_report(
    output_path: Path,
    index_summary: pd.DataFrame,
    scenario_summary: pd.DataFrame,
    regional_summary: pd.DataFrame,
    sensitivity: pd.DataFrame,
    economic_exposure: pd.DataFrame,
    chart_dir: Path,
    simulations: int,
    seed: int,
    as_of: str,
    source_freshness: pd.DataFrame,
    calibration_status: pd.DataFrame,
    structural_validation: pd.DataFrame,
    evidence_audit: pd.DataFrame,
    baseline_comparison: pd.DataFrame,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    styles = _styles()
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.62 * inch,
        bottomMargin=0.7 * inch,
        title="Middle East Nuclear Development Pressure Forecast",
        author="Jason Keen",
        subject="Conditional OSINT scenario forecast",
    )

    twelve = scenario_summary[scenario_summary["horizon_months"] == 12].set_index("scenario")
    push = twelve.loc["Combined push toward latency or weaponization"]
    leading = twelve.drop(index="Combined push toward latency or weaponization")["mean_probability_pct"].idxmax()
    lead_prob = twelve.loc[leading, "mean_probability_pct"]

    story = [
        Paragraph("Middle East Nuclear Development Pressure Forecast", styles["TitleNavy"]),
        Paragraph("Iran-Israel-Gulf conflict | Conditional OSINT assessment | Evidence through " + as_of, styles["Deck"]),
        Paragraph(
            f"The current evidence produces a <font color='#D65A4A'>{push['mean_probability_pct']:.1f}%</font> mean 12-month probability of a push toward greater nuclear latency or a weaponization decision. The leading pathway is <i>{leading.lower()}</i> at {lead_prob:.1f}%.",
            styles["Callout"],
        ),
        Paragraph("Key judgment", styles["H1Navy"]),
        Paragraph(
            "Conflict-driven motivation is rising faster than verified technical capability, while observability has deteriorated. This creates a high-pressure but highly uncertain environment: military damage can delay technical progress at the same time that attacks strengthen the perceived value of a strategic deterrent.",
            styles["Body9"],
        ),
        Paragraph("What the model does - and does not do", styles["H2Blue"]),
        Paragraph(
            "The model estimates strategic pathways from public evidence. It does not claim that Iran has decided to build a weapon, does not estimate weapon design details, and does not treat missing inspections as proof of weaponization. Low observability widens uncertainty and shifts weight toward opaque pathways.",
            styles["Body9"],
        ),
        Image(str(chart_dir / "scenario_probabilities.png"), width=7.05 * inch, height=3.76 * inch),
        Paragraph(
            f"Simulation settings: {simulations:,} Monte Carlo draws; reproducible seed {seed}. Probabilities are preliminary analytic estimates, not observed frequencies.",
            styles["Small"],
        ),
        PageBreak(),
        Paragraph("Current evidence structure", styles["H1Navy"]),
        Image(str(chart_dir / "evidence_indices.png"), width=7.0 * inch, height=4.13 * inch),
    ]

    index_data = [["Index", "Mean", "P05", "P95"]]
    for row in index_summary.itertuples(index=False):
        index_data.append([row.index, f"{row.mean:.1f}", f"{row.p05:.1f}", f"{row.p95:.1f}"])
    story.extend(
        [
            _table(index_data, [3.45 * inch, 0.85 * inch, 0.85 * inch, 0.85 * inch]),
            Spacer(1, 8),
            Paragraph(
                "Interpretation: strategic incentive and economic constraint can both be high. The former increases demand for deterrence; the latter reduces implementation capacity and can increase the attraction of negotiations. Verification observability is a confidence-control variable, not a direct measure of prohibited activity.",
                styles["Body9"],
            ),
            PageBreak(),
            Paragraph("Regional cascade assessment", styles["H1Navy"]),
            Paragraph(
                "The regional score measures pressure to expand hedging, latency, or strategic nuclear options. It is not the probability that a state will acquire a weapon.",
                styles["Body9"],
            ),
            Image(str(chart_dir / "regional_pressure.png"), width=7.0 * inch, height=3.83 * inch),
        ]
    )
    actor_data = [["Actor", "Pressure", "Band", "Analytic role"]]
    for row in regional_summary.itertuples(index=False):
        actor_data.append([row.actor, f"{row.mean_pressure:.1f}", row.classification, Paragraph(row.analytic_role, styles["Small"])])
    story.extend([_table(actor_data, [1.05 * inch, 0.8 * inch, 0.8 * inch, 3.7 * inch]), PageBreak()])

    story.extend(
        [
            Paragraph("Economic transmission layer", styles["H1Navy"]),
            Paragraph(
                "This layer connects the strategic forecast to energy, shipping, defense expenditure, sovereign risk, and civil nuclear investment. Values are conditional exposure indices designed to interface with a separate market model; they are not price forecasts.",
                styles["Body9"],
            ),
            Image(str(chart_dir / "economic_exposure.png"), width=7.0 * inch, height=4.06 * inch),
        ]
    )
    econ_data = [["Horizon", "Exposure metric", "Index"]]
    for row in economic_exposure.itertuples(index=False):
        econ_data.append([f"{row.horizon_months} months", row.metric.replace("_", " ").title(), f"{row.probability_weighted_exposure_index:.1f}"])
    story.extend([_table(econ_data, [1.0 * inch, 3.9 * inch, 0.9 * inch]), PageBreak()])

    top_sensitivity = sensitivity.reindex(sensitivity["change_from_baseline_pct_points"].abs().sort_values(ascending=False).index).head(10)
    sensitivity_data = [["Indicator shock", "Push probability", "Change"]]
    for row in top_sensitivity.itertuples(index=False):
        label = row.indicator.replace("_", " ").title() + f" ({row.shock_points:+.0f})"
        sensitivity_data.append([label, f"{row.push_probability_pct:.1f}%", f"{row.change_from_baseline_pct_points:+.1f} pp"])

    scenario_data = [["12-month pathway", "Mean", "P05-P95"]]
    for scenario, row in twelve.drop(index="Combined push toward latency or weaponization").iterrows():
        scenario_data.append([scenario, f"{row.mean_probability_pct:.1f}%", f"{row.p05_pct:.1f}-{row.p95_pct:.1f}%"])

    story.extend(
        [
            Paragraph("Sensitivity and monitoring", styles["H1Navy"]),
            Paragraph("Largest modeled changes to the 12-month push probability from a 10-point indicator shock:", styles["Body9"]),
            _table(sensitivity_data, [3.55 * inch, 1.2 * inch, 1.1 * inch]),
            Spacer(1, 10),
            Paragraph("Scenario probability table", styles["H2Blue"]),
            _table(scenario_data, [3.55 * inch, 0.9 * inch, 1.3 * inch]),
            Spacer(1, 10),
            Paragraph("Priority indicators for updating", styles["H2Blue"]),
            Paragraph(
                "1. Restored IAEA access and verified material accountancy.<br/>2. Evidence of a durable nuclear agreement with enforceable monitoring.<br/>3. Confirmed facility reconstruction or continuing enrichment.<br/>4. Leadership statements that alter official nuclear doctrine.<br/>5. Saudi, Turkish, Egyptian, or UAE changes to safeguards, enrichment policy, or security guarantees.<br/>6. Changes in conflict intensity, sanctions, oil exports, or regime stability.",
                styles["Body9"],
            ),
            Paragraph("Confidence assessment", styles["H2Blue"]),
            Paragraph(
                "Direction of strategic incentive: moderate confidence. Technical capability continuity: low confidence. Regional cascade ordering: low-to-moderate confidence. Overall scenario probabilities remain preliminary because the conflict regime is new and the frozen forecasts have not matured.",
                styles["Body9"],
            ),
            PageBreak(),
            Paragraph("Validation and update governance", styles["H1Navy"]),
        ]
    )

    passed = int(structural_validation["passed"].sum())
    overdue = int((source_freshness["freshness_status"] == "overdue").sum())
    current = int((source_freshness["freshness_status"] == "current").sum())
    scored = int((calibration_status["score_status"] == "scored").sum())
    open_forecasts = int((calibration_status["score_status"] == "open_not_matured").sum())
    applied_updates = int((evidence_audit.get("status", pd.Series(dtype=str)) == "applied").sum())
    max_change = float(baseline_comparison["change_pct_points"].abs().max())

    governance_data = [
        ["Control", "Result", "Interpretation"],
        ["Structural validation", f"{passed}/{len(structural_validation)} passed", "Synthetic edge cases; not a historical backtest"],
        ["Source freshness", f"{current} current; {overdue} overdue", "Limits vary by source role"],
        ["Forecast registry", f"{scored} scored; {open_forecasts} open", "Scoring begins only after target dates and adjudication"],
        ["Evidence updates", f"{applied_updates} applied", "Accepted updates are confidence-discounted"],
        ["v0.1 baseline drift", f"{max_change:.3f} pp maximum", "No evidence update means only Monte Carlo rounding drift"],
    ]
    structural_data = [["Case", "Expected", "Dominant", "Result"]]
    for row in structural_validation.itertuples(index=False):
        structural_data.append(
            [
                row.case_id,
                Paragraph(row.expected_scenario, styles["Small"]),
                Paragraph(row.dominant_scenario, styles["Small"]),
                "Pass" if row.passed else "Review",
            ]
        )
    registry_data = [["Horizon", "Target date", "Status"]]
    for row in calibration_status.itertuples(index=False):
        registry_data.append(
            [f"{row.horizon_months} months", str(row.target_date), row.score_status.replace("_", " ")]
        )

    story.extend(
        [
            Paragraph(
                "Version 0.2 separates validation of model behavior from measurement of forecast performance. It freezes issued probabilities before outcomes are known, preventing a hindsight backtest from being presented as calibration evidence.",
                styles["Body9"],
            ),
            _table(governance_data, [1.25 * inch, 1.25 * inch, 3.8 * inch]),
            Spacer(1, 10),
            Paragraph("Structural validation cases", styles["H2Blue"]),
            _table(structural_data, [0.55 * inch, 2.15 * inch, 2.15 * inch, 0.65 * inch]),
            Spacer(1, 10),
            Paragraph("Frozen forecast registry", styles["H2Blue"]),
            _table(registry_data, [1.1 * inch, 1.35 * inch, 2.4 * inch]),
            Paragraph(
                "Brier score and log loss are intentionally blank until a forecast target date passes and the realized scenario is independently adjudicated. This is a feature of the governance design, not missing analysis.",
                styles["Small"],
            ),
            PageBreak(),
            Paragraph("Methodology and source notes", styles["H1Navy"]),
            Paragraph(
                "The engine applies any accepted, dated evidence adjustments to the preserved baseline; confidence discounts the adjustment magnitude. It then samples indicators from bounded normal distributions, calculates six weighted indices, and converts standardized deviations into mutually exclusive scenario probabilities using a softmax transformation. Scenario priors are set independently for 12, 24, and 36 months. Regional actors use a separate incentive-capability-restraint model. All values remain editable in CSV files with audit outputs.",
                styles["Body9"],
            ),
            Paragraph("Primary source anchors", styles["H2Blue"]),
            Paragraph(
                "<link href='https://www.iaea.org/sites/default/files/gov2026-33.pdf' color='#2E6F95'>IAEA GOV/2026/33</link> (4 June 2026)<br/>"
                "<link href='https://www.iaea.org/newscenter/statements/iaea-director-generals-introductory-statement-to-the-board-of-governors-8-june-2026' color='#2E6F95'>IAEA Director General statement</link> (8 June 2026)<br/>"
                "<link href='https://press.un.org/en/2026/sc16382.doc.htm' color='#2E6F95'>UN Security Council Iran nuclear coverage</link> (9 June 2026)<br/>"
                "<link href='https://www.sipri.org/media/press-release/2026/increasing-focus-nuclear-weapons-amid-heightened-escalation-risks-new-sipri-yearbook-out-now' color='#2E6F95'>SIPRI Yearbook 2026 release</link> (8 June 2026)<br/>"
                "<link href='https://www.iaea.org/topics/additional-protocol' color='#2E6F95'>IAEA safeguards framework</link>",
                styles["Small"],
            ),
            Paragraph("Current conflict context", styles["H2Blue"]),
            Paragraph(
                "<link href='https://www.reuters.com/world/middle-east/iran-says-tehran-must-overcome-unjust-sanctions-us-ramps-up-economic-pressure-2026-08-21/' color='#2E6F95'>Reuters: Iran sanctions and economic pressure</link> (21 August 2026)<br/>"
                "<link href='https://www.reuters.com/world/middle-east/iran-threatens-go-offensive-strait-hormuz-if-diplomacy-with-us-fails-2026-08-17/' color='#2E6F95'>Reuters: conflict posture and stalled diplomacy</link> (17 August 2026)",
                styles["Small"],
            ),
            Spacer(1, 12),
            Paragraph(
                "Prepared as an open-source strategic decision-support product. It is not a statement of government intent, not a substitute for classified intelligence, and not investment advice.",
                styles["Callout"],
            ),
        ]
    )

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
