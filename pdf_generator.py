from __future__ import annotations

from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


def _format_duration(contract_months: int) -> str:
    if contract_months % 12 == 0:
        years = contract_months // 12
        return f"{years} year{'s' if years > 1 else ''}"
    return f"{contract_months} month{'s' if contract_months > 1 else ''}"


def generate_contract(data: dict) -> bytes:
    streamer_handle = data["streamer_handle"].strip()
    streamer_legal_name = data["streamer_legal_name"].strip()
    streamer_govt_id = data["streamer_govt_id"].strip()
    effective_date = data.get("effective_date") or date.today().strftime("%d/%m/%Y")
    contract_months = int(data.get("contract_months", 12))
    contract_duration_str = _format_duration(contract_months)

    fee_type = data.get("fee_type", "Dynamic")
    fee_percentage = str(data.get("fee_percentage", "")).strip()

    if fee_type == "Fixed %":
        pct = fee_percentage or "0"
        fee_display = f"{pct}% of gross transaction value"
        fee_clause = (
            f"3.1 <b>Revenue Share / Platform Fee:</b> The Streamer shall receive payouts after deduction of a platform "
            f"fee of <b>{pct}%</b> of gross transaction value processed through the platform. This rate shall be "
            f"communicated transparently within the platform dashboard or reporting."
        )
    else:
        fee_display = "dynamic based on feature usage"
        fee_clause = (
            "3.1 <b>Revenue Share / Platform Fee:</b> The Streamer shall receive payouts after deduction of platform "
            "charges based on features utilized. The exact percentage or fee structure may vary depending on features "
            "enabled, tools used, or monetization methods selected by the Streamer, and shall be communicated "
            "transparently within the platform dashboard or reporting."
        )

    _ = fee_display

    PAGE_W, PAGE_H = A4
    MARGIN = 2.5 * cm
    HEADER_H = 2.8 * cm
    FOOTER_H = 1.6 * cm

    BRAND_DARK = colors.HexColor("#1a1a2e")
    BRAND_ACCENT = colors.HexColor("#6c63ff")
    GREY = colors.HexColor("#666666")
    LIGHT_GREY = colors.HexColor("#cccccc")

    def draw_letterhead(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BRAND_ACCENT)
        canvas.rect(0, PAGE_H - 0.45 * cm, PAGE_W, 0.45 * cm, fill=1, stroke=0)
        canvas.setFont("Helvetica-Bold", 15)
        canvas.setFillColor(BRAND_DARK)
        canvas.drawString(MARGIN, PAGE_H - 1.35 * cm, "HyperChat")
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN, PAGE_H - 1.85 * cm, "by Streamheart Private Limited")
        canvas.setFont("Helvetica-Oblique", 8)
        canvas.setFillColor(GREY)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.35 * cm, "Streamer Partnership Agreement")
        canvas.setFont("Helvetica", 7.5)
        canvas.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.75 * cm, "Confidential")
        canvas.setStrokeColor(BRAND_ACCENT)
        canvas.setLineWidth(1.2)
        canvas.line(MARGIN, PAGE_H - 2.15 * cm, PAGE_W - MARGIN, PAGE_H - 2.15 * cm)
        canvas.setStrokeColor(LIGHT_GREY)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, FOOTER_H, PAGE_W - MARGIN, FOOTER_H)
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(GREY)
        canvas.drawString(
            MARGIN,
            FOOTER_H - 0.45 * cm,
            "G-478, G Block, Govindpuram Park, Block 1, Govindpuram, Ghaziabad, Uttar Pradesh – 201013, India",
        )
        canvas.drawString(MARGIN, FOOTER_H - 0.85 * cm, "ankit.hyperchat@gmail.com")
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawRightString(PAGE_W - MARGIN, FOOTER_H - 0.45 * cm, f"Page {doc.page}")
        canvas.setFillColor(BRAND_ACCENT)
        canvas.rect(0, 0, PAGE_W, 0.3 * cm, fill=1, stroke=0)
        canvas.restoreState()

    output = BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=HEADER_H + 0.6 * cm,
        bottomMargin=FOOTER_H + 0.8 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CT",
        parent=styles["Title"],
        fontSize=15,
        fontName="Helvetica-Bold",
        textColor=BRAND_DARK,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CS",
        parent=styles["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=GREY,
        spaceAfter=4,
        alignment=TA_CENTER,
    )
    heading1_style = ParagraphStyle(
        "H1", parent=styles["Heading1"], fontSize=10.5, fontName="Helvetica-Bold", textColor=BRAND_DARK, spaceBefore=12, spaceAfter=5
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9.5,
        fontName="Helvetica",
        textColor=colors.HexColor("#222222"),
        spaceAfter=5,
        leading=14,
        alignment=TA_JUSTIFY,
    )
    bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=18, bulletIndent=6, spaceAfter=3)
    party_style = ParagraphStyle("Party", parent=body_style, leftIndent=20, spaceAfter=3)

    story = []

    story.append(Paragraph("STREAMER PARTNERSHIP AGREEMENT", title_style))
    story.append(Paragraph(f"HyperChat by Streamheart Private Limited &nbsp;×&nbsp; {streamer_handle}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_ACCENT, spaceAfter=10))

    story.append(
        Paragraph(
            f'This Streamer Partnership Agreement ("Agreement") is executed on <b>{effective_date}</b> ("Effective Date"), by and between:',
            body_style,
        )
    )
    story.append(Spacer(1, 0.25 * cm))
    story.append(
        Paragraph(
            '<b>HyperChat by Streamheart Private Limited</b>, a company incorporated under the Companies Act, 2013, '
            'having CIN: U62099UP2025PTC235918, represented by its Director <b>Ankit Kumar</b>, with its registered office at '
            'G-478, G Block, Govindpuram Park, Block 1, Govindpuram, Ghaziabad, Uttar Pradesh – 201013, India '
            '(hereinafter referred to as the <b>"Company"</b>);',
            party_style,
        )
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("AND", ParagraphStyle("And", parent=body_style, alignment=TA_CENTER, fontName="Helvetica-Bold")))
    story.append(Spacer(1, 0.15 * cm))
    story.append(
        Paragraph(
            f'<b>{streamer_legal_name}</b>, bearing Government-issued Identity No. <b>{streamer_govt_id}</b>, '
            f'an independent digital content creator professionally known as <b>{streamer_handle}</b> '
            f'(hereinafter referred to as the <b>"Streamer"</b>).',
            party_style,
        )
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(
        Paragraph(
            'The Company and the Streamer are collectively referred to as the <b>"Parties"</b> and individually as a <b>"Party"</b>.',
            body_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY, spaceAfter=6))

    def section(num, title, items):
        story.append(Paragraph(f"{num}.&nbsp;&nbsp;{title}", heading1_style))
        for item in items:
            story.append(item)

    def clause(text):
        return Paragraph(text, body_style)

    def sub(text):
        return Paragraph(text, bullet_style)

    section("1", "PLATFORM ACCESS AND NATURE OF RELATIONSHIP", [
        clause("1.1 The Company hereby grants the Streamer access to utilize its platform \"HyperChat,\" and the Streamer agrees to use the platform subject to the terms of this Agreement."),
        clause("1.2 The relationship between the Parties is strictly that of independent contracting parties. Nothing in this Agreement shall be construed to create an employer-employee relationship, partnership, joint venture, or agency. The Streamer shall not represent themselves as having authority to bind the Company."),
    ])
    section("2", "USE OF PLATFORM AND OBLIGATIONS", [
        clause("2.1 The Streamer agrees to actively use and integrate HyperChat within their digital content ecosystem, including but not limited to live streams, recorded content, and social media platforms."),
        clause("2.2 Such integration may include verbal mentions, feature usage, and display of the HyperChat interface during live streams."),
        clause("2.3 The Streamer shall maintain reasonable consistency in usage and engagement with HyperChat, ensuring that the platform is represented in a fair, accurate, and non-misleading manner."),
        clause("2.4 The Streamer retains full creative control over their content. However, such content must comply with:"),
        sub("(a) Applicable laws in India,"),
        sub("(b) Policies of third-party platforms such as YouTube, Twitch, or similar services, and"),
        sub("(c) Platform guidelines communicated by the Company."),
        clause("2.5 The Company shall provide necessary onboarding, access to the platform, and reasonable technical support required for the Streamer to perform their obligations."),
    ])
    section("3", "REVENUE SHARE, PLATFORM FEE, AND PAYMENTS", [
        clause(fee_clause),
        clause("3.2 <b>Attribution Mechanism:</b> The Company shall maintain a transparent system to determine how revenue is attributed to the Streamer. This may include account mapping, referral tracking, or platform analytics. The logic and methodology used for such attribution shall be documented and made available to the Streamer. Any material change to attribution logic shall be communicated at least seven (7) days in advance."),
        clause("3.3 <b>Monthly Summary:</b> The Company shall provide a monthly summary including total earnings, deductions, and final payout amount through the platform dashboard or communication channels."),
        clause("3.4 <b>No Hidden Charges:</b> The Company shall not apply hidden charges. All deductions shall be clearly visible in payout reporting."),
        clause("3.5 <b>Payment Terms:</b> Payments shall be processed on a monthly basis and released within thirty (30) days from the end of each earning cycle. The Streamer is not required to raise an invoice for receiving payouts. Payments shall be made using the payment method provided by the Streamer (including UPI or bank transfer). The Company shall maintain internal records of all transactions and provide payout reports."),
        clause("3.6 <b>Payment Method:</b> Payments may be made via UPI, bank transfer, or any other method supported by the Company. The Streamer is responsible for providing accurate and up-to-date payment details."),
        clause("3.7 <b>Payment Dispute Window:</b> The Streamer must raise any dispute regarding payouts within thirty (30) days of receiving the payment report. Failure to do so shall result in the payout being deemed accepted and final."),
        clause("3.8 <b>Payment Hold:</b> The Company reserves the right to temporarily hold payouts in cases of suspected fraud, abuse, or policy violations. The Streamer shall be notified and given a reasonable opportunity to respond before any hold exceeds fifteen (15) days."),
        clause("3.9 <b>Fraud, Abuse, and Clawback:</b> If the Company reasonably suspects fraudulent activity, including but not limited to self-donations, bot usage, or artificial inflation of transactions, it shall have the right to temporarily withhold payments, conduct an investigation, and reverse or adjust payouts where fraud is established. The Company may recover such amounts from future payouts or require direct repayment."),
        clause("3.10 <b>Taxes:</b> The Company shall deduct applicable TDS in accordance with Indian law. The Streamer shall be solely responsible for their own tax filings and compliance."),
    ])
    section("4", "CONTENT RIGHTS AND INTELLECTUAL PROPERTY", [
        clause("4.1 The Streamer retains full ownership of all content created by them."),
        clause("4.2 The Streamer grants the Company a non-exclusive, limited, revocable license to use such content solely for purposes of marketing, promotion, and growth of HyperChat."),
        clause("4.3 This license shall remain valid only during the term of this Agreement. Upon termination, the Company shall immediately cease all use of the Streamer's content. Any continued or future use shall require a separate written agreement. The Company shall seek prior written consent from the Streamer before using any content for purposes beyond routine platform promotion."),
        clause("4.4 The Company shall not modify, edit, or create derivative works from the Streamer's content without prior written consent."),
        clause("4.5 The Streamer agrees not to reverse engineer, copy, replicate, or misuse the Company's technology, platform, or business model, nor misuse any trademarks or proprietary assets of the Company."),
    ])
    section("5", "PLATFORM USE AND NON-MISUSE", [
        clause("5.1 The Streamer is free to use other platforms and tools, provided they do not directly misuse or replicate HyperChat's proprietary features, technology, or business model for personal or third-party commercial gain."),
        clause("5.2 The Streamer shall not:"),
        sub("&#8226; Redirect users acquired through HyperChat to alternative payment methods with intent to bypass the platform,"),
        sub("&#8226; Encourage off-platform monetization solely to circumvent the service, or"),
        sub("&#8226; Attempt to misuse or replicate the HyperChat system for competing purposes."),
        clause("5.3 This clause shall not restrict general sponsorships, brand collaborations, or use of non-competing tools."),
    ])
    section("6", "USER-GENERATED CONTENT AND LIABILITY", [
        clause("6.1 The Company operates as an intermediary in accordance with the Information Technology Act, 2000 and the Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021."),
        clause("6.2 The Company shall provide tools and mechanisms for moderation and shall act upon valid legal takedown requests."),
        clause("6.3 The Streamer shall exercise reasonable care in moderating content and shall not knowingly allow content that is illegal, defamatory, or harmful."),
        clause("6.4 The Streamer shall be liable only in cases of gross negligence or willful misconduct. The Company shall remain responsible for failures arising from platform design, lack of reasonable safeguards, or technical malfunctions."),
    ])
    section("7", "SERVICE DISCLAIMER", [
        clause('The HyperChat platform is provided on an "as-is" and "as-available" basis. While the Company shall make reasonable efforts to ensure reliability, it does not guarantee uninterrupted or error-free operation. Temporary service interruptions shall not constitute a breach of this Agreement.'),
    ])
    section("8", "DATA PROTECTION AND PRIVACY", [
        clause("The Company shall collect, process, and store data in compliance with the Information Technology Act, 2000 and the Digital Personal Data Protection Act, 2023, and shall implement reasonable technical and organizational measures to protect user data."),
    ])
    section("9", "LIMITATION OF LIABILITY", [
        clause("Neither Party shall be liable for any indirect, incidental, or consequential damages. The total liability of the Company under this Agreement shall not exceed the total payments made to the Streamer in the preceding three (3) months."),
    ])
    section("10", "MUTUAL INDEMNITY", [
        clause("Each Party agrees to indemnify and hold harmless the other Party against any claims, damages, or liabilities arising from breach of this Agreement, violation of applicable laws, or intellectual property infringement."),
    ])
    section("11", "REPRESENTATIONS AND WARRANTIES", [
        clause("Each Party represents and warrants that it has full legal capacity to enter into this Agreement, that this Agreement does not conflict with any existing obligations, and that it shall comply with all applicable laws and regulations."),
    ])
    section("12", "TERM AND TERMINATION", [
        clause(f"12.1 This Agreement shall remain in effect for a minimum period of <b>{contract_duration_str}</b> unless terminated earlier."),
        clause("12.2 Either Party may terminate this Agreement by providing seven (7) days' written notice."),
        clause("12.3 The Parties may terminate this Agreement at any time upon mutual written consent."),
        clause("12.4 In the event of a breach, the defaulting Party shall be given fifteen (15) days to cure such breach before termination takes effect."),
        clause("12.5 Immediate termination shall be permitted in cases of fraud, criminal activity, or severe reputational harm."),
        clause("12.6 Upon termination:"),
        sub("&#8226; All outstanding payments shall be settled within fifteen (15) days,"),
        sub("&#8226; The Streamer shall cease using HyperChat features outlined in this Agreement, and"),
        sub("&#8226; Rights granted under the content license shall terminate immediately as per Clause 4.3."),
    ])
    section("13", "CONFIDENTIALITY", [
        clause("Both Parties agree to keep confidential all proprietary or sensitive information shared during the course of this Agreement. This obligation shall survive for a period of three (3) years after termination."),
    ])
    section("14", "FORCE MAJEURE", [
        clause("Neither Party shall be held liable for failure or delay in performance caused by events beyond reasonable control, including but not limited to natural disasters, government actions, internet shutdowns, or platform bans. Obligations shall be suspended for the duration of such events."),
    ])
    section("15", "DISPUTE RESOLUTION", [
        clause("15.1 The Parties shall first attempt to resolve any dispute through good faith negotiations within thirty (30) days of written notice. Notices may be sent to <b>ankit.hyperchat@gmail.com</b>."),
        clause("15.2 If unresolved, the dispute shall be referred to arbitration under the Arbitration and Conciliation Act, 1996. The seat and venue shall be Ghaziabad, Uttar Pradesh, proceedings shall be in English, and courts at Ghaziabad shall have exclusive jurisdiction."),
        clause("15.3 Nothing in this clause shall prevent either Party from seeking interim relief from a competent court."),
    ])
    section("16", "ASSIGNMENT", [
        clause("Neither Party may assign or transfer its rights or obligations under this Agreement without prior written consent of the other Party, except that the Company may assign this Agreement to its affiliates or in connection with a merger or acquisition."),
    ])
    section("17", "SURVIVAL", [
        clause("Clauses relating to intellectual property, payments, indemnity, confidentiality, and dispute resolution shall survive termination of this Agreement."),
    ])
    section("18", "NOTICES", [
        clause("All notices shall be sent via registered email addresses designated by the Parties and shall be deemed received within twenty-four (24) hours of transmission."),
    ])
    section("19", "MISCELLANEOUS", [
        clause("If any provision of this Agreement is held invalid, the remaining provisions shall continue in full force. This Agreement constitutes the entire understanding between the Parties and supersedes all prior discussions. Any amendment must be in writing and signed by both Parties."),
    ])
    section("20", "EXECUTION", [
        clause("IN WITNESS WHEREOF, the Parties have executed this Agreement as of the Effective Date."),
    ])

    story.append(Spacer(1, 0.8 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY, spaceAfter=12))

    sig_data = [
        [Paragraph("<b>For the Company</b>", body_style), Paragraph("<b>Streamer</b>", body_style)],
        [Paragraph("Name: <b>Ankit Kumar</b>", body_style), Paragraph(f"Name: <b>{streamer_legal_name}</b> ({streamer_handle})", body_style)],
        [Paragraph("Designation: <b>Director</b>", body_style), Paragraph(f"Govt. ID No.: <b>{streamer_govt_id}</b>", body_style)],
        [Paragraph("Company: <b>HyperChat by Streamheart Pvt. Ltd.</b>", body_style), Paragraph("", body_style)],
        [Spacer(1, 0.6 * cm), Spacer(1, 0.6 * cm)],
        [Paragraph("Signature: ______________________", body_style), Paragraph("Signature: ______________________", body_style)],
        [Spacer(1, 0.4 * cm), Spacer(1, 0.4 * cm)],
        [Paragraph("Date: ___________________________", body_style), Paragraph("Date: ___________________________", body_style)],
    ]

    sig_table = Table(sig_data, colWidths=[8 * cm, 8 * cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(sig_table)

    doc.build(story, onFirstPage=draw_letterhead, onLaterPages=draw_letterhead)
    return output.getvalue()
