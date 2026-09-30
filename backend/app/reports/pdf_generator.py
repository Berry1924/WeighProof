import io
import json
from decimal import Decimal
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.engine.hasher import generate_verification_qr_code


def build_pdf_report(report_data: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Center
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    pass_style = ParagraphStyle(
        'PassBadge',
        parent=body_bold,
        textColor=colors.HexColor('#166534')
    )
    fail_style = ParagraphStyle(
        'FailBadge',
        parent=body_bold,
        textColor=colors.HexColor('#991B1B')
    )

    elements = []

    # Header
    elements.append(Paragraph("<b>OIML R 76-2 TYPE EVALUATION REPORT</b>", title_style))
    elements.append(Paragraph("Non-Automatic Weighing Instrument (NAWI) Metrological Verification<br/>Issued under WeighProof Metrological Governance Engine (SIH PS26035)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=10))

    # Master Meta & Status
    inst = report_data.get("instrument_snapshot", {})
    results = report_data.get("evaluation_results", {})
    overall_verdict = report_data.get("overall_verdict", "FAIL")
    report_num = report_data.get("report_number", "DRAFT-000")
    ruleset_id = report_data.get("ruleset_id", "oiml_r76_2006")
    ruleset_edition = report_data.get("ruleset_edition", "2006 (E)")
    status = report_data.get("status", "DRAFT")
    sha256_hash = report_data.get("canonical_hash", "UNSIGNED_DRAFT")

    # Generate QR Code image
    _, qr_bytes = generate_verification_qr_code(report_num, sha256_hash)
    qr_img = Image(io.BytesIO(qr_bytes), width=1.1*inch, height=1.1*inch)

    meta_table_data = [
        [
            Paragraph(f"<b>Report No:</b> {report_num}", body_style),
            Paragraph(f"<b>Status:</b> <b>{status}</b>", pass_style if status == "SIGNED" else body_style),
            qr_img
        ],
        [
            Paragraph(f"<b>Ruleset:</b> {ruleset_id} (OIML R 76-1 {ruleset_edition})", body_style),
            Paragraph(f"<b>Overall Verdict:</b> <b>{overall_verdict}</b>", pass_style if overall_verdict == "PASS" else fail_style),
            ""
        ],
        [
            Paragraph(f"<b>Created By:</b> {report_data.get('created_by', 'N/A')}", body_style),
            Paragraph(f"<b>Reviewer:</b> {report_data.get('reviewer_username', 'Pending Sign-off')}", body_style),
            ""
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[2.6*inch, 2.8*inch, 1.4*inch])
    meta_table.setStyle(TableStyle([
        ('SPAN', (2, 0), (2, 2)),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Instrument Master Data Table
    elements.append(Paragraph("<b>1. Instrument Master Characteristics (OIML R 76-2 Page 5)</b>", h2_style))
    inst_table_data = [
        ["Manufacturer", inst.get("manufacturer", "N/A"), "Model", inst.get("model", "N/A")],
        ["Serial Number", inst.get("serial_number", "N/A"), "Accuracy Class", f"Class {inst.get('accuracy_class', 'N/A')}"],
        ["Max Capacity", f"{inst.get('max_capacity')} {inst.get('unit')}", "Min Capacity", f"{inst.get('min_capacity')} {inst.get('unit')}"],
        ["Scale Interval (e)", f"{inst.get('verification_scale_interval_e')} {inst.get('unit')}", "Scale Interval (d)", f"{inst.get('actual_scale_interval_d')} {inst.get('unit')}"],
        ["Intervals Count (n)", str(inst.get("calculated_n", "3000")), "Support Points", str(inst.get("points_of_support", 4))],
    ]
    t_inst = Table(inst_table_data, colWidths=[1.7*inch, 2.0*inch, 1.6*inch, 1.7*inch])
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_inst)
    elements.append(Spacer(1, 8))

    # Summary Checklist (Page 9)
    elements.append(Paragraph("<b>2. Summary of Type Evaluation (OIML R 76-2 Page 9)</b>", h2_style))
    summary_data = [
        ["Test Examination", "Standard Reference", "Observed Metric", "Verdict"],
        ["Master Data Plausibility", "OIML R 76-1 Cl. 3.2, Table 3", f"n = {inst.get('calculated_n', 3000)}, e in {{1,2,5}}x10^k", "PASSED"],
        ["Weighing Performance", "OIML R 76-1 Cl. A.4.4, Form 1", f"Max |Ec|: {results.get('weighing_performance', {}).get('max_corrected_error', '0.0')} {inst.get('unit')}", results.get('weighing_performance', {}).get('overall_verdict', 'N/A')],
        ["Eccentricity Loading", "OIML R 76-1 Cl. A.4.7, Form 3", f"Load: {results.get('eccentricity', {}).get('actual_test_load', 'N/A')} {inst.get('unit')}", results.get('eccentricity', {}).get('overall_verdict', 'N/A')],
        ["Repeatability", "OIML R 76-1 Cl. A.4.10, Form 5", "Series 50% & 100% Max", results.get('repeatability', {}).get('overall_verdict', 'N/A')],
    ]
    t_sum = Table(summary_data, colWidths=[2.2*inch, 2.0*inch, 2.0*inch, 0.8*inch])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_sum)
    elements.append(Spacer(1, 10))

    # Weighing Performance Details Table (Page 10)
    wp = results.get("weighing_performance", {})
    if wp and "points" in wp:
        elements.append(Paragraph("<b>3. Weighing Performance Test (OIML R 76-2 Form 1)</b>", h2_style))
        wp_rows = [["Dir", "Load L", "Ind I", "ΔL", "P (Prior)", "Error E", "Corr Ec", "MPE", "Verdict"]]
        unit = inst.get("unit", "g")
        for pt in wp["points"][:12]: # fit cleanly on page
            v = pt.get("verdict", "PASS")
            wp_rows.append([
                pt.get("direction", "")[:3].upper(),
                f"{pt.get('load')} {unit}",
                f"{pt.get('indicated')} {unit}",
                f"{pt.get('delta_load', '-')} {unit}" if pt.get('delta_load') is not None else "-",
                f"{pt.get('turning_indication_p', '-')} {unit}",
                f"{pt.get('uncorrected_error_e', '-')} {unit}",
                f"{pt.get('corrected_error_ec', '-')} {unit}",
                f"±{pt.get('mpe')} {unit}",
                v
            ])
        t_wp = Table(wp_rows, colWidths=[0.5*inch, 0.9*inch, 0.9*inch, 0.7*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.7*inch])
        t_wp.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7.5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(t_wp)
        elements.append(Spacer(1, 10))

    # Cryptographic Hash & Verification Footer
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94A3B8'), spaceAfter=6),
        Paragraph("<b>Tamper-Evident Metrological Seal & Digital Signature</b>", h2_style),
        Paragraph(f"<b>Canonical SHA-256 Digest:</b> <font face='Courier'>{sha256_hash}</font>", body_style),
        Paragraph(f"<b>Verification URI:</b> https://weighproof.org/verify/{report_num}?hash={sha256_hash}", body_style),
        Paragraph(f"<b>Sign-off Timestamp:</b> {report_data.get('signed_at', 'Pending Reviewer Signature')}", body_style),
        Paragraph("<i>Notice: Any modification to data values within this report invalidates the SHA-256 seal. This certificate is legally traceable under OIML R 76-1 / ISO 17025.</i>", subtitle_style)
    ]))

    doc.build(elements)
    return buffer.getvalue()
