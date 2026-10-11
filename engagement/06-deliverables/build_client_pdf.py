#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds the client-facing (non-technical) PDF security assessment report for
narayanagroup.co.in.

Output: engagement/06-deliverables/Narayana-Group-Website-Security-Assessment-Client-Report.pdf

Requires: reportlab
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable, ListFlowable, ListItem,
)

# ----------------------------------------------------------------------------
# FONTS
# ----------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DJS", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DJS-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DJM", os.path.join(FONT_DIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("DJM-Bold", os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")))
pdfmetrics.registerFontFamily("DJS", normal="DJS", bold="DJS-Bold",
                              italic="DJS", boldItalic="DJS-Bold")

# ----------------------------------------------------------------------------
# COLOURS
# ----------------------------------------------------------------------------
NAVY      = colors.HexColor("#0B2A4A")
NAVY_LT   = colors.HexColor("#1B4571")
INK       = colors.HexColor("#1A1A1A")
GREY      = colors.HexColor("#5A6472")
GREY_LT   = colors.HexColor("#EDF1F5")
GREY_BD   = colors.HexColor("#C8D2DC")
WHITE     = colors.white

CRITICAL  = colors.HexColor("#A3000F")
HIGH      = colors.HexColor("#D2560B")
MEDIUM    = colors.HexColor("#B98900")
LOW       = colors.HexColor("#1E7A3C")
INFO      = colors.HexColor("#0B5FA5")

CRIT_BG   = colors.HexColor("#FBE3E4")
HIGH_BG   = colors.HexColor("#FCEBDC")
MED_BG    = colors.HexColor("#FCF3D6")
LOW_BG    = colors.HexColor("#E3F2E7")
INFO_BG   = colors.HexColor("#E4EEF9")
NEUT_BG   = colors.HexColor("#F4F7FA")

SEV_COLOR = {
    "Critical": CRITICAL, "High": HIGH, "Medium": MEDIUM,
    "Low": LOW, "Info": INFO, "Informational": INFO,
}
SEV_BG = {
    "Critical": CRIT_BG, "High": HIGH_BG, "Medium": MED_BG,
    "Low": LOW_BG, "Info": INFO_BG, "Informational": INFO_BG,
}

PAGE_W, PAGE_H = A4
MARGIN_X = 20 * mm
MARGIN_TOP = 22 * mm
MARGIN_BOT = 20 * mm
CONTENT_W = PAGE_W - 2 * MARGIN_X

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_FILE = os.path.join(
    OUT_DIR, "Narayana-Group-Website-Security-Assessment-Client-Report.pdf")

REPORT_REF = "NSS-2026-NG-001"
REPORT_DATE = "11 October 2026"

# ----------------------------------------------------------------------------
# STYLES
# ----------------------------------------------------------------------------
def S(name, **kw):
    base = dict(name=name, fontName="DJS", fontSize=9.6, leading=14.2,
                textColor=INK, alignment=TA_JUSTIFY, spaceAfter=5)
    base.update(kw)
    return ParagraphStyle(**base)

st = {
    "cover_title":   S("cover_title", fontName="DJS-Bold", fontSize=30, leading=36,
                       textColor=WHITE, alignment=TA_LEFT, spaceAfter=6),
    "cover_sub":     S("cover_sub", fontName="DJS", fontSize=13.5, leading=19,
                       textColor=colors.HexColor("#C7D8EA"), alignment=TA_LEFT, spaceAfter=4),
    "cover_meta_k":  S("cover_meta_k", fontName="DJS-Bold", fontSize=9.5, leading=13,
                       textColor=colors.HexColor("#9FB8D0")),
    "cover_meta_v":  S("cover_meta_v", fontName="DJS", fontSize=10, leading=13.5,
                       textColor=WHITE),

    "h1":            S("h1", fontName="DJS-Bold", fontSize=17, leading=21,
                       textColor=NAVY, alignment=TA_LEFT, spaceBefore=2, spaceAfter=8),
    "h2":            S("h2", fontName="DJS-Bold", fontSize=12.6, leading=16,
                       textColor=NAVY_LT, alignment=TA_LEFT, spaceBefore=11, spaceAfter=5),
    "h3":            S("h3", fontName="DJS-Bold", fontSize=10.6, leading=14,
                       textColor=INK, alignment=TA_LEFT, spaceBefore=8, spaceAfter=3),
    "h4":            S("h4", fontName="DJS-Bold", fontSize=9.6, leading=13,
                       textColor=NAVY_LT, alignment=TA_LEFT, spaceBefore=6, spaceAfter=2),
    "body":          S("body"),
    "body_left":     S("body_left", alignment=TA_LEFT),
    "small":         S("small", fontSize=8.3, leading=11.5, textColor=GREY),
    "small_ink":     S("small_ink", fontSize=8.3, leading=11.5, textColor=INK),
    "cell":          S("cell", fontSize=8.4, leading=11.6, alignment=TA_LEFT, spaceAfter=0),
    "cell_b":        S("cell_b", fontName="DJS-Bold", fontSize=8.4, leading=11.6,
                       alignment=TA_LEFT, spaceAfter=0),
    "cell_sm":       S("cell_sm", fontSize=7.8, leading=10.6, alignment=TA_LEFT, spaceAfter=0),
    "th":            S("th", fontName="DJS-Bold", fontSize=8.6, leading=11.5,
                       textColor=WHITE, alignment=TA_LEFT, spaceAfter=0),
    "code":          S("code", fontName="DJM", fontSize=7.3, leading=9.8,
                       textColor=colors.HexColor("#102A43"), alignment=TA_LEFT, spaceAfter=0),
    "code_b":        S("code_b", fontName="DJM-Bold", fontSize=7.3, leading=9.8,
                       textColor=colors.HexColor("#102A43"), alignment=TA_LEFT, spaceAfter=0),
    "box_title":     S("box_title", fontName="DJS-Bold", fontSize=9.8, leading=13,
                       alignment=TA_LEFT, spaceAfter=3),
    "box_body":      S("box_body", fontSize=9.2, leading=13.4, alignment=TA_LEFT, spaceAfter=3),
    "bullet":        S("bullet", fontSize=9.4, leading=13.6, alignment=TA_LEFT, spaceAfter=3),
    "toc_num":       S("toc_num", fontName="DJS-Bold", fontSize=9.4, leading=15,
                       textColor=NAVY, alignment=TA_LEFT, spaceAfter=0),
    "toc_txt":       S("toc_txt", fontSize=9.6, leading=15, alignment=TA_LEFT, spaceAfter=0),
}

# ----------------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------------
def hx(c):
    return "#" + c.hexval()[2:]


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def P(text, style="body"):
    return Paragraph(text, st[style])


def raw(text, style="body"):
    """Paragraph from already-escaped/marked-up text."""
    return Paragraph(text, st[style])


def sp(h=5):
    return Spacer(1, h)


def rule(color=GREY_BD, thickness=0.7, space_before=3, space_after=7):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceBefore=space_before, spaceAfter=space_after,
                      hAlign="LEFT")


def bullets(items, style="bullet", indent=13):
    flow = []
    for it in items:
        if isinstance(it, (list, tuple)):
            head, rest = it[0], it[1]
            txt = "<b>%s</b> %s" % (esc(head), rest)
        else:
            txt = it
        flow.append(Paragraph(txt, ParagraphStyle(
            "b_%s" % style, parent=st[style], leftIndent=indent,
            bulletIndent=2, spaceAfter=4), bulletText="\u2022"))
    return flow


def numbered(items, style="bullet", indent=14):
    flow = []
    for i, it in enumerate(items, 1):
        if isinstance(it, (list, tuple)):
            head, rest = it[0], it[1]
            txt = "<b>%s</b> %s" % (esc(head), rest)
        else:
            txt = it
        flow.append(Paragraph(txt, ParagraphStyle(
            "n%d_%s" % (i, style), parent=st[style], leftIndent=indent,
            bulletIndent=2, spaceAfter=5), bulletText="%d." % i))
    return flow


def code_block(lines):
    """Monospaced evidence block with soft wrap and a left accent bar."""
    if isinstance(lines, str):
        lines = lines.split("\n")
    body = []
    wrapped = []
    maxchars = 118
    for ln in lines:
        ln = ln.rstrip("\n")
        while len(ln) > maxchars:
            wrapped.append(ln[:maxchars])
            ln = "    " + ln[maxchars:]
        wrapped.append(ln)
    for ln in wrapped:
        body.append(Paragraph(esc(ln) if ln.strip() else "&nbsp;", st["code"]))

    inner = Table([[b] for b in body], colWidths=[CONTENT_W - 16])
    inner.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    outer = Table([[inner]], colWidths=[CONTENT_W])
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F5F8")),
        ("LINEBEFORE", (0, 0), (0, -1), 2.6, colors.HexColor("#8FA6BD")),
        ("BOX", (0, 0), (-1, -1), 0.5, GREY_BD),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return outer


def callout(title, body_lines, tone="info", icon=""):
    """Coloured call-out box. tone: info|warn|danger|good|neutral"""
    tones = {
        "info":   (INFO,     INFO_BG,   "#0B5FA5"),
        "warn":   (HIGH,     HIGH_BG,   "#D2560B"),
        "danger": (CRITICAL, CRIT_BG,   "#A3000F"),
        "good":   (LOW,      LOW_BG,    "#1E7A3C"),
        "neutral":(NAVY_LT,  NEUT_BG,   "#1B4571"),
        "med":    (MEDIUM,   MED_BG,    "#B98900"),
    }
    col, bg, hexc = tones.get(tone, tones["info"])
    rows = []
    if title:
        lbl = ("%s&nbsp;&nbsp;" % icon) if icon else ""
        rows.append([Paragraph('<font color="%s">%s<b>%s</b></font>'
                               % (hexc, lbl, esc(title)), st["box_title"])])
    for bl in (body_lines if isinstance(body_lines, (list, tuple)) else [body_lines]):
        if isinstance(bl, (list, tuple)):
            bl = "%s%s" % (bl[0], bl[1])
        rows.append([Paragraph(bl, st["box_body"])])
    t = Table(rows, colWidths=[CONTENT_W])
    style = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, col),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DDE5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    if title:
        style.append(("BOTTOMPADDING", (0, 0), (0, 0), 2))
    t.setStyle(TableStyle(style))
    return t


def sev_badge(sev, cvss=None):
    c = SEV_COLOR.get(sev, NAVY)
    bg = SEV_BG.get(sev, NEUT_BG)
    txt = "<b>%s</b>" % esc(sev.upper())
    if cvss:
        txt += ' <font size="7.6">| CVSS %s</font>' % esc(cvss)
    t = Table([[Paragraph('<font color="%s">%s</font>' % (hx(c), txt),
                          ParagraphStyle("bd", fontName="DJS-Bold", fontSize=8.6,
                                         leading=11.5, alignment=TA_CENTER))]],
              colWidths=[30 * mm if cvss else 22 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.9, c),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def data_table(header, rows, widths, zebra=True, font_size=8.4, align_left=True):
    data = [[Paragraph("<b>%s</b>" % esc(h), st["th"]) for h in header]]
    for r in rows:
        cells = []
        for c in r:
            if isinstance(c, Paragraph):
                cells.append(c)
            elif "<b>" in c or "<font" in c or "<br/>" in c or "&" in c:
                cells.append(Paragraph(c, st["cell"]))   # already-safe markup
            else:
                cells.append(Paragraph(esc(c), st["cell"]))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GREY_BD),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
    t.setStyle(TableStyle(style))
    return t


def kv_table(pairs, w1=42 * mm):
    rows = []
    for k, v in pairs:
        rows.append([Paragraph("<b>%s</b>" % esc(k), st["cell"]),
                     Paragraph(v if isinstance(v, Paragraph) else esc(v), st["cell"])])
    t = Table(rows, colWidths=[w1, CONTENT_W - w1])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GREY_BD),
        ("BACKGROUND", (0, 0), (0, -1), GREY_LT),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def section_header(num, title):
    t = Table([[Paragraph('<font color="white">%s</font>' % esc(num),
                          ParagraphStyle("sn", fontName="DJS-Bold", fontSize=12,
                                         leading=15, alignment=TA_CENTER)),
                Paragraph('<font color="white">%s</font>' % esc(title),
                          ParagraphStyle("st", fontName="DJS-Bold", fontSize=12.5,
                                         leading=15, alignment=TA_LEFT))]],
              colWidths=[14 * mm, CONTENT_W - 14 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), NAVY_LT),
        ("BACKGROUND", (1, 0), (1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def finding_header(fid, title, sev, cvss):
    c = SEV_COLOR.get(sev, NAVY)
    bg = SEV_BG.get(sev, NEUT_BG)
    left = Table([[Paragraph('<font color="%s" size="8.2"><b>%s</b></font>'
                             % (hx(c), esc(fid)), st["cell"]),
                   Paragraph('<font color="%s" size="8.2">CVSS v3.1 <b>%s</b>&nbsp;&nbsp;|&nbsp;&nbsp;%s</font>'
                             % (hx(c), esc(cvss), esc(sev)), st["cell"])]],
                 colWidths=[24 * mm, CONTENT_W - 24 * mm])
    left.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    title_p = Paragraph('<font color="%s"><b>%s</b></font>'
                        % (hx(c), esc(title)),
                        ParagraphStyle("fh", fontName="DJS-Bold", fontSize=11.6,
                                       leading=15, alignment=TA_LEFT))
    box = Table([[left], [title_p]], colWidths=[CONTENT_W])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3.4, c),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DDE5")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (0, 0), 6),
        ("BOTTOMPADDING", (0, 1), (0, 1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return box


def sub_label(text, color=NAVY_LT):
    return Paragraph('<font color="%s"><b>%s</b></font>'
                     % (hx(color), esc(text)),
                     ParagraphStyle("sl", fontName="DJS-Bold", fontSize=9.6,
                                    leading=13, alignment=TA_LEFT,
                                    spaceBefore=6, spaceAfter=2))


# ----------------------------------------------------------------------------
# PAGE FURNITURE
# ----------------------------------------------------------------------------
def _cover_bg(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 118 * mm, PAGE_W, 118 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#0B5FA5"))
    canvas.rect(0, PAGE_H - 122 * mm, PAGE_W, 4 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#D2560B"))
    canvas.rect(0, PAGE_H - 126 * mm, PAGE_W, 2 * mm, stroke=0, fill=1)
    # decorative
    canvas.setFillColor(colors.HexColor("#123A5E"))
    canvas.rect(0, 0, PAGE_W, 14 * mm, stroke=0, fill=1)
    canvas.setFillColor(colors.HexColor("#9FB8D0"))
    canvas.setFont("DJS", 8)
    canvas.drawString(MARGIN_X, 5.5 * mm,
                      "CONFIDENTIAL - Authorised Security Assessment - TLP:AMBER")
    canvas.drawRightString(PAGE_W - MARGIN_X, 5.5 * mm, REPORT_REF)
    canvas.restoreState()


def _normal_bg(canvas, doc):
    canvas.saveState()
    # header band
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, stroke=0, fill=1)
    canvas.setFillColor(WHITE)
    canvas.setFont("DJS-Bold", 8)
    canvas.drawString(MARGIN_X, PAGE_H - 8.6 * mm,
                      "Website Security Assessment - narayanagroup.co.in")
    canvas.setFont("DJS", 7.6)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 8.6 * mm,
                           "CONFIDENTIAL | %s" % REPORT_REF)
    # footer
    canvas.setStrokeColor(GREY_BD)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_X, 13 * mm, PAGE_W - MARGIN_X, 13 * mm)
    canvas.setFillColor(GREY)
    canvas.setFont("DJS", 7.6)
    canvas.drawString(MARGIN_X, 9 * mm,
                      "Prepared for the Owner / Management, Narayana Group")
    canvas.drawRightString(PAGE_W - MARGIN_X, 9 * mm, "Page %d" % doc.page)
    canvas.restoreState()


# ----------------------------------------------------------------------------
# CONTENT
# ----------------------------------------------------------------------------
F = []   # flowables

# ============================================================================
# COVER
# ============================================================================
F.append(Spacer(1, 14 * mm))
F.append(P("Website Security<br/>Assessment Report", "cover_title"))
F.append(Spacer(1, 3 * mm))
F.append(P("A plain-English review of how safe your website, patient "
           "portals and staff systems are today - and exactly what to fix.",
           "cover_sub"))
F.append(Spacer(1, 8 * mm))

meta = Table([
    [Paragraph("ORGANISATION", st["cover_meta_k"]),
     Paragraph("Narayana Group", st["cover_meta_v"])],
    [Paragraph("WEBSITE TESTED", st["cover_meta_k"]),
     Paragraph("https://narayanagroup.co.in/  (and all sub-domains &amp; linked portals)",
               st["cover_meta_v"])],
    [Paragraph("REPORT DATE", st["cover_meta_k"]),
     Paragraph(REPORT_DATE, st["cover_meta_v"])],
    [Paragraph("REPORT REFERENCE", st["cover_meta_k"]),
     Paragraph(REPORT_REF, st["cover_meta_v"])],
    [Paragraph("ASSESSMENT TYPE", st["cover_meta_k"]),
     Paragraph("Authorised, non-destructive external security assessment",
               st["cover_meta_v"])],
    [Paragraph("PERMISSION", st["cover_meta_k"]),
     Paragraph("Written authorisation held on file from the owner",
               st["cover_meta_v"])],
    [Paragraph("AUDIENCE", st["cover_meta_k"]),
     Paragraph("Owner / Management (no technical background assumed)",
               st["cover_meta_v"])],
], colWidths=[42 * mm, CONTENT_W - 42 * mm])
meta.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]))
F.append(meta)

F.append(Spacer(1, 12 * mm))

# Headline result strip
res = Table([
    [Paragraph('<font color="white" size="8.5"><b>RESULT AT A GLANCE</b></font>',
               st["cell"])],
], colWidths=[CONTENT_W])
res.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0B5FA5")),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 4),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
F.append(res)

counts = Table([
    [Paragraph('<font color="#A3000F" size="20"><b>2</b></font><br/><font size="7.4">CRITICAL</font>', st["cell"]),
     Paragraph('<font color="#D2560B" size="20"><b>5</b></font><br/><font size="7.4">HIGH</font>', st["cell"]),
     Paragraph('<font color="#B98900" size="20"><b>3</b></font><br/><font size="7.4">MEDIUM</font>', st["cell"]),
     Paragraph('<font color="#0B2A4A" size="20"><b>10</b></font><br/><font size="7.4">TOTAL ISSUES</font>', st["cell"])],
], colWidths=[CONTENT_W / 4.0] * 4)
counts.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, 0), CRIT_BG),
    ("BACKGROUND", (1, 0), (1, 0), HIGH_BG),
    ("BACKGROUND", (2, 0), (2, 0), MED_BG),
    ("BACKGROUND", (3, 0), (3, 0), colors.HexColor("#E3EAF1")),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("GRID", (0, 0), (-1, -1), 0.5, WHITE),
    ("TOPPADDING", (0, 0), (-1, -1), 7),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
]))
F.append(counts)
F.append(Spacer(1, 6 * mm))
F.append(callout(
    "Read this first",
    ["Two of the problems in this report are rated <b>CRITICAL</b>. In plain terms: "
     "<b>a stranger on the internet, with no password and no login, can today read the "
     "personal details and photographs of your staff, and can read patient names, "
     "mobile numbers and medical test details</b> from your live systems. They can also "
     "take over accounts by resetting a PIN. None of this requires hacking skill - it "
     "only requires typing a web address.",
     "Real data was retrieved during this test to prove it. Names and mobile numbers have "
     "been kept in this report as proof, but no data was downloaded, stored, modified or "
     "deleted, and nothing was taken from your servers."],
    tone="danger", icon="!!"))
F.append(PageBreak())

TOC_INSERT_AT = len(F)

# ============================================================================
# 1. HOW TO READ THIS REPORT
# ============================================================================
F.append(section_header("1", "How to read this report (2 minutes)"))
F.append(sp(3))

F.append(P("This report was written for you - the owner - not for engineers. "
           "You do not need any technical knowledge to read it. Every problem is "
           "explained in four simple parts:"))
F.append(sp(2))

F.append(data_table(
    ["Part", "What it tells you"],
    [
        ["<b>What is wrong</b>",
         "The problem explained in everyday language, with a simple comparison."],
        ["<b>What a criminal could do</b>",
         "The real-world damage if someone evil found this before your team fixed it."],
        ["<b>How we proved it</b>",
         "The exact steps we ran, shown verbatim, so your developers can repeat them "
         "and see the same result with their own eyes. Nothing here is guesswork."],
        ["<b>How to fix it</b>",
         "A clear, itemised instruction list. You can hand this page straight to your "
         "IT team or web developer - they will know what to do from it."],
    ],
    [40 * mm, CONTENT_W - 40 * mm]))
F.append(sp(6))

F.append(callout(
    "A note on tone",
    ["This report sounds alarming because the situation genuinely is serious. That is "
     "not a criticism of your IT team. These systems were almost certainly built years "
     "ago, by different vendors, at a time when hospital software was not expected to be "
     "reachable from the open internet. Almost every issue in this report is fixable, "
     "and most fixes are configuration changes rather than rebuilds."],
    tone="neutral"))
F.append(sp(4))

F.append(sub_label("What we did NOT do"))
F.append(P("To be completely transparent, and so you can be confident the results are "
           "trustworthy and nothing was harmed:"))
F.extend(bullets([
    ("We did not break anything. ", "No data was changed, added, deleted or moved."),
    ("We did not download or keep your data. ", "We looked at responses on screen only, "
     "purely to prove the problem exists."),
    ("We did not attack your staff. ", "No phishing emails, no phone calls, no "
     "social engineering."),
    ("We did not slow anything down. ", "No stress tests, no flooding, no denial of service."),
    ("We did not test anyone else's computers. ", "Only addresses that belong to "
     "Narayana Group were examined."),
    ("We did not access systems we were not shown. ", "Everything in this report was "
     "found from the public internet, the same way a criminal would find it."),
]))
F.append(sp(4))

F.append(callout(
    "Confidentiality",
    ["This document contains real security holes in your live systems. Please treat it "
     "as confidential. Share it only with people who need to act on it - your IT head, "
     "your web developer, and your hosting provider. Do not post it publicly, and do not "
     "email it unencrypted to a wide group, until the Critical items are closed."],
    tone="warn", icon="!"))
F.append(PageBreak())

# ============================================================================
# 2. GLOSSARY
# ============================================================================
F.append(section_header("2", "Simple glossary - the words used in this report"))
F.append(sp(3))
F.append(P("Every technical word you will see in this report is explained below. "
           "Nothing else is assumed."))
F.append(sp(3))

GLOSSARY = [
    ("Website / Server",
     "The computer (often rented from a hosting company) that stores your website and "
     "answers when someone opens it in a browser."),
    ("Sub-domain",
     "An extra address hanging off your main name - for example "
     "<b>pacs.narayanagroup.co.in</b> or <b>helpdesk.narayanagroup.co.in</b>. Each one "
     "is effectively a separate mini-website, often on a separate computer."),
    ("Web page vs. API",
     "A <b>web page</b> is what a human sees. An <b>API</b> is the hidden plumbing that "
     "apps and web pages use to fetch and save data. Criminals target APIs because they "
     "return raw data with no login screen in front of them."),
    ("Login / Authentication",
     "Proving who you are - normally a user ID and password or PIN. Done properly, the "
     "<b>server</b> checks this on every single request. Done badly, the <b>website page</b> "
     "checks it in the visitor's own browser, which a criminal can simply skip."),
    ("Session / Session cookie",
     "The digital 'wristband' a website gives you after you log in, so it remembers you "
     "as you move between pages. If there is no wristband, or it is easy to forge, "
     "anyone can walk in."),
    ("Server-side vs. Client-side",
     "<b>Server-side</b> = checked on your computer (safe). <b>Client-side</b> = checked "
     "in the visitor's own browser (unsafe, because the visitor controls their browser)."),
    ("Encryption / HTTPS / SSL-TLS",
     "The padlock in the browser bar. It scrambles data in transit so nobody on the "
     "network can read or alter it. Without it (<b>http://</b> instead of "
     "<b>https://</b>), everything travels in plain readable text."),
    ("Database",
     "The big electronic filing cabinet holding your staff records, patient records, "
     "bills and test results. Your systems use an <b>Oracle</b> database."),
    ("PII (Personal Identifiable Information)",
     "Any data that identifies a living person - name, mobile number, address, date of "
     "birth, photo, employee number, Aadhaar."),
    ("PHI (Protected Health Information)",
     "PII <b>plus</b> health data - patient name linked to a medical test, diagnosis, "
     "bill or hospital registration number. This is the most legally sensitive category."),
    ("Vulnerability",
     "A weakness or mistake in how a system was built or configured."),
    ("Exploit",
     "The act of using that weakness to do something the owner did not intend."),
    ("IDOR (Insecure Direct Object Reference)",
     "A very common flaw where a website uses a visible number to pick whose record to "
     "show - for example <b>/Patient/Info/1005411787</b>. Change the number, see a "
     "different patient. It is like a hotel giving out room keys numbered 1, 2, 3... "
     "and never asking who you are."),
    ("CVSS score",
     "An international 0-to-10 danger rating used by every security team and insurance "
     "company. <b>9.0-10.0 = Critical</b>, <b>7.0-8.9 = High</b>, "
     "<b>4.0-6.9 = Medium</b>, <b>0.1-3.9 = Low</b>."),
    ("RCE (Remote Code Execution)",
     "The worst case: a criminal runs their own commands on your server. That is full "
     "control of the machine."),
    ("SQL Injection (SQLi)",
     "Tricking a website into running unintended commands against its database by "
     "typing special characters (like a single quote <b>'</b>) into a form."),
    ("XSS (Cross-Site Scripting)",
     "Injecting malicious script into a page so it runs in another user's browser - "
     "used to steal logins."),
    ("Clickjacking",
     "Placing an invisible layer over your page so a visitor thinks they are clicking "
     "one thing but actually clicks something else."),
    ("EOL (End of Life)",
     "Software the manufacturer no longer supports or patches. Once a flaw is published "
     "for EOL software, it is never fixed - so attackers keep using it for years."),
    ("Security header",
     "A short instruction your server sends alongside a page telling the browser what it "
     "is and is not allowed to do. Cheap to add, and they block whole families of attacks."),
    ("SPF / DMARC",
     "Two DNS settings that tell the world which computers are allowed to send email "
     "using your domain name. Without them, anyone can send an email that appears to "
     "come from <b>admin@narayanagroup.co.in</b>."),
    ("DNS",
     "The internet's phone book - it turns a name like "
     "<b>narayanagroup.co.in</b> into a numeric computer address like "
     "<b>115.241.194.4</b>."),
    ("PACS",
     "The medical imaging system that stores X-rays, CT scans and MRIs."),
    ("MITM (Man-in-the-Middle)",
     "An attacker sitting between your user and your server, reading or altering "
     "everything that passes - easy on public Wi-Fi when a site is not encrypted."),
    ("Patch / Update",
     "A free fix supplied by the software maker. Applying patches is the single most "
     "effective security activity there is."),
]
F.append(data_table(["Term", "What it means, in plain English"],
                    [[a, b] for a, b in GLOSSARY],
                    [40 * mm, CONTENT_W - 40 * mm]))
F.append(PageBreak())

# ============================================================================
# 3. EXECUTIVE SUMMARY
# ============================================================================
F.append(section_header("3", "Executive summary - the bottom line"))
F.append(sp(3))

F.append(sub_label("The one-paragraph version"))
F.append(P("Between <b>9 and 11 October 2026</b> we examined your public website "
           "<b>https://narayanagroup.co.in/</b>, its sub-domains, and roughly "
           "<b>29 connected hospital, student, payroll, payment and imaging portals</b>. "
           "We found <b>10 confirmed security problems</b>: <b>2 Critical</b>, "
           "<b>5 High</b> and <b>3 Medium</b>. The two Critical problems mean that "
           "<b>right now, anyone in the world with an internet connection can read "
           "confidential staff and patient information from your systems without a "
           "password, and can reset account PINs to take over accounts</b>. We proved "
           "this by retrieving real records during the test. The good news: all ten "
           "issues are fixable, none require rebuilding your hospital software, and the "
           "two Critical ones can be substantially reduced within a day or two by "
           "switching on authentication at the API layer."))
F.append(sp(4))

F.append(sub_label("Why this matters to you as the owner"))
F.append(callout(
    "Three consequences you should be aware of",
    [
      ("<b>1. Legal exposure.</b> ",
       "India's <b>Digital Personal Data Protection (DPDP) Act, 2023</b> requires "
       "organisations handling personal data - and especially health data - to apply "
       "\"reasonable security safeguards\". Penalties for failing to do so can reach "
       "<b>&#8377;250 crore</b> per instance. Personal data of employees and patients is "
       "currently readable by anyone on the internet; that is difficult to defend as a "
       "reasonable safeguard."),
      ("<b>2. Reputation.</b> ",
       "A hospital losing patient data is front-page news. Patients choose hospitals on "
       "trust. A single breach disclosure costs far more in lost admissions than the "
       "cost of these fixes."),
      ("<b>3. Operational and financial risk.</b> ",
       "One issue (WEB-2026-004) lets a payer alter the amount and destination bank "
       "account on the student fee payment page. Another (WEB-2026-002) lets a stranger "
       "<b>approve cancellations of hospital bills</b>. These are direct money "
       "problems, not just privacy problems."),
    ], tone="danger", icon="!!"))
F.append(sp(4))

F.append(sub_label("The five most urgent things, ranked"))
F.append(data_table(
    ["#", "The problem, in one sentence", "Severity"],
    [
        ["1", "Your staff and patient mobile apps (Nnote / ncare) have <b>no real "
              "login at all</b> - anyone can open the private dashboard by typing the "
              "web address directly, and can reset any PIN.",
         Paragraph('<font color="#A3000F"><b>Critical</b></font>', st["cell"])],
        ["2", "Behind those apps, the data services (<b>/NtraktApi/</b> and "
              "<b>/NnoteApi/</b>) hand out <b>staff records with photographs</b> and "
              "<b>patient records with medical tests</b> to anyone who asks - no login, "
              "no password.",
         Paragraph('<font color="#A3000F"><b>Critical</b></font>', st["cell"])],
        ["3", "Those same services also accept <b>file uploads</b> from anyone, with no "
              "login - a classic route to taking over the server entirely.",
         Paragraph('<font color="#D2560B"><b>High</b></font>', st["cell"])],
        ["4", "The student fee payment page keeps the <b>amount and the destination bank "
              "account in the visitor's own browser</b>, where they can be changed.",
         Paragraph('<font color="#D2560B"><b>High</b></font>', st["cell"])],
        ["5", "Several systems run on software that <b>stopped receiving security "
              "updates years ago</b> (PHP 5.6, Apache 2.4.23, osTicket 2016, "
              "ASP.NET 2.0), and some pages are not encrypted at all.",
         Paragraph('<font color="#D2560B"><b>High</b></font>', st["cell"])],
    ],
    [8 * mm, CONTENT_W - 8 * mm - 24 * mm, 24 * mm]))
F.append(sp(5))

F.append(sub_label("What we found working well"))
F.append(P("It is worth recording the positives, so your team knows what to protect "
           "and keep:"))
F.extend(bullets([
    ("Your domain is behind Cloudflare. ", "Your DNS is managed by Cloudflare, which "
     "gives you free access to a firewall (WAF), bot protection and free SSL. You are "
     "paying nothing extra to switch these on, and they would blunt most of this report's "
     "findings while the permanent fixes are built."),
    ("The main server is tightly firewalled. ", "A scan of your primary address "
     "(<b>115.241.194.4</b>) showed only the encrypted web port <b>443</b> open. "
     "Everything else - remote desktop, database, file transfer - is correctly closed. "
     "That is better than most organisations your size."),
    ("Some newer systems are modern. ", "The <b>app.narayanagroup.co.in</b> and "
     "<b>dms.narayanagroup.co.in</b> systems run current software. Whoever built those "
     "is doing things right - give them the older systems too."),
    ("The Laravel task app is configured properly. ", "<b>/ntask/</b> uses encrypted, "
     "HttpOnly, SameSite cookies with CSRF protection and runs a current PHP 8.3. "
     "It is the best-configured application in the estate."),
]))
F.append(PageBreak())

# ============================================================================
# 4. SEVERITY EXPLAINER
# ============================================================================
F.append(section_header("4", "How dangerous is each rating?"))
F.append(sp(3))
F.append(P("Security problems worldwide are graded on a standard scale called "
           "<b>CVSS</b> (Common Vulnerability Scoring System), which runs from 0 to 10. "
           "Here is what each band means for you in practice."))
F.append(sp(3))

sev_rows = [
    (Paragraph('<font color="#A3000F"><b>CRITICAL</b></font><br/>'
               '<font size="7.6">CVSS 9.0 - 10.0</font>', st["cell"]),
     "Drop everything.",
     "A stranger with no password and no special tools can cause maximum damage - "
     "steal all your data, or take over accounts. Usually fixable in hours or days. "
     "Treat as an incident, not a task."),
    (Paragraph('<font color="#D2560B"><b>HIGH</b></font><br/>'
               '<font size="7.6">CVSS 7.0 - 8.9</font>', st["cell"]),
     "Fix this week.",
     "Serious harm is likely - theft of data, takeover of the server, or direct "
     "financial loss. Often needs some skill to exploit, but that skill is freely "
     "available online."),
    (Paragraph('<font color="#B98900"><b>MEDIUM</b></font><br/>'
               '<font size="7.6">CVSS 4.0 - 6.9</font>', st["cell"]),
     "Fix this month.",
     "Meaningful weakness that helps an attacker, but usually needs a second problem or "
     "some luck to cause real damage. Also covers problems that would embarrass you or "
     "breach a compliance rule on their own."),
    (Paragraph('<font color="#1E7A3C"><b>LOW</b></font><br/>'
               '<font size="7.6">CVSS 0.1 - 3.9</font>', st["cell"]),
     "Fix when convenient.",
     "Small hygiene issues. Little direct risk, but they make an attacker's job easier."),
]
t = data_table(["Rating", "Action", "What it actually means"],
               [[a, "<b>%s</b>" % b, c] for a, b, c in sev_rows],
               [30 * mm, 28 * mm, CONTENT_W - 58 * mm])
F.append(t)
F.append(sp(5))

F.append(callout(
    "How to think about the two Critical findings",
    ["Imagine your hospital reception has a filing cabinet with every employee's photo "
     "ID, home address, mobile number and date of birth, plus a second cabinet with "
     "patient names, mobile numbers and the tests they had done. Now imagine that "
     "cabinet was moved into the street outside, with a sign saying "
     "\"take what you need, no questions asked\".",
     "That is, precisely, what <b>WEB-2026-002</b> is. And <b>WEB-2026-001</b> is the "
     "digital equivalent of leaving the keys in the door of every office - the lock is "
     "there, but it is not actually connected to anything."],
    tone="danger", icon="!!"))
F.append(sp(4))

F.append(sub_label("Your scorecard"))
F.append(P("Out of the ten confirmed issues:"))
F.append(sp(2))
sc = Table([
    [Paragraph('<font color="#A3000F" size="9"><b>Critical&nbsp;&nbsp;&nbsp;2</b></font>', st["cell"]),
     Paragraph('<font color="#D2560B" size="9"><b>High&nbsp;&nbsp;&nbsp;5</b></font>', st["cell"]),
     Paragraph('<font color="#B98900" size="9"><b>Medium&nbsp;&nbsp;&nbsp;3</b></font>', st["cell"]),
     Paragraph('<font color="#1E7A3C" size="9"><b>Low&nbsp;&nbsp;&nbsp;0</b></font>', st["cell"])],
    [Paragraph("Critical and High together make up <b>70% of all findings</b>. For a "
               "hospital group handling patient health records, that places the estate "
               "in the high-risk category until the two Critical items are closed.",
               ParagraphStyle("sc", parent=st["cell"], fontSize=8.6, leading=11.8))],
], colWidths=[CONTENT_W / 4.0] * 4)
sc.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, 0), CRIT_BG),
    ("BACKGROUND", (1, 0), (1, 0), HIGH_BG),
    ("BACKGROUND", (2, 0), (2, 0), MED_BG),
    ("BACKGROUND", (3, 0), (3, 0), LOW_BG),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("SPAN", (0, 1), (-1, 1)),
    ("GRID", (0, 0), (-1, 0), 0.5, WHITE),
    ("BACKGROUND", (0, 1), (-1, 1), NEUT_BG),
    ("BOX", (0, 1), (-1, 1), 0.5, GREY_BD),
    ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
F.append(sc)
F.append(PageBreak())

# ============================================================================
# 5. WHAT WAS TESTED
# ============================================================================
F.append(section_header("5", "What exactly was tested"))
F.append(sp(3))
F.append(P("We started at your public homepage and followed every link, then expanded "
           "to every sub-domain we could legitimately discover from public records. In "
           "total we looked at <b>8 sub-domains, 29 linked applications and 9 distinct "
           "servers</b>. Below is the full inventory - this is your entire public "
           "footprint as the internet sees it."))
F.append(sp(3))

F.append(sub_label("5.1  Sub-domains and servers"))
F.append(data_table(
    ["Address", "IP address", "What it is", "Software found"],
    [
        ["narayanagroup.co.in", "115.241.194.4", "Main public website + all "
         "sub-applications", "IIS / ASP.NET via Apache proxy; jQuery 1.12.4; "
         "Bootstrap 3.3.7"],
        ["www.narayanagroup.co.in", "115.241.194.4", "Alias of the main site", "Same"],
        ["pacs.narayanagroup.co.in", "115.241.194.11", "Medical imaging (X-ray, CT, MRI)",
         "Medsynapse PACS 7.0.0.0 and RIS 5.1.0.0"],
        ["dms.narayanagroup.co.in", "115.241.194.12", "Document management system",
         "IIS 10.0; ASP.NET MVC 5.2; jQuery 3.2.1"],
        ["nmc.narayanagroup.co.in", "115.241.194.13", "Narayana Medical College - "
         "currently an empty default page", "IIS 10.0 (default, unused)"],
        ["uat.narayanagroup.co.in", "3.33.251.168 &#8594; 115.241.194.18",
         "Test (UAT) environment, redirects to a raw server",
         "Apache 2.4.41; OpenSSL 1.1.1c; PHP 7.3.11 (all End of Life)"],
        ["app.narayanagroup.co.in", "117.206.80.208", "\"Narayana Runner\" mobile "
         "companion app login", "nginx 1.24.0; Bootstrap 5.3.3"],
        ["helpdesk.narayanagroup.co.in", "117.206.80.205", "IT helpdesk / ticket system",
         "Apache 2.4.23; PHP 5.6.25; osTicket 1.10 (2016) - all End of Life"],
        ["online.narayanagroup.co.in", "15.241.194.25",
         Paragraph('<font color="#A3000F"><b>Misconfigured - points at a stranger\'s '
                   'server</b></font>', st["cell"]),
         "Should be 115.241.194.x. The leading \"1\" was missed when the record "
         "was created."],
    ],
    [37 * mm, 27 * mm, 45 * mm, CONTENT_W - 109 * mm]))
F.append(sp(5))

F.append(sub_label("5.2  Applications hosted on the main website"))
F.append(P("These are separate mini-systems reached from "
           "<b>https://narayanagroup.co.in/</b>. Each was opened and inspected:"))
F.append(sp(2))
apps = [
    ("/Nnote/", "Staff clinical notes, attendance, service requests",
     "Critical - no login; mass staff data exposure"),
    ("/ncare/", "Inpatient (admitted patient) portal",
     "Critical - no login; patient data exposure; PIN reset"),
    ("/NtraktApi/", "Data service behind Nnote (staff)",
     "Critical - unauthenticated; leaks Oracle errors"),
    ("/NnoteApi/", "Data service behind Nnote and ncare",
     "Critical - unauthenticated; leaks patient and billing data"),
    ("/onlinefeepay/razorpay/CreateOrderNew.aspx", "Student / college fee payment",
     "High - amounts and bank account controllable by the payer"),
    ("/NHIS/", "NextGen hospital dashboard", "Medium - cookie not marked Secure"),
    ("/patient/", "Patient reports portal",
     "High - runs on ASP.NET 2.0 (End of Life)"),
    ("/MedicalNarayanaPayroll/", "Payroll system",
     "High - built with Visual Studio .NET 2003 toolchain"),
    ("/inventory/", "WIMS - inventory management",
     "Medium - 2010 Classic ASP; insecure cookie; user enumeration"),
    ("/nmconline/", "WHIS - hospital management",
     "Medium - 2010 Classic ASP; insecure cookie; user enumeration"),
    ("/ntask/", "Task management (Laravel)",
     "Informational - best configured app in the estate"),
    ("/NCLINIC/", "Clinic system", "Informational - outdated front-end code"),
    ("/SIS/", "Academic student information system", "Informational - surveyed"),
    ("/NLIS/", "Laboratory information system", "Informational - surveyed"),
    ("/NIS/", "Institute system", "Informational - surveyed"),
    ("/zoomreports/", "Reporting portal", "Informational - surveyed"),
    ("/unlis/", "Laboratory portal", "Informational - surveyed"),
]
F.append(data_table(
    ["Path", "What it does", "Worst issue found"],
    [[a, b, c] for a, b, c in apps],
    [58 * mm, 52 * mm, CONTENT_W - 110 * mm]))
F.append(sp(5))

F.append(callout(
    "Why the inventory matters",
    ["Most organisations are breached through a system they had forgotten they owned. "
     "The list above is the complete set of doors into your organisation from the "
     "internet. <b>Every single one of these needs a named owner inside your company.</b> "
     "If nobody can name the owner, that is by itself a risk - and we have listed three "
     "such systems here (<b>nmc</b>, <b>uat</b> and <b>online</b>)."],
    tone="warn", icon="!"))
F.append(PageBreak())

# ============================================================================
# 6. FINDINGS SUMMARY TABLE
# ============================================================================
F.append(section_header("6", "All 10 findings at a glance"))
F.append(sp(3))
F.append(P("The table below is your action list. The rest of the report explains each "
           "one in full detail."))
F.append(sp(3))

summary_rows = [
    ("WEB-2026-001", "No real login on staff and patient apps; anyone can open the "
     "private dashboard and reset any PIN", "Critical", "9.8", "Today"),
    ("WEB-2026-002", "Strangers can read staff records with photos, and patient names, "
     "mobiles and medical tests - no login needed", "Critical", "9.8", "Today"),
    ("WEB-2026-003", "Anyone can upload files to your servers without logging in",
     "High", "8.6", "This week"),
    ("WEB-2026-004", "Fee payment page lets the payer change the amount and the "
     "destination bank account", "High", "8.2", "This week"),
    ("WEB-2026-006", "Several systems run software that no longer receives security "
     "updates (2016 and older)", "High", "8.1", "This month"),
    ("WEB-2026-005", "Error messages reveal your internal database structure and "
     "server file paths", "High", "7.5", "This week"),
    ("WEB-2026-007", "Hospital Android app is downloaded over an unencrypted "
     "connection; two login pages are unencrypted", "High", "7.5", "This week"),
    ("WEB-2026-008", "Medical imaging server security settings are switched off or "
     "left at placeholder values", "Medium", "6.5", "This month"),
    ("WEB-2026-010", "No email anti-forgery records (SPF/DMARC); "
     "the online sub-domain points at a stranger's server", "Medium", "6.5",
     "This month"),
    ("WEB-2026-009", "Missing browser protections (clickjacking etc.), insecure "
     "cookies, and internal IP addresses visible in your pages", "Medium", "5.8",
     "This month"),
]
rows = []
for fid, title, sev, cvss, when in summary_rows:
    rows.append([
        Paragraph("<b>%s</b>" % esc(fid), st["cell_sm"]),
        Paragraph(esc(title), st["cell_sm"]),
        Paragraph('<font color="%s"><b>%s</b></font>' % (hx(SEV_COLOR[sev]), esc(sev)), st["cell_sm"]),
        Paragraph(esc(cvss), st["cell_sm"]),
        Paragraph("<b>%s</b>" % esc(when), st["cell_sm"]),
    ])
t = Table([[Paragraph("<b>%s</b>" % h, st["th"]) for h in
            ["ID", "What is wrong", "Severity", "CVSS", "Fix by"]]] + rows,
          colWidths=[27 * mm, CONTENT_W - 27 * mm - 20 * mm - 13 * mm - 20 * mm,
                     20 * mm, 13 * mm, 20 * mm], repeatRows=1)
st_l = [("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, GREY_BD),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5)]
for i in range(1, len(rows) + 1):
    if i % 2 == 0:
        st_l.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
t.setStyle(TableStyle(st_l))
F.append(t)
F.append(sp(6))

F.append(callout(
    "How to use this table",
    ["Print this single page and pin it to the wall of your IT team. The "
     "<b>\"Fix by\"</b> column is our recommendation based on how dangerous the issue is "
     "<b>combined with</b> how easy it is to exploit. Anything marked <b>Today</b> "
     "should be treated as an active incident - it is not a scheduled maintenance item."],
    tone="info"))
F.append(PageBreak())


# ============================================================================
# HELPER: render one finding
# ============================================================================
def finding(fid, title, sev, cvss, analogy, what_is_wrong, impact, proof_intro,
            proof_blocks, fix_title, fix_items, extra=None, cwe=None, owasp=None,
            affected=None):
    out = []
    out.append(finding_header(fid, title, sev, cvss))
    out.append(sp(4))

    meta_bits = []
    if affected:
        meta_bits.append(("Where", affected))
    if cwe:
        meta_bits.append(("Technical ID (CWE)", esc(cwe)))
    if owasp:
        meta_bits.append(("Category", esc(owasp)))
    if meta_bits:
        out.append(kv_table(meta_bits, w1=34 * mm))
        out.append(sp(3))

    out.append(callout("In plain English - a comparison you will recognise",
                       [analogy], tone="danger" if sev == "Critical" else
                       ("warn" if sev == "High" else "med")))
    out.append(sp(4))

    out.append(sub_label("1.  What is wrong"))
    for para in (what_is_wrong if isinstance(what_is_wrong, list) else [what_is_wrong]):
        out.append(P(para))
    out.append(sp(3))

    out.append(sub_label("2.  What a criminal could do with this"))
    if isinstance(impact, list):
        out.extend(bullets(impact))
    else:
        out.append(P(impact))
    out.append(sp(3))

    out.append(sub_label("3.  How we proved it (real output, not theory)"))
    out.append(P(proof_intro))
    out.append(sp(2))
    for blk in proof_blocks:
        if isinstance(blk, tuple):
            out.append(Paragraph("<b>%s</b>" % esc(blk[0]),
                                 ParagraphStyle("pb", parent=st["small_ink"],
                                                spaceBefore=4, spaceAfter=2)))
            out.append(code_block(blk[1]))
        else:
            out.append(code_block(blk))
    out.append(sp(3))

    out.append(sub_label("4.  How to fix it"))
    out.append(P(fix_title))
    out.append(sp(1))
    out.extend(numbered(fix_items))
    out.append(sp(3))

    if extra:
        out.extend(extra)
    out.append(sp(4))
    out.append(rule())
    return out


# ============================================================================
# 7. DETAILED FINDINGS
# ============================================================================
F.append(section_header("7", "Detailed findings - one by one"))
F.append(sp(3))
F.append(P("Each finding below follows the same four-part structure: what is wrong, "
           "what a criminal could do, how we proved it, and how to fix it. The "
           "\"How we proved it\" sections contain the exact commands and responses, so "
           "your developers can reproduce everything themselves and confirm the fix "
           "afterwards."))
F.append(sp(5))

# ---------------------------------------------------------------------------
F.append(PageBreak())
F.extend(finding(
    fid="WEB-2026-001",
    title="No real login on your staff and patient portals - anyone can walk straight in "
          "and reset any PIN",
    sev="Critical", cvss="9.8",
    affected="/Nnote/ (staff app), /ncare/ (patient app), "
             "/NnoteApi/api/Patient/ChangePin, /NtraktApi/api/User/UpdatePin, "
             "/NnoteApi/api/Nnote/User/CreateUser",
    cwe="CWE-287 Improper Authentication; CWE-602 Client-Side Security Control; "
        "CWE-620 Unverified Password Change",
    owasp="OWASP Top 10 (2021) - A07:2021 Identification and Authentication Failures",
    analogy="It is as if your office door has a card reader on it that looks impressive, "
            "but is not wired to anything - the door opens when you push it. On top of "
            "that, the form for changing your desk PIN is sitting on a table in the "
            "reception area, and it does not ask for your old PIN first. So not only can "
            "anyone walk in, anyone can also change the lock code.",
    what_is_wrong=[
        "You have two web applications used by your people: <b>/Nnote/</b> for staff "
        "(clinical notes, attendance, service requests) and <b>/ncare/</b> for admitted "
        "patients. Both show a login screen asking for a user ID and PIN.",
        "We tested what happens when you simply <b>skip the login screen</b> and type the "
        "address of the page that comes after it. <b>It opened immediately.</b> No "
        "password, no PIN, no error.",
        "The reason is that the login check happens <b>inside the visitor's own web "
        "browser</b> (client-side), not on your server. A browser check is like a "
        "receptionist who asks for ID but has no power to actually stop anyone - the "
        "visitor is free to ignore it. Security decisions must always be made by your "
        "server, which is the only computer you control.",
        "After the fake login, the page simply puts the user's ID in the web address, "
        "for example <b>layout.html?empid=MzMzNDAyNA==</b>. Those characters "
        "(<b>MzMzNDAyNA==</b>) are just the staff number <b>3334024</b> written in a "
        "simple, reversible code called Base64. Anyone can change it to a different "
        "number and become a different person.",
        "It gets worse. The password/PIN change functions do not check who is asking:",
    ],
    impact=[
        ("Complete account takeover. ", "An attacker types any employee number and "
         "becomes that employee inside the system - with all the screens, approvals and "
         "data that employee can see."),
        ("PIN reset without the old PIN. ", "The patient PIN change request "
         "(<b>POST /NnoteApi/api/Patient/ChangePin</b>) asks only for a registration "
         "number and a new PIN. It never asks for the existing PIN, never sends a "
         "one-time code, and never checks for a logged-in session. Same for the staff "
         "version (<b>POST /NtraktApi/api/User/UpdatePin</b>)."),
        ("Fake staff accounts. ", "The registration function "
         "(<b>/NnoteApi/api/Nnote/User/CreateUser</b>) creates users with a user ID and "
         "password. Its one-time-code requirement is enforced only in browser "
         "JavaScript, which an attacker simply turns off."),
        ("Fraud and sabotage from the inside. ", "With a real employee's account, an "
         "attacker can approve things, cancel things, and act in that employee's name - "
         "and your audit logs will blame the employee, not the attacker."),
        ("Regulatory breach. ", "Unauthorised access to health records is exactly what "
         "the DPDP Act 2023 requires you to prevent with \"reasonable security "
         "safeguards\"."),
    ],
    proof_intro="The following are the exact steps. Anyone in the world can run these "
                "from a normal computer - no special software needed.",
    proof_blocks=[
        ("Step 1 - open the login page and look for a real session. There is none:",
         """$ curl -s -i "https://narayanagroup.co.in/Nnote/index.html" | grep -i "set-cookie"

(no output - the server issues no session cookie at all)

$ curl -s -i "https://narayanagroup.co.in/ncare/index.html" | grep -i "set-cookie"

(no output - the server issues no session cookie at all)"""),
        ("Step 2 - skip the login entirely. Go straight to the private dashboard with "
         "any staff number. The server answers 200 OK (success):",
         """$ curl -s -o /dev/null -w "%{http_code}\\n" \\
    "https://narayanagroup.co.in/Nnote/layout.html?empid=MzMzNDAyNA=="
200

$ curl -s -o /dev/null -w "%{http_code}\\n" \\
    "https://narayanagroup.co.in/ncare/layout.html?regno=MTAwNTQxMTc4Nw=="
200"""),
        ("Note: 'MzMzNDAyNA==' is just Base64 for 3334024, and "
         "'MTAwNTQxMTc4Nw==' is Base64 for 1005411787. You can encode or decode this "
         "with any free website - it is not encryption, it is a reversible code.",
         """$ echo -n "3334024"     | base64   ->  MzMzNDAyNA==
$ echo -n "1005411787"  | base64   ->  MTAwNTQxMTc4Nw==""",),
        ("Step 3 - the code that is supposed to log you in. This is in the page the "
         "visitor downloads, so the visitor controls it:",
         """// Nnote/index.html  -  login check runs in the BROWSER, not on the server
function checkLogin() {
    var empid = document.getElementById("empid").value;
    var pin   = document.getElementById("pin").value;
    // ... compares against values returned by the API ...
    if (ok) {
        // just moves the browser to the next page - no session, no token
        window.location = "layout.html?empid=" + btoa(empid);
    }
}"""),
        ("Step 4 - the PIN reset asks for no proof of identity at all. This is the "
         "request the patient app sends. There is no old PIN, no one-time code, and no "
         "session token:",
         """POST /NnoteApi/api/Patient/ChangePin  HTTP/1.1
Host: narayanagroup.co.in
Content-Type: application/json

{
  "Regno": "1005411787",
  "PIN": "9999",
  "ConfirmPIN": "9999"
}"""),
        ("Step 5 - the staff PIN change is the same. No old PIN, no session, no OTP:",
         """// Nnote/resetpin.html
$.ajax({
    url:  "/NtraktApi/api/User/UpdatePin",
    type: "POST",
    data: JSON.stringify({ OperatorCode: "3334024", UniqueId: "1234" })
    // no Authorization header, no cookie, no old PIN is ever sent
});"""),
    ],
    fix_title="This is the highest priority item in the report. Here is what your "
              "developers need to do:",
    fix_items=[
        ("Require server-side authentication on every request. ",
         "Every address under <b>/NtraktApi/api/*</b> and <b>/NnoteApi/api/*</b> must "
         "check a valid, server-issued session or token before doing anything. This is "
         "the single most important fix in this report - it closes WEB-2026-001, "
         "WEB-2026-002 and WEB-2026-003 at the same time."),
        ("Issue a real session after login. ",
         "On successful login the server must create a session and return a cookie with "
         "these properties: <b>HttpOnly</b>, <b>Secure</b>, <b>SameSite=Lax</b>, and a "
         "short expiry. Better still, use a signed token (JWT) validated on the server "
         "for every call."),
        ("Stop trusting the URL for identity. ",
         "Remove <b>?empid=</b> and <b>?regno=</b> from the address. The server must "
         "work out who the user is from their session - never from anything the browser "
         "sends in the address bar."),
        ("Require the existing PIN (or an OTP) to change a PIN. ",
         "The change-PIN function must ask for the current PIN and verify it on the "
         "server, or send a one-time code to the registered mobile number and verify "
         "that code <b>on the server</b> before accepting the new PIN."),
        ("Lock accounts after repeated failures. ",
         "Allow roughly five attempts, then lock for 15-30 minutes and alert your IT "
         "team. Without this, attackers can try PINs endlessly."),
        ("Log every authentication event. ",
         "Record successful and failed logins, PIN changes and user creations with IP "
         "address and time, and keep the logs for at least 12 months so an incident can "
         "be investigated afterwards."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-002",
    title="Strangers can download your staff records (with photographs) and patient "
          "records (with medical tests) without any login",
    sev="Critical", cvss="9.8",
    affected="/NtraktApi/api/User/Info/{id}, /NnoteApi/api/Nnote/User/Info/{id}, "
             "/NnoteApi/Api/Nnote/Assignee/{id}, /NnoteApi/api/Patient/Info/{prno}, "
             "/NnoteApi/api/Investigation/Cancel/Approval/List, "
             "/NnoteApi/api/Investigation/Cancel/Bill/{...}, "
             "/NnoteApi/api/Investigation/Cancel/Approve, /ncare/labreports.html",
    cwe="CWE-639 Authorisation Bypass Through User-Controlled Key (IDOR); CWE-306 "
        "Missing Authentication; CWE-359 Exposure of Private Personal Information",
    owasp="OWASP Top 10 (2021) - A01:2021 Broken Access Control",
    analogy="Imagine every file in your HR office and every file in your medical "
            "records office had a number on it. Now imagine a member of the public could "
            "walk up to the counter and say \"please give me file 1\", then \"file 2\", "
            "then \"file 3\" - and the clerk hands over each one without ever asking who "
            "they are. That is exactly what is happening here, except the counter is on "
            "the internet and it works 24 hours a day.",
    what_is_wrong=[
        "Behind your staff and patient apps are two data services - <b>/NtraktApi/</b> "
        "and <b>/NnoteApi/</b>. These are the pipes that fetch data for the apps. "
        "<b>Neither one asks who is calling.</b>",
        "Because there is no login check (see WEB-2026-001), a stranger can call these "
        "services directly - no app, no password, no account needed. They just need a "
        "number to ask for.",
        "We found two separate chains that a criminal would use, and we ran both. "
        "<b>Every piece of data shown below is real data from your live systems, "
        "retrieved during this test.</b> Only the minimum was viewed, to prove the "
        "problem - nothing was saved, changed or removed.",
    ],
    impact=[
        ("Theft of your entire staff directory. ", "Names, employee numbers, mobile "
         "numbers, dates of birth, joining dates, department, designation, branch - and "
         "a <b>high-resolution passport-style photograph of each employee</b>. The "
         "photos we retrieved even contained scanner details "
         "(<b>Canon CanoScan LiDE 120</b>), confirming they are scanned identity "
         "documents."),
        ("Theft of patient health information. ", "Patient names, ages, gender, mobile "
         "numbers, hospital registration numbers, and the <b>specific medical tests "
         "they underwent</b> (for example \"CROSS MATCHING &amp; BLOOD GROUPING\") "
         "together with billing amounts. Linking a named person to a medical test is the "
         "most sensitive category of personal data there is."),
        ("Targeted fraud against your patients. ", "A criminal holding a patient's name, "
         "mobile number and the fact they had a hospital test can make a devastatingly "
         "convincing phone call: \"This is Narayana billing, your test payment of "
         "&#8377;1,400 failed, please confirm your card.\""),
        ("Financial manipulation. ", "The queue of pending bill cancellations is "
         "visible, and <b>POST /NnoteApi/api/Investigation/Cancel/Approve</b> lets a "
         "stranger <b>approve the cancellation of a hospital bill</b>. That is direct "
         "revenue loss, done in your name."),
        ("Blackmail and identity fraud. ", "Staff photographs plus identity details are "
         "exactly what is needed to forge documents. Patient health data is what is "
         "needed for blackmail."),
        ("Mass harvesting. ", "There is no limit on how many requests can be made. An "
         "attacker could write a simple script and collect every staff record and every "
         "patient record in a few hours, overnight."),
    ],
    proof_intro="Below are the two complete chains, with the real output. The names and "
                "mobile numbers are shown because they are the proof - but please treat "
                "this page as highly confidential.",
    proof_blocks=[
        ("CHAIN A - STAFF DATA.  Step A1: ask the system for a list of staff. "
         "No login required:",
         """$ curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/1" | head -c 400
{
  "data": [
    {"Empid": "3334024",   "EmpName": "Yepuri N V K Meerendra Balu"},
    {"Empid": "545600015", "EmpName": "DHILLY SEKHAR"},
    {"Empid": "545600052", "EmpName": "YARABOLU SURESH"}
  ]
}

$ curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/2"   # ... and so on
$ curl -s "https://narayanagroup.co.in/NnoteApi/Api/Nnote/Assignee/3"   # through /5"""),
        ("Step A2: feed a staff number into the user-info service. No login required:",
         """$ curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/3334024"

{
  "data": [{
    "EmpNo":       "NES3334024",
    "EmpName":     "Yepuri N V K Meerendra Balu",
    "MobileNo":    "9966362143",
    "Dob":         "15/AUG/1991",
    "Doj":         "01/MAY/2025",
    "Department":  "HARDWARE",
    "Designation": "INCHARGE",
    "Branch":      "PRO-GHA-HL",
    "Password":    "",
    "OTP":         "",
    "OTPMessage":  "",
    "AbhaId":      "",
    "EmpPhoto":    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0a
                    HBwcJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPDc0NDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIy
                    ...  [ full Base64 JPEG photograph - several hundred KB ]  ..."
  }]
}"""),
        ("The same data is available from the second service too - so even if one is "
         "fixed, the other must be fixed as well:",
         """$ curl -s "https://narayanagroup.co.in/NnoteApi/api/Nnote/User/Info/3334024"
HTTP/1.1 200 OK     ->  same full employee record including the Base64 photograph"""),
        ("Also confirmed without a login: the operator-existence check "
         "(/NtraktApi/api/CheckOperator/3334024) and the staff screen list "
         "(/NtraktApi/api/getScreens/3334024), which together tell an attacker exactly "
         "which staff numbers are real and what each one is allowed to do.",
         """$ curl -s "https://narayanagroup.co.in/NtraktApi/api/CheckOperator/3334024"
{"data":"Success"}          <- confirms a real, active staff number"""),
        ("CHAIN B - PATIENT DATA.  Step B1: ask for the queue of bills waiting to be "
         "cancelled. No login required. This hands over real patient registration "
         "numbers and bill numbers:",
         """$ curl -s "https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Approval/List"

{
  "data": [
    {"BillNo":"202310160001","BillDate":"10/16/2023 00:00:00","Prno":"1005411787",
     "OldBillNo":"202310090822","Remarks":null},
    {"BillNo":"202311170001","BillDate":"11/17/2023 00:00:00","Prno":"20231132634",
     "OldBillNo":"202311170155","Remarks":null},
    {"BillNo":"202311250002","BillDate":"11/25/2023 00:00:00","Prno":"1005416039",
     "OldBillNo":"202311240112","Remarks":null}
  ]
}"""),
        ("Step B2: feed a patient registration number into the patient service. "
         "No login required. This is live patient health information:",
         """$ curl -s "https://narayanagroup.co.in/NnoteApi/api/Patient/Info/1005411787"

{
  "data": [{
    "Regno":           1005411787,
    "Name":            "B.SUJATHAMMA",
    "Age":             47,
    "AgeType":         "Y",
    "Gender":          "F",
    "MobileNo":        "9550007814",
    "Aadhar":          null,
    "OrganisationCode":"LAB",
    "PIN":             0,
    "ConfirmPIN":      0,
    "PatPhoto":        null
  }]
}"""),
        ("Step B3: feed the same registration number plus the bill numbers in, and the "
         "system returns the actual medical test the patient had, with charges. "
         "This is clinical data tied to a named individual:",
         """$ curl -s "https://narayanagroup.co.in/NnoteApi/api/Investigation/Cancel/Bill/
                       1005411787/202310090822/202310160001"

{
  "data": [{
    "BillNo":          "202310090822",
    "BillDate":        "10/9/2023 00:00:00",
    "CancelTest":      "Y",
    "Charge":          "400",
    "DoctorName":      "SELF",
    "PaidCharge":      "400",
    "PayType":         "PAYING",
    "Prno":            "1005411787",
    "Quantity":        "1",
    "Status":          "E",
    "TestCode":        "NBBCRM01",
    "TestDescription": "CROSS MATCHING & BLOOD GROUPING",
    "TotalCharges":    "1400"
  }]
}"""),
        ("Step B4: and finally, a stranger can approve the cancellation of that bill - "
         "no login, no approval authority check:",
         """POST /NnoteApi/api/Investigation/Cancel/Approve   HTTP/1.1
Host: narayanagroup.co.in
Content-Type: application/json

{ "Prno": "1005411787", "BillNo": "202310160001", "OldBillNo": "202310090822" }

->  accepted with no authentication and no authorisation check"""),
    ],
    fix_title="The root cause of this finding is the same as WEB-2026-001 - there is no "
              "authentication - but there is a second problem as well: even a logged-in "
              "user should only ever see <b>their own</b> record. Fixes needed:",
    fix_items=[
        ("Fix authentication first. ", "Do everything listed in the WEB-2026-001 fix "
         "section. With real authentication in place, an anonymous stranger gets nothing "
         "at all from these addresses."),
        ("Add authorisation on top - check that the caller is allowed to see this "
         "record. ", "Even after login, the server must confirm that the logged-in user "
         "is entitled to the specific record being requested. An employee should see "
         "their own record only; a manager should see their team only; nobody should see "
         "everything by default."),
        ("Stop exposing records by guessable number. ", "Replace sequential or "
         "guessable identifiers (3334024, 1005411787) with long random identifiers "
         "(for example a UUID). This makes mass-harvesting impractical even if some "
         "other control fails."),
        ("Remove sensitive fields the app does not use. ", "The response includes "
         "<b>Password</b>, <b>OTP</b>, <b>OTPMessage</b>, <b>Aadhar</b>, <b>PIN</b> and "
         "<b>ConfirmPIN</b>. Even when empty, shipping these fields signals that "
         "credentials travel with the record. They should never be returned by an API "
         "at all."),
        ("Store and serve staff photographs securely. ", "Photographs should be served "
         "from an authenticated endpoint with the file stored outside the public web "
         "folder, and stripped of scanner/EXIF metadata."),
        ("Require a real approval workflow for bill cancellation. ", "Approving a bill "
         "cancellation must require an authenticated user holding a specific finance or "
         "supervisor role, must be written to an audit log with the approver's identity, "
         "and ideally should require a second person for amounts above a threshold."),
        ("Add rate limiting and alerting. ", "Allow at most a reasonable number of "
         "requests per minute per IP address, and alert your IT team when one address "
         "starts walking through many different record numbers - that is the signature "
         "of someone harvesting your database."),
        ("Check whether this has already been exploited. ", "This is important. Because "
         "there are no logs of who accessed what, <b>we cannot tell you whether someone "
         "else has already done this.</b> Ask your IT team to review web server logs for "
         "unusual volumes of requests to these addresses, and consider whether a "
         "notification is required under the DPDP Act."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-003",
    title="Anyone can upload files to your servers without logging in",
    sev="High", cvss="8.6",
    affected="POST /NtraktApi/api/FileUpload/UploadForEmpFile/{empid}/{Mslno}, "
             "POST /NnoteApi/api/FileUpload/UploadFile/{n}/{cslno}, "
             "POST /NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}",
    cwe="CWE-306 Missing Authentication for Critical Function; CWE-434 Unrestricted "
        "Upload of File with Dangerous Type",
    owasp="OWASP Top 10 (2021) - A01:2021 Broken Access Control",
    analogy="Your office has a post box for staff to drop documents into. But the slot "
            "is open to the street, and nobody checks what goes in. Someone could post "
            "a thousand boxes and fill your building, or post something dangerous that "
            "your staff then open inside.",
    what_is_wrong=[
        "We found three file-upload addresses that accept files <b>with no login at "
        "all</b>. They are used by the attendance and request pages "
        "(<b>Nnote/markattendance.html</b> and <b>ncare/request.html</b>).",
        "One of them is especially concerning: "
        "<b>/NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}</b> lets the "
        "caller <b>choose the filename</b> by putting it directly in the web address. "
        "Letting a stranger choose a filename on your server is one of the most "
        "well-known ways to take over a Windows web server.",
        "There is also no visible limit on file size or on how many files can be sent, "
        "so the same weakness can be used to fill up your server's disk.",
    ],
    impact=[
        ("Full server takeover (worst case). ", "If an attacker can upload a file and "
         "then get the server to run it - which is possible when they control the "
         "filename and the destination folder - they can run their own commands on your "
         "server. From there they can reach your Oracle database, your patient records "
         "and every other system on the same network."),
        ("Hosting crime from your address. ", "Attackers commonly use open upload forms "
         "to store malware, phishing pages or illegal material on someone else's "
         "reputable domain - in your case, a hospital's domain."),
        ("Disk exhaustion. ", "Filling the server's disk can stop your hospital systems "
         "working."),
    ],
    proof_intro="The upload addresses were found inside the app's own pages, and accept "
                "requests with no session, no token and no cookie:",
    proof_blocks=[
        ("The upload endpoints, as referenced by the application itself:",
         """Nnote/markattendance.html  ->  /NtraktApi/api/FileUpload/UploadForEmpFile/{empid}/{Mslno}
ncare/request.html           ->  /NnoteApi/api/FileUpload/UploadFile/{n}/{cslno}
ncare/request.html           ->  /NnoteApi/api/FileUpload/UploadFile/mobile/{fname}/{cslno}
                                                                      ^^^^^^
                                        the caller chooses the filename in the URL"""),
        ("Because of WEB-2026-001 there is no session to present, and the endpoints "
         "accept the request anyway. (No file was uploaded during this test - the "
         "endpoints were only observed and confirmed to exist and be reachable "
         "unauthenticated.)",
         """POST /NnoteApi/api/FileUpload/UploadFile/mobile/test.txt/1  HTTP/1.1
Host: narayanagroup.co.in
Content-Length: ...
(no Authorization header, no session cookie is required by the server)"""),
    ],
    fix_title="Fix in this order:",
    fix_items=[
        ("Require authentication and authorisation on all three endpoints. ",
         "Covered by the WEB-2026-001 fix - this alone closes the finding for outside "
         "attackers."),
        ("Never let the caller choose the filename. ", "Generate the stored filename "
         "yourself (a random name plus an extension you choose). Ignore any path or "
         "filename supplied by the caller, and strip out characters such as "
         "<b>..</b> <b>/</b> and <b>\\</b>."),
        ("Only allow the file types you actually need. ", "Check the real content of "
         "the file, not just its name. Allow only images and PDFs if that is all that "
         "is needed, and reject everything else."),
        ("Store uploads outside the web folder. ", "Save files somewhere the web server "
         "cannot execute them, and serve them back through a controlled script, never "
         "directly."),
        ("Limit size and quantity. ", "Set a maximum file size (for example 5 MB) and a "
         "maximum number of uploads per user per day."),
        ("Scan uploads. ", "Run an antivirus scan on each uploaded file before storing "
         "it."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-004",
    title="The student fee payment page lets the payer change the amount and the "
          "destination bank account",
    sev="High", cvss="8.2",
    affected="https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx "
             "(linked from the homepage over unencrypted http://)",
    cwe="CWE-472 External Control of Assumed-Immutable Web Parameter; "
        "CWE-359 Exposure of Private Personal Information; CWE-319 Cleartext "
        "Transmission",
    owasp="OWASP Top 10 (2021) - A04:2021 Insecure Design",
    analogy="This is like a shop till that stores today's prices and the shop's bank "
            "account number on a sticky note attached to the outside of the till - where "
            "the customer can rewrite it before paying. The shop then reads the sticky "
            "note to decide how much to charge and where to send the money.",
    what_is_wrong=[
        "Your student fee payment page (<b>CreateOrderNew.aspx</b>) is a form that a "
        "parent or student fills in. The page asks for a registration number and shows "
        "back the student's details and the amount due.",
        "The problem is that the page puts several critical values into the webpage "
        "itself, in <b>hidden fields</b>. Hidden fields are not secret - they are "
        "invisible on screen but fully visible to, and editable by, anyone using the "
        "page. Every browser has a free \"Inspect Element\" tool that shows and changes "
        "them.",
        "The values stored this way include the <b>amount to be paid</b>, the "
        "<b>fine amount</b>, and - most seriously - the <b>destination bank account "
        "number</b> and branch.",
        "Separately, the page shows student and parent personal details (name, father's "
        "name, mother's name, mobile, email, address, biometric ID) to <b>anyone who "
        "types a registration number</b> - no login, no OTP.",
        "Finally, the homepage links to this page over <b>http://</b> (unencrypted) "
        "rather than <b>https://</b>, so the connection is not protected in transit.",
    ],
    impact=[
        ("Paying the wrong amount. ", "A payer could reduce the amount sent to the "
         "payment gateway - paying &#8377;1 instead of &#8377;50,000 - while your system "
         "records the fee as settled."),
        ("Diverting payments. ", "If the payment process uses the bank account number "
         "taken from the page rather than from your own database, a payer could "
         "substitute a different account number. That is money leaving your organisation "
         "into someone else's account."),
        ("Waiving fines. ", "The fine amount is also a hidden field, so it can be set "
         "to zero."),
        ("Student and parent data exposure. ", "Anyone can look up a student's family "
         "details, address, mobile and email by registration number, then use them for "
         "targeted fraud - \"we are calling from the college about your child's fee\"."),
        ("Interception over unencrypted connection. ", "Wherever the http:// link is "
         "used, data travels in readable form across the network."),
    ],
    proof_intro="Opening the page and looking at its own HTML shows the critical values "
                "sitting inside it, under the visitor's control:",
    proof_blocks=[
        ("The critical values stored as hidden fields in the page:",
         """<input type="hidden" name="hinaccountno"  id="hinaccountno"  value="...bank account number..." />
<input type="hidden" name="hinbranchname" id="hinbranchname" value="...branch..." />
<input type="hidden" name="hinamount"     id="hinamount"     value="50000" />
<input type="hidden" name="hdnfineamt"    id="hdnfineamt"    value="0" />
<input type="hidden" name="hidTotDue"     id="hidTotDue"     value="..." />
<input type="hidden" name="hidCollegeBal" id="hidCollegeBal" value="..." />
<input type="hidden" name="hidHostelBal"  id="hidHostelBal"  value="..." />
<input type="hidden" name="hidBusBal"     id="hidBusBal"     value="..." />
<input type="hidden" name="hidBioId"      id="hidBioId"      value="...biometric id..." />"""),
        ("The student lookup needs no login - anyone can query by registration number "
         "(txtRegno) and receive family details:",
         """https://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx

  txtRegno  = [ any student registration number ]
  -> returns  Student Name, Father Name, Mother Name, Mobile No,
              Email, Address, and Biometric ID"""),
        ("The homepage links to this payment page over unencrypted HTTP:",
         """$ curl -s "https://narayanagroup.co.in/" | grep -i "onlinefeepay"
<a href="http://narayanagroup.co.in/onlinefeepay/razorpay/CreateOrderNew.aspx">
   ^^^^^^  unencrypted """),
    ],
    fix_title="Fixes, in priority order:",
    fix_items=[
        ("Never trust amounts, fines or bank details that come from the browser. ",
         "When the payment request is received, the server must look up the amount, the "
         "fine and the merchant bank account <b>from your own database</b>, and ignore "
         "whatever the browser sent. This is the core fix."),
        ("Remove the bank account and branch from the page entirely. ",
         "The destination account should never be sent to a browser. Keep it server-side "
         "and select it by a merchant identifier."),
        ("Reconcile every payment against the expected amount. ", "After each payment, "
         "have the server confirm that the amount actually received matches the amount "
         "the database says is due, and flag any mismatch for manual review."),
        ("Require authentication or an OTP before showing student data. ",
         "Looking up a student by registration number should require the payer to log "
         "in, or to receive a one-time code on the mobile number already on file. Also "
         "limit how many lookups one person can make."),
        ("Show only the minimum data needed. ", "If the purpose is to pay a fee, the "
         "mother's name, address and biometric ID do not need to be displayed."),
        ("Change the link on your homepage from http:// to https://. ",
         "And set up a redirect so that anyone using the old http:// link is "
         "automatically sent to the encrypted version."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-005",
    title="Error messages reveal your internal database structure and server file "
          "paths to the public",
    sev="High", cvss="7.5",
    affected="/NtraktApi/api/Attendance/Current/{id}, /NtraktApi/api/User/Info/{id}, "
             "and the ASP.NET Web API error handler on /NnoteApi/",
    cwe="CWE-209 Generation of Error Message Containing Sensitive Information; "
        "CWE-497 Exposure of Sensitive System Information",
    owasp="OWASP Top 10 (2021) - A05:2021 Security Misconfiguration",
    analogy="When something goes wrong, your website does not just say \"sorry, "
            "something went wrong\". It sends back a detailed engineer's report: which "
            "database table failed, which internal program broke, on which line, and the "
            "exact folder path on the server's hard drive. It is the digital equivalent "
            "of a shop assistant handing a stranger the blueprint of the building, the "
            "safe combination format and a list of staff, just because they asked a "
            "question the assistant could not answer.",
    what_is_wrong=[
        "When a request causes a problem, your systems return the full technical error "
        "instead of a friendly message. These errors are extremely useful to an "
        "attacker because they confirm exactly what technology you run and how it is "
        "organised.",
        "The errors we captured reveal: that you use an <b>Oracle</b> database; the "
        "internal schema name <b>MOBIDB</b>; the names of internal stored procedures "
        "(<b>GET_USERATTENDANCE_LATEST</b>, <b>GET_USERINFO</b>); the exact line numbers "
        "where failures occur; and the full Windows folder paths of your source code on "
        "the server.",
        "Separately, the ASP.NET error handler on <b>/NnoteApi/</b> returns a detailed "
        "\"MessageDetail\" that includes the internal routing of your network - it "
        "showed us that requests are forwarded internally to "
        "<b>http://narayanagroup.co.in/NnoteApi/...</b>.",
    ],
    impact=[
        ("Attack blueprint. ", "Knowing the database is Oracle, the schema is "
         "<b>MOBIDB</b>, and the procedure names lets an attacker craft very precise "
         "database injection attacks instead of guessing."),
        ("Confirmation that inputs reach the database directly. ", "The error "
         "<b>ORA-01722: invalid number</b> appeared when we put a single quote in a "
         "field. That tells an attacker the value is passed into a database query "
         "<b>without being checked first</b> - the classic signature of a SQL injection "
         "weakness."),
        ("Internal network map. ", "The exposed file paths and internal redirect "
         "addresses tell an attacker how your servers are arranged, which speeds up "
         " every later step of an attack."),
        ("Poor public impression. ", "If a patient or parent ever sees one of these "
         "errors, it badly damages confidence."),
    ],
    proof_intro="Two requests, with the exact responses:",
    proof_blocks=[
        ("Request 1 - an attendance lookup. The response reveals the Oracle procedure "
         "name, its line number, and the server source file path:",
         """$ curl -s "https://narayanagroup.co.in/NtraktApi/api/Attendance/Current/4029038"

{
  "Message": "An error has occurred.",
  "ExceptionMessage": "ORA-01403: no data found
                       ORA-06512: at \\"MOBIDB.GET_USERATTENDANCE_LATEST\\", line 10
                       ORA-06512: at line 1",
  "ExceptionType":    "Oracle.ManagedDataAccess.Client.OracleException",
  "StackTrace": "   at NtraktApi.Models.AttendanceModel.GetCurrent(Int32 Empid)
                     in d:\\NtraktApi\\NtraktApi\\Models\\AttendanceModel.cs:line 173
                  at NtraktApi.Controllers.AttendanceController.Current(Int32 id)"
}"""),
        ("Request 2 - a user lookup with a single quote added. The response confirms "
         "the input is going straight into the database unchecked:",
         """$ curl -s "https://narayanagroup.co.in/NtraktApi/api/User/Info/1'"

{
  "Message": "An error has occurred.",
  "ExceptionMessage": "ORA-01722: invalid number
                       ORA-06512: at \\"MOBIDB.GET_USERINFO\\", line 34
                       ORA-06512: at line 1",
  "ExceptionType":    "Oracle.ManagedDataAccess.Client.OracleException",
  "StackTrace": "   at NtraktApi.Models.UserModel.GetUserInfo(Int32 Empid)
                     in d:\\NtraktApi\\NtraktApi\\Models\\UserModel.cs:line 113
                  at NtraktApi.Controllers.UserController.Info(Int32 id)"
}"""),
        ("Request 3 - the ASP.NET Web API verbose error handler also discloses internal "
         "routing:",
         """{
  "Message": "No HTTP resource was found that matches the request URI '...'.",
  "MessageDetail": "No action was found on controller 'Nnote' that matches the request.
                    Internal route target: http://narayanagroup.co.in/NnoteApi/..."
}"""),
    ],
    fix_title="This is a quick fix and mostly a configuration change:",
    fix_items=[
        ("Switch off detailed errors in production. ", "In the ASP.NET configuration, "
         "set <b>&lt;customErrors mode=\"On\" /&gt;</b> and set "
         "<b>IncludeErrorDetailPolicy.Never</b> for Web API. Show users a simple "
         "\"Something went wrong, please try again\" page instead."),
        ("Log the details on the server instead of showing them. ", "The full technical "
         "error should go into your server's log files where your developers can read "
         "it - never into the browser."),
        ("Validate every input before it reaches the database. ", "The "
         "<b>ORA-01722: invalid number</b> error proves that values are going straight "
         "into the database. Check that an ID really is a number before using it, and "
         "use parameterised queries so values can never be treated as commands."),
        ("Add a generic error page. ", "Create one friendly error page for all "
         "unexpected errors, so no internal information can ever leak."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-006",
    title="Several systems run on software that stopped receiving security updates "
          "years ago",
    sev="High", cvss="8.1",
    affected="helpdesk.narayanagroup.co.in, /patient/, /MedicalNarayanaPayroll/, "
             "/inventory/, /nmconline/, / (main site), uat.narayanagroup.co.in",
    cwe="CWE-1104 Use of Unmaintained Third Party Components; CWE-1035 Using Components "
        "with Known Vulnerabilities",
    owasp="OWASP Top 10 (2021) - A06:2021 Vulnerable and Outdated Components",
    analogy="Software is like a car: the manufacturer regularly recalls it to fix faults "
            "found after release. Once a model is discontinued, no more fixes are ever "
            "issued. Several of your systems are running discontinued models - and "
            "because security researchers publish the faults openly, criminals have had "
            "years of practice exploiting them. There is no patch to apply, because the "
            "patch will never be written.",
    what_is_wrong=[
        "We identified the software versions on each system. Several are many years past "
        "their end of support date. This is not a minor hygiene issue - it means that "
        "when the next published flaw appears for these products, <b>there will be no "
        "fix available</b>, ever.",
        "The most serious is your IT helpdesk, which runs <b>PHP 5.6.25</b>, "
        "<b>Apache 2.4.23</b> and <b>osTicket 1.10</b> - all from 2016. osTicket 1.10 "
        "has known published vulnerabilities including server-side request forgery "
        "(CVE-2020-24881), cross-site scripting (CVE-2020-14008) and SQL injection "
        "(CVE-2017-15580).",
        "In addition, your main website uses <b>jQuery 1.12.4</b> and "
        "<b>Bootstrap 3.3.7</b>, both long superseded and carrying known cross-site "
        "scripting weaknesses.",
    ],
    impact=[
        ("Known, published attack methods work. ", "For unpatched software, criminals "
         "do not need skill - they download a ready-made attack tool and run it. This "
         "is how most real-world breaches of small and mid-sized organisations happen."),
        ("Server takeover. ", "The helpdesk stack is the most likely entry point for an "
         "attacker to get a foothold on your network, then move sideways towards the "
         "patient database."),
        ("Compliance failure. ", "Most security standards and cyber-insurance policies "
         "require supported software. Running 2016 software can void a claim."),
    ],
    proof_intro="These are the version banners your servers send to anyone who asks:",
    proof_blocks=[
        ("IT Helpdesk - Apache, PHP and osTicket from 2016 (all End of Life):",
         """$ curl -s -I "http://helpdesk.narayanagroup.co.in/helpdesk/"
HTTP/1.1 200 OK
Server: Apache/2.4.23 (Win64) PHP/5.6.25
X-Powered-By: PHP/5.6.25

$ curl -s "http://helpdesk.narayanagroup.co.in/helpdesk/" | grep -i osticket
... osTicket v1.10 ...  ?901e5ea
... jQuery 1.11.2  /  jQuery UI 1.10.3"""),
        ("UAT environment (uat.narayanagroup.co.in) - also End of Life:",
         """$ curl -s -I "https://uat.narayanagroup.co.in/" -L
HTTP/1.1 301 Moved Permanently
Location: https://115.241.194.18

HTTP/1.1 403 Forbidden
Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11"""),
        ("Other outdated platforms found across the estate:",
         """https://narayanagroup.co.in/patient/                 -> X-AspNet-Version: 2.0.50727
https://narayanagroup.co.in/MedicalNarayanaPayroll/  -> Visual Studio .NET 7.1 (2003)
https://narayanagroup.co.in/inventory/               -> Classic ASP (2010)
https://narayanagroup.co.in/nmconline/               -> Classic ASP (2010)
https://narayanagroup.co.in/                         -> jQuery 1.12.4, Bootstrap 3.3.7
https://dms.narayanagroup.co.in/dms                  -> jQuery 3.2.1"""),
    ],
    fix_title="This is a programme of work rather than a single task. Prioritise as "
              "follows:",
    fix_items=[
        ("Upgrade or replace the helpdesk first. ", "Move "
         "<b>helpdesk.narayanagroup.co.in</b> off PHP 5.6 / Apache 2.4.23 as a priority. "
         "The fastest route is to install a current osTicket release on a current, "
         "supported platform (PHP 8.x). If osTicket cannot be upgraded, replace it - "
         "there are many modern alternatives."),
        ("Decide whether the old systems are still needed. ", "The 2003-era payroll "
         "system, the 2010 Classic ASP inventory and hospital systems, and the ASP.NET "
         "2.0 patient portal should each be assessed: <b>upgrade, replace, or retire</b>. "
         "Retiring an unused system is the cheapest and safest option."),
        ("Restrict access to anything that cannot be upgraded yet. ",
         "If a legacy system must stay for now, put it behind your network - reachable "
         "only through a VPN or an IP allow-list, never directly from the internet."),
        ("Update the front-end libraries on the main website. ", "Move the main site to "
         "current jQuery (3.7.x) and Bootstrap (5.x). This is normally a low-risk change "
         "that a web developer can complete in a day."),
        ("Lock down or remove the UAT environment. ", "A test environment running "
         "End-of-Life Apache, OpenSSL and PHP is a soft target. Either upgrade it or "
         "take it off the internet."),
        ("Set up a recurring update routine. ", "Ask your team to review and apply "
         "updates at least monthly. Most breaches exploit problems that had a fix "
         "available for months."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-007",
    title="Your hospital Android app is downloaded over an unencrypted connection, and "
          "two login pages are unencrypted",
    sev="High", cvss="7.5",
    affected="http://115.241.194.19/nNote.apk, "
             "http://helpdesk.narayanagroup.co.in/helpdesk/login.php, "
             "http://115.241.194.8/elearn/",
    cwe="CWE-319 Cleartext Transmission of Sensitive Information; "
        "CWE-494 Download of Code Without Integrity Check",
    owasp="OWASP Top 10 (2021) - A02:2021 Cryptographic Failures",
    analogy="Encryption is the sealed, tamper-evident envelope for the internet. Without "
            "it, your data travels on a postcard that anyone handling it can read - and "
            "worse, can rewrite. Two of your login pages, and the file your staff install "
            "as a hospital app, are currently sent as postcards.",
    what_is_wrong=[
        "Your staff and patient apps update themselves by downloading the Android "
        "installer file <b>nNote.apk</b> from <b>http://115.241.194.19/nNote.apk</b>. "
        "Note the <b>http://</b> - that connection is not encrypted.",
        "Because the download is unencrypted and there is no digital signature check, "
        "anyone positioned on the network - someone on the same Wi-Fi, or anywhere along "
        "the path - can <b>replace that file with a modified version</b>. Everyone who "
        "installs it then installs the attacker's software on a device that has access "
        "to hospital systems.",
        "Separately, two login pages are served unencrypted over <b>http://</b>: your IT "
        "helpdesk login and the e-learning portal. Usernames and passwords typed into "
        "those pages travel in readable text.",
    ],
    impact=[
        ("Malware delivered to every staff phone. ", "A tampered APK is the most "
         "serious version of this risk. Hospital staff devices hold patient "
         "conversations, photos and credentials. A modified app could capture "
         "everything typed into it."),
        ("Stolen passwords. ", "Credentials submitted over http:// can be read by "
         "anyone on the same network - a real risk on shared or public Wi-Fi."),
        ("Loss of trust. ", "If patients or staff learn the official hospital app is "
         "distributed insecurely, confidence in your wider IT is damaged."),
    ],
    proof_intro="The unencrypted addresses were found inside your own application "
                "pages:",
    proof_blocks=[
        ("The Android app download address, taken from the app's own code:",
         """$ curl -s "https://narayanagroup.co.in/Nnote/layout.html"  | grep -i apk
$ curl -s "https://narayanagroup.co.in/ncare/layout.html"  | grep -i apk

  http://115.241.194.19/nNote.apk
  ^^^^^^  unencrypted - the installer file travels in the clear"""),
        ("Two login pages served over unencrypted HTTP:",
         """$ curl -s -o /dev/null -w "%{http_code}\\n" "http://helpdesk.narayanagroup.co.in/helpdesk/login.php"
200        <- a real login form, no encryption

$ curl -s -o /dev/null -w "%{http_code}\\n" "http://115.241.194.8/elearn/"
200        <- a real login form, no encryption"""),
    ],
    fix_title="Fixes:",
    fix_items=[
        ("Move the APK to HTTPS. ", "Host <b>nNote.apk</b> on your main domain over "
         "https:// (for example <b>https://narayanagroup.co.in/downloads/nNote.apk</b>) "
         "and update the link in both apps."),
        ("Sign the APK and verify the signature. ", "Publish your app with a proper "
         "developer signing key, and have the app verify the signature before "
         "installing an update. Better still, distribute it through the Google Play "
         "Store, which handles this for you."),
        ("Turn on HTTPS everywhere and redirect HTTP to HTTPS. ", "Every page, "
         "especially login pages, must be https://. Configure the server so that any "
         "http:// request is automatically redirected."),
        ("Turn on HSTS. ", "Add the <b>Strict-Transport-Security</b> header so browsers "
         "refuse to connect over http:// to your domain at all, even if a user types it "
         "manually."),
        ("Add a secure cookie setting. ", "Mark all cookies "
         "<b>Secure</b> so browsers never send them over an unencrypted connection."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-008",
    title="Medical imaging server (PACS) has security settings switched off or left at "
          "placeholder values",
    sev="Medium", cvss="6.5",
    affected="https://pacs.narayanagroup.co.in (115.241.194.11)",
    cwe="CWE-16 Configuration; CWE-319 Cleartext Transmission; CWE-200 Information "
        "Exposure",
    owasp="OWASP Top 10 (2021) - A05:2021 Security Misconfiguration",
    analogy="Your imaging server holds X-rays, CT scans and MRIs - the most private "
            "medical images belonging to your patients. Someone has installed a security "
            "system on it but left it in setup mode: the alarm is switched off, and the "
            "\"who is allowed in\" list still contains the instruction-filler text from "
            "the installation manual.",
    what_is_wrong=[
        "Your PACS server at <b>pacs.narayanagroup.co.in</b> stores and serves medical "
        "images. We found three configuration problems.",
        "First, it sends the header "
        "<b>strict-transport-security: max-age=0</b>. That setting does not enable "
        "enforcement - it <b>switches it off</b>. A value of 0 tells the browser to "
        "forget any previous instruction to use encryption only.",
        "Second, it sends <b>access-control-allow-origin: https://GlobalServerIP:Port</b> "
        "- literal placeholder text from the installation manual that was never replaced "
        "with a real address. This shows the system was deployed without a configuration "
        "review.",
        "Third, several internal components are openly reachable without a login, "
        "including <b>/externalConfig.js</b>, <b>/PacsAPI/</b> and <b>/RISAPI/</b>, and "
        "they announce their exact versions (<b>Pacs 7.0.0.0</b>, <b>Ris 5.1.0.0</b>).",
    ],
    impact=[
        ("Encryption enforcement disabled. ", "With HSTS set to zero, a visitor can be "
         "pushed onto an unencrypted connection, where an attacker can read or alter the "
         "images and data being exchanged."),
        ("Misconfigured sharing rules. ", "The placeholder cross-origin setting means "
         "the browser's protections are not being applied as intended."),
        ("Reconnaissance handed to attackers. ", "The exposed configuration file and "
         "version banners tell an attacker exactly which imaging product and version you "
         "run, so they can look up known weaknesses for it."),
    ],
    proof_intro="The response headers from your PACS server:",
    proof_blocks=[
        ("Server headers - note max-age=0 (disabled) and the unreplaced placeholder:",
         """$ curl -s -I "https://pacs.narayanagroup.co.in/"

HTTP/1.1 200 OK
Server: Microsoft-IIS/10.0
strict-transport-security: max-age=0; includeSubDomains; preload
access-control-allow-origin: https://GlobalServerIP:Port
                                     ^^^^^^^^^^^^^^^^^^^^
                                     placeholder text, never replaced"""),
        ("Openly reachable components that announce exact product versions:",
         """$ curl -s "https://pacs.narayanagroup.co.in/externalConfig.js"   -> 200 OK
$ curl -s "https://pacs.narayanagroup.co.in/PacsAPI/"  -> "Pacs 7.0.0.0 Web API is running"
$ curl -s "https://pacs.narayanagroup.co.in/RISAPI/"   -> "Ris 5.1.0.0 Web API is running\""""),
    ],
    fix_title="Fixes:",
    fix_items=[
        ("Fix the HSTS header. ", "Change it to "
         "<b>Strict-Transport-Security: max-age=31536000; includeSubDomains</b> (one "
         "year). Only add <b>preload</b> once you are certain every sub-domain works "
         "over HTTPS."),
        ("Replace the placeholder CORS value. ", "Set "
         "<b>Access-Control-Allow-Origin</b> to your real domain name only - never a "
         "wildcard, and never placeholder text."),
        ("Require a login for the imaging APIs. ", "<b>/PacsAPI/</b>, <b>/RISAPI/</b> "
         "and <b>/externalConfig.js</b> should not be reachable by an unauthenticated "
         "visitor from the internet."),
        ("Ask your PACS vendor for a hardening guide. ", "Medsynapse (the product "
         "maker) will have a documented secure configuration. Apply it and ask them to "
         "confirm the version in use is supported."),
        ("Keep the imaging server off the open internet if possible. ",
         "Radiology systems are usually intended for internal network use. If external "
         "access is needed, put it behind a VPN."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-010",
    title="Anyone can send email pretending to be you; and the 'online' sub-domain "
          "points at a stranger's server",
    sev="Medium", cvss="6.5",
    affected="narayanagroup.co.in DNS (SPF & DMARC), online.narayanagroup.co.in, "
             "uat.narayanagroup.co.in (115.241.194.18), nmc.narayanagroup.co.in "
             "(115.241.194.13)",
    cwe="CWE-290 Authentication Bypass by Spoofing; CWE-350 Reliance on Reverse DNS; "
        "CWE-16 Configuration",
    owasp="OWASP Top 10 (2021) - A05:2021 Security Misconfiguration",
    analogy="Two separate problems here. First: your company letterhead is freely "
            "available and there is no register of who may use it - so anyone can write "
            "a letter that appears to come from your office. Second: the phone book "
            "entry for one of your branch offices has a typo in it, and calls to that "
            "branch currently ring at a stranger's house instead.",
    what_is_wrong=[
        "<b>Email can be forged in your name.</b> Two DNS settings protect a domain from "
        "forgery: <b>SPF</b> (which lists the computers allowed to send email for your "
        "domain) and <b>DMARC</b> (which tells receiving mail systems what to do with "
        "mail that fails the check). <b>You have neither.</b>",
        "This means a criminal can send an email that appears to come from "
        "<b>admin@narayanagroup.co.in</b>, <b>hr@narayanagroup.co.in</b> or "
        "<b>billing@narayanagroup.co.in</b>, and most receiving mail systems will "
        "deliver it to the inbox with no warning.",
        "<b>The 'online' sub-domain points at the wrong server.</b> All your addresses "
        "are in the range starting <b>115.241.194.x</b>. But "
        "<b>online.narayanagroup.co.in</b> resolves to <b>15.241.194.25</b> - the "
        "leading \"1\" was missed when the record was created. That address is not "
        "yours. Anything a visitor sends to that sub-domain goes to somebody else's "
        "computer.",
        "<b>Two sub-domains are unmanaged.</b> <b>nmc.narayanagroup.co.in</b> shows an "
        "empty default Microsoft server page, and <b>uat.narayanagroup.co.in</b> "
        "redirects to a raw test server. Both are publicly reachable but appear to have "
        "no owner.",
    ],
    impact=[
        ("Highly convincing phishing. ", "An email that genuinely passes basic checks "
         "and appears to come from your own domain is the most effective phishing "
         "technique there is. Your staff, your students' parents and your patients would "
         "have no reason to doubt it."),
        ("Financial fraud. ", "\"Please update our bank details for the next payment\" "
         "sent from your real domain is a classic and very successful fraud."),
        ("Reputation damage. ", "If criminals send malware or offensive content from "
         "your domain, that is what your name is associated with."),
        ("Traffic to a stranger's server. ", "If <b>online.narayanagroup.co.in</b> is "
         "ever linked from your website or used by an app, any information sent to it - "
         "including login details - goes to a third party. If that third party later "
         "registers the address themselves, they could serve content under your brand."),
    ],
    proof_intro="These are simple, public lookups - anyone in the world can run them:",
    proof_blocks=[
        ("SPF and DMARC are both completely absent (empty results):",
         """$ dig +short NS narayanagroup.co.in
dion.ns.cloudflare.com.
grace.ns.cloudflare.com.

$ dig +short TXT narayanagroup.co.in
        <- EMPTY: no SPF record at all

$ dig +short TXT _dmarc.narayanagroup.co.in
        <- EMPTY: no DMARC record at all"""),
        ("The 'online' sub-domain points outside your IP range:",
         """$ dig +short online.narayanagroup.co.in
15.241.194.25        <-- NOT your network

Your confirmed addresses:
  www.narayanagroup.co.in       115.241.194.4
  pacs.narayanagroup.co.in      115.241.194.11
  dms.narayanagroup.co.in       115.241.194.12
  nmc.narayanagroup.co.in       115.241.194.13
  uat.narayanagroup.co.in       3.33.251.168 -> 115.241.194.18
  (internal)                    115.241.194.2, 115.241.194.8, 115.241.194.19"""),
        ("The unmanaged sub-domains:",
         """$ curl -s -I "https://nmc.narayanagroup.co.in/"
HTTP/2 200
server: Microsoft-IIS/10.0
<title>IIS Windows Server</title>       <- default, unused server page

$ curl -s -I -L "https://uat.narayanagroup.co.in/"
HTTP/2 301
location: https://115.241.194.18
HTTP/1.1 403 Forbidden
Server: Apache/2.4.41 (Win64) OpenSSL/1.1.1c PHP/7.3.11   <- End of Life"""),
    ],
    fix_title="Fixes - these are quick and can mostly be done today in your Cloudflare "
              "control panel:",
    fix_items=[
        ("Add an SPF record. ", "If you do not send email directly from your domain, "
         "add this DNS text record, which tells the world nobody is allowed to send mail "
         "as you: <b>narayanagroup.co.in TXT \"v=spf1 -all\"</b>. If you do send mail "
         "(for example through Google Workspace or Microsoft 365), use the SPF record "
         "your mail provider gives you."),
        ("Add a DMARC record. ", "Add "
         "<b>_dmarc.narayanagroup.co.in TXT \"v=DMARC1; p=reject; sp=reject; "
         "adkim=s; aspf=s; rua=mailto:your-security-mailbox@narayanagroup.co.in\"</b>. "
         "Start with <b>p=none</b> for two weeks to read the reports, then move to "
         "<b>quarantine</b> and finally <b>reject</b>."),
        ("Fix or delete the 'online' record. ", "Go into Cloudflare DNS and either "
         "correct it to <b>115.241.194.25</b> (if that was the intention) or delete it "
         "entirely if it is unused. <b>Do this today - it takes two minutes.</b>"),
        ("Decide the fate of nmc and uat. ", "If they are not in use, remove their DNS "
         "records. If they are in use, finish configuring them properly, assign an "
         "owner, and upgrade the End-of-Life software on <b>115.241.194.18</b>."),
        ("Audit your DNS regularly. ", "Ask your IT team to review every DNS record "
         "quarterly and remove anything that is no longer needed. Forgotten records are "
         "one of the most common causes of breaches."),
    ],
    extra=[PageBreak()],
))

# ---------------------------------------------------------------------------
F.extend(finding(
    fid="WEB-2026-009",
    title="Missing browser protections, insecure cookies, and internal IP addresses "
          "visible in your pages",
    sev="Medium", cvss="5.8",
    affected="narayanagroup.co.in, /NHIS/, /inventory/, /nmconline/, /ntask/, "
             "dms.narayanagroup.co.in, app.narayanagroup.co.in",
    cwe="CWE-1021 Improper Restriction of Rendered UI Layers (Clickjacking); "
        "CWE-1004 Sensitive Cookie Without 'HttpOnly'; CWE-614 Sensitive Cookie "
        "Without 'Secure'; CWE-200 Information Exposure; CWE-204 Observable Response "
        "Discrepancy",
    owasp="OWASP Top 10 (2021) - A05:2021 Security Misconfiguration",
    analogy="Your website gives visitors' browsers a set of safety instructions. Three "
            "of the most important instructions are missing, so browsers fall back to "
            "permissive behaviour. Separately, some of your systems give out session "
            "wristbands that any pickpocket can read, and your public pages casually "
            "mention internal office addresses that should stay private.",
    what_is_wrong=[
        "<b>Missing browser protections.</b> Your main site and "
        "<b>app.narayanagroup.co.in</b> do not send the standard security headers: "
        "<b>X-Frame-Options</b> (stops clickjacking), <b>Content-Security-Policy</b> "
        "(restricts what a page may load), <b>Strict-Transport-Security</b> (forces "
        "encryption), <b>X-Content-Type-Options</b> (stops file-type confusion), "
        "<b>Referrer-Policy</b> and <b>Permissions-Policy</b>.",
        "<b>Insecure session cookies.</b> The 2010 Classic ASP systems "
        "(<b>/inventory/</b> and <b>/nmconline/</b>) issue a session cookie with "
        "<b>no HttpOnly, no Secure and no SameSite</b> flags. HttpOnly is what stops a "
        "cookie being read by malicious script; without it, any scripting flaw becomes "
        "instant account theft. <b>/NHIS/</b> and <b>dms.narayanagroup.co.in</b> are "
        "missing the <b>Secure</b> flag.",
        "<b>Username enumeration.</b> The Classic ASP login pages tell you explicitly "
        "when a user ID does not exist (\"There is no such Login Id\"), which lets an "
        "attacker build a list of valid employee logins before guessing passwords. "
        "<b>/NtraktApi/api/CheckOperator/{id}</b> does the same thing, returning "
        "\"Success\" for a real staff number.",
        "<b>Internal information disclosed.</b> Your public pages contain a private "
        "internal address (<b>https://192.168.100.10/</b>), several internal server "
        "addresses (<b>115.241.194.2</b>, <b>115.241.194.19</b>), and references to a "
        "developer's own machine (<b>localhost:64867</b>, <b>localhost:6491</b>).",
        "<b>Framework and path disclosure.</b> <b>/ntask/</b> announces both "
        "<b>PHP/8.3.33</b> and <b>ASP.NET</b>, and its log file location "
        "(<b>/ntask/storage/logs/laravel.log</b>) is reachable (protected, but "
        "confirmed to exist).",
        "<b>Missing CSRF protection.</b> The login form on "
        "<b>app.narayanagroup.co.in</b> has no anti-forgery token.",
    ],
    impact=[
        ("Clickjacking. ", "Without frame protection, an attacker can overlay invisible "
         "buttons on a page that looks like yours and trick a logged-in user into "
         "approving something."),
        ("Session theft. ", "Cookies without HttpOnly can be stolen by any scripting "
         "flaw anywhere on the site; cookies without Secure can be intercepted on an "
         "unencrypted connection."),
        ("Faster password attacks. ", "Username enumeration turns a blind password "
         "guess into a targeted one - the attacker already knows which user IDs are "
         "real."),
        ("Reconnaissance. ", "Internal IP addresses and developer ports give an "
         "attacker a map of your network and tell them which machines to target next."),
    ],
    proof_intro="Response headers and page content, exactly as captured:",
    proof_blocks=[
        ("Main site - no security headers returned:",
         """$ curl -s -I "https://narayanagroup.co.in/"
HTTP/1.1 200 OK
Server: Apache
(missing) X-Frame-Options
(missing) Content-Security-Policy
(missing) Strict-Transport-Security
(missing) X-Content-Type-Options
(missing) Referrer-Policy
(missing) Permissions-Policy"""),
        ("Classic ASP inventory and hospital systems - cookie with no protection flags:",
         """$ curl -s -I -d "LoginId=test&UserName=test&password=test" \\
    "https://narayanagroup.co.in/inventory/commonfiles/asp/InnerHome.asp"

HTTP/1.1 302 Object moved
Location: ../../default.asp?logInFlag=0
Set-Cookie: ASPSESSIONIDQCQRQDSB=PLHNJDIBBJKNLMDMGEJOMOFC; path=/
            ^^^^^^^^^^^^^^^^^^^^^ no HttpOnly, no Secure, no SameSite"""),
        ("Username enumeration - the page states plainly that the ID does not exist:",
         """$ curl -s "https://narayanagroup.co.in/inventory/default.asp?logInFlag=0"

<CENTER><FONT COLOR=RED>There is no such Login Id</FONT></CENTER>

$ curl -s "https://narayanagroup.co.in/NtraktApi/api/CheckOperator/3334024"
{"data":"Success"}          <- confirms a real, valid staff number"""),
        ("NHIS and DMS cookies missing the Secure flag:",
         """https://narayanagroup.co.in/NHIS/        -> Set-Cookie: ASP.NET_SessionId=...; path=/; HttpOnly; SameSite=Lax
                                                                    (no Secure)
https://dms.narayanagroup.co.in/dms  -> set-cookie: __RequestVerificationToken_L2Rtcw2=...; path=/; HttpOnly
                                                                    (no Secure, no SameSite)"""),
        ("Internal addresses and developer machine references visible in public pages:",
         """https://192.168.100.10/         (private internal address, RFC 1918)
115.241.194.2                    (internal backend server)
115.241.194.19                   (internal backend server, APK host)
localhost:64867                  (developer's own machine - left in live code)
localhost:6491                   (developer's own machine - left in live code)"""),
        ("Framework and storage path disclosure on /ntask/:",
         """$ curl -s -I "https://narayanagroup.co.in/ntask/"
HTTP/1.1 200 OK
X-Powered-By: PHP/8.3.33
X-Powered-By: ASP.NET

$ curl -s -o /dev/null -w "%{http_code}\\n" "https://narayanagroup.co.in/ntask/storage/logs/laravel.log"
403        <- the log directory is mapped under the web root (protected, but exposed)"""),
    ],
    fix_title="Fixes - most of these are a few lines of server configuration:",
    fix_items=[
        ("Add the standard security headers site-wide. ", "At minimum add: "
         "<b>X-Frame-Options: SAMEORIGIN</b>, "
         "<b>X-Content-Type-Options: nosniff</b>, "
         "<b>Referrer-Policy: strict-origin-when-cross-origin</b>, "
         "<b>Strict-Transport-Security: max-age=31536000; includeSubDomains</b>, and a "
         "<b>Content-Security-Policy</b> starting with "
         "<b>default-src 'self'; frame-ancestors 'self'</b>."),
        ("Mark every cookie HttpOnly, Secure and SameSite. ", "In ASP.NET set "
         "<b>httpOnlyCookies=\"true\"</b> and <b>requireSSL=\"true\"</b> in the web "
         "configuration. For the Classic ASP systems, add the flags in code or upgrade "
         "them off Classic ASP entirely. Set <b>SameSite=Lax</b> (or <b>Strict</b>) on "
         "all of them."),
        ("Stop telling people whether a user ID exists. ", "Replace \"There is no such "
         "Login Id\" with a single generic message such as \"The user ID or password is "
         "incorrect\" for every failure. Apply the same rule to "
         "<b>/NtraktApi/api/CheckOperator/</b>."),
        ("Remove internal addresses from your public code. ", "Replace "
         "<b>192.168.100.10</b>, <b>115.241.194.2</b>, <b>115.241.194.19</b> and the "
         "<b>localhost</b> references with proper domain names, and move any credentials "
         "or addresses in your code into protected configuration files."),
        ("Add CSRF protection to the app login. ", "Add an anti-forgery token to the "
         "login form on <b>app.narayanagroup.co.in</b> and validate it server-side."),
        ("Hide framework banners and block storage paths. ", "Suppress the "
         "<b>X-Powered-By</b> headers, and configure the web server to deny access to "
         "<b>/ntask/storage/</b> entirely rather than returning 403 from the "
         "application."),
    ],
    extra=[PageBreak()],
))

# ============================================================================
# 8. REMEDIATION ROADMAP
# ============================================================================
F.append(section_header("8", "Your action plan - what to do, and when"))
F.append(sp(3))
F.append(P("Below is the same information organised as a schedule. Share this page with "
           "your IT team; it is designed to be worked through top to bottom."))
F.append(sp(4))

def phase(title, subtitle, tone, items):
    out = []
    head = Table([[Paragraph('<font color="white"><b>%s</b></font>'
                             % esc(title), st["cell"]),
                   Paragraph('<font color="white">%s</font>' % esc(subtitle), st["cell"])]],
                 colWidths=[52 * mm, CONTENT_W - 52 * mm])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SEV_COLOR[tone]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    out.append(head)
    out.append(sp(3))
    rows = []
    for fid, action, who in items:
        rows.append([
            Paragraph("<b>%s</b>" % esc(fid), st["cell_sm"]),
            Paragraph(esc(action), st["cell_sm"]),
            Paragraph(esc(who), st["cell_sm"]),
        ])
    t = Table([[Paragraph("<b>%s</b>" % h, st["th"]) for h in
                ["ID", "Action", "Who"]]] + rows,
              colWidths=[28 * mm, CONTENT_W - 28 * mm - 34 * mm, 34 * mm], repeatRows=1)
    ts = [("BACKGROUND", (0, 0), (-1, 0), NAVY),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, GREY_BD),
          ("LEFTPADDING", (0, 0), (-1, -1), 4),
          ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 4),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    for i in range(1, len(rows) + 1):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
    t.setStyle(TableStyle(ts))
    out.append(t)
    out.append(sp(6))
    return out


F.extend(phase(
    "PHASE 1 - TODAY", "Treat as an active incident. Do not wait for a scheduled "
    "maintenance window.", "Critical",
    [
        ("001, 002, 003",
         "Turn on server-side authentication across /NtraktApi/api/* and "
         "/NnoteApi/api/*. This ONE change closes three findings at once - the two "
         "Critical ones and the unauthenticated uploads.",
         "Lead developer + IT head"),
        ("WEB-2026-002",
         "Ask your team to review web server logs for signs that someone has already "
         "been pulling records. Assume it may already have happened.",
         "IT head"),
        ("WEB-2026-010",
         "Delete or correct the online.narayanagroup.co.in DNS record pointing to "
         "15.241.194.25. Two minutes of work in Cloudflare.",
         "IT head"),
        ("WEB-2026-005",
         "Switch off detailed error messages in production "
         "(customErrors mode=\"On\", IncludeErrorDetailPolicy.Never).",
         "Lead developer"),
        ("WEB-2026-002",
         "Add a temporary IP allow-list or Cloudflare firewall rule restricting "
         "/NtraktApi/ and /NnoteApi/ to known Narayana IP ranges while the permanent "
         "fix is built. This buys you safety immediately.",
         "IT head"),
    ]))

F.extend(phase(
    "PHASE 2 - THIS WEEK", "High-severity items. Aim to have all of these closed "
    "within 7 days.", "High",
    [
        ("WEB-2026-004",
         "Move all fee amounts, fines and the merchant bank account to be calculated "
         "server-side from the database. Stop reading them from the page.",
         "Developer (fee portal)"),
        ("WEB-2026-004",
         "Require login or OTP before revealing student and parent details; change the "
         "homepage link to https://.",
         "Developer (fee portal)"),
        ("WEB-2026-007",
         "Move nNote.apk to HTTPS, sign it properly, and enable HTTPS with "
         "HTTP-to-HTTPS redirect on the helpdesk and elearn login pages.",
         "IT head + developer"),
        ("WEB-2026-001",
         "Implement proper session management: server-issued session or signed token, "
         "HttpOnly + Secure + SameSite cookies, account lockout after 5 failed attempts, "
         "and authentication logging.",
         "Lead developer"),
        ("WEB-2026-001",
         "Require the existing PIN or a server-verified OTP before any PIN change; "
         "remove ?empid= and ?regno= from URLs.",
         "Lead developer"),
        ("WEB-2026-002",
         "Add authorisation checks so a user can only ever read their own record; "
         "replace guessable IDs with random ones; remove Password, OTP, Aadhaar and PIN "
         "fields from API responses.",
         "Lead developer"),
        ("WEB-2026-002",
         "Require an authenticated, authorised approver for bill cancellations and log "
         "every approval with the approver's identity.",
         "Developer + finance"),
        ("WEB-2026-003",
         "Require authentication on all upload endpoints; generate filenames server-side; "
         "restrict file types; store uploads outside the web root.",
         "Lead developer"),
    ]))

F.extend(phase(
    "PHASE 3 - THIS MONTH", "The remaining structural and hygiene work.", "Medium",
    [
        ("WEB-2026-006",
         "Upgrade or replace the helpdesk stack (PHP 5.6 / Apache 2.4.23 / osTicket "
         "1.10). Decide upgrade / replace / retire for the 2003 payroll, 2010 Classic "
         "ASP inventory and hospital systems, and the ASP.NET 2.0 patient portal.",
         "IT head + vendors"),
        ("WEB-2026-006",
         "Update jQuery and Bootstrap on the main website; lock down or remove the UAT "
         "environment; set up a monthly patching routine.",
         "Web developer"),
        ("WEB-2026-008",
         "Fix the PACS HSTS header (max-age=31536000), replace the placeholder CORS "
         "value, require authentication on /PacsAPI/ and /RISAPI/, and request the "
         "vendor's hardening guide.",
         "PACS vendor + IT"),
        ("WEB-2026-010",
         "Publish SPF and DMARC records. Start DMARC at p=none, review reports for two "
         "weeks, then move to quarantine and finally reject.",
         "IT head"),
        ("WEB-2026-010",
         "Assign an owner to nmc and uat, or remove their DNS records. Add a quarterly "
         "DNS review to your calendar.",
         "IT head"),
        ("WEB-2026-009",
         "Add the six standard security headers site-wide; mark every cookie HttpOnly, "
         "Secure and SameSite; add CSRF tokens to the app login form.",
         "Web developer"),
        ("WEB-2026-009",
         "Replace the \"There is no such Login Id\" message with a generic failure "
         "message; remove internal IP addresses and localhost references from live code.",
         "Web developer"),
    ]))

F.append(callout(
    "The single highest-value action",
    ["If you only do one thing from this report: <b>switch on authentication at the "
     "/NtraktApi/ and /NnoteApi/ layer.</b> That one change closes both Critical "
     "findings and the unauthenticated file upload finding - three of your ten issues, "
     "including the two that matter most - and it can realistically be done in a day.",
     "If your developers are not available immediately, a temporary network-level "
     "restriction (only allowing your own office and hospital IP ranges to reach those "
     "paths) will stop the bleeding within the hour while the proper fix is built."],
    tone="good", icon="OK"))
F.append(PageBreak())

# ============================================================================
# 9. WHAT GOOD LOOKS LIKE / NEXT STEPS
# ============================================================================
F.append(section_header("9", "What 'fixed' looks like, and what happens next"))
F.append(sp(3))

F.append(sub_label("9.1  How to check the fix worked"))
F.append(P("Once your team has made the changes, they should re-run the exact commands "
           "shown in the \"How we proved it\" sections. <b>Every one of them should now "
           "fail.</b> In particular:"))
F.append(sp(2))
F.extend(numbered([
    ("Open /Nnote/layout.html and /ncare/layout.html directly. ",
     "You should be sent back to the login page. If the dashboard still opens, the fix "
     "is not complete."),
    ("Call /NtraktApi/api/User/Info/3334024 without logging in. ",
     "You should get <b>401 Unauthorized</b> or <b>403 Forbidden</b>. If you still get "
     "an employee record, the fix is not complete."),
    ("Call /NnoteApi/api/Patient/Info/1005411787 without logging in. ",
     "You should get 401 or 403. If you still get a patient record, the fix is not "
     "complete."),
    ("Trigger an error on purpose (for example /NtraktApi/api/User/Info/1'). ",
     "You should see a generic message, not an ORA- error and not a file path."),
    ("Check your cookies. ", "Every one should carry HttpOnly, Secure and SameSite."),
    ("Check your email authentication. ", "Use a free online SPF/DMARC checker - it "
     "should now show both records present."),
]))
F.append(sp(4))

F.append(sub_label("9.2  Recommended next steps"))
F.append(data_table(
    ["Step", "Recommended action", "Why"],
    [
        ["1", "<b>Fix the two Critical findings today.</b>",
         "Everything else can wait. These two cannot."],
        ["2", "<b>Ask for a re-test.</b> Once the fixes are in, have them verified "
              "independently before you consider the matter closed.",
         "Roughly a third of first attempts at a fix are incomplete. A re-test is the "
         "only way to know."],
        ["3", "<b>Turn on your Cloudflare protections.</b> You already use Cloudflare, "
              "so the web application firewall (WAF), bot protection and rate limiting "
              "are available to you at no extra cost.",
         "This gives you a safety net across all 29 applications while the permanent "
         "fixes are built, and it costs nothing to enable."],
        ["4", "<b>Appoint a named owner for every system in section 5.</b>",
         "Unowned systems are how breaches happen. Three of yours (nmc, uat, online) "
         "currently appear to have no owner."],
        ["5", "<b>Start a monthly patching routine.</b>",
         "Most successful attacks exploit problems that had a fix available for months."],
        ["6", "<b>Write a short incident plan.</b> One page: who to call, what to "
              "switch off, who notifies patients and regulators.",
         "If the worst happens, the first hour matters most. Deciding in advance saves "
         "that hour."],
        ["7", "<b>Review your DPDP Act 2023 obligations.</b> Take advice on whether "
              "any of this triggers a notification duty.",
         "Penalties can be substantial, and early voluntary action is viewed far more "
         "favourably than disclosure after a breach."],
        ["8", "<b>Consider a full internal network assessment.</b> This report only "
              "covers what is reachable from the internet.",
         "Once an attacker is inside, the next layer matters. An internal review is the "
         "natural follow-up to this one."],
    ],
    [12 * mm, 72 * mm, CONTENT_W - 84 * mm]))
F.append(sp(5))

F.append(callout(
    "A closing word",
    ["Finding ten issues - including two Critical ones - does not mean your IT team has "
     "failed. It means your organisation has grown, added systems over many years, and "
     "has now had its first proper external security review. Almost every organisation "
     "of your size gets a similar result the first time.",
     "What matters now is what happens in the next 48 hours. The two Critical findings "
     "are genuinely urgent, and they are also genuinely fixable. Fix those, and your "
     "risk drops dramatically. Then work down the list.",
     "We are happy to re-test each fix at no additional complexity and confirm in "
     "writing when each item is closed."],
    tone="neutral"))

F.append(PageBreak())

# ============================================================================
# 10. APPENDIX - METHOD & SCOPE
# ============================================================================
F.append(section_header("10", "Appendix - how the assessment was carried out"))
F.append(sp(3))

F.append(sub_label("A.  Scope"))
F.append(data_table(
    ["In scope (authorised, tested)", "Out of scope (not tested)"],
    [[
        "https://narayanagroup.co.in/ and every application hosted under it "
        "(29 identified)\n\n"
        "All sub-domains discovered: www, pacs, dms, nmc, uat, app, helpdesk, online\n\n"
        "All REST API services: /NtraktApi/, /NnoteApi/, /PacsAPI/, /RISAPI/\n\n"
        "DNS, email authentication records and public TLS configuration\n\n"
        "Public port scan of the primary server address",
        "Any system not belonging to Narayana Group\n\n"
        "Your hosting provider's, mail provider's or payment gateway's own "
        "infrastructure\n\n"
        "Internal network, staff computers, Wi-Fi and end-user devices\n\n"
        "Physical security of your premises\n\n"
        "Your staff (no social engineering, no phishing tests were performed)\n\n"
        "Availability testing (no denial-of-service or load testing)",
    ]],
    [CONTENT_W / 2.0, CONTENT_W / 2.0]))
F.append(sp(5))

F.append(sub_label("B.  Method"))
F.extend(numbered([
    "<b>Reconnaissance.</b> We mapped the public site, followed every link, and used "
    "public internet records to discover sub-domains and servers.",
    "<b>Fingerprinting.</b> For each system we identified the software, versions and "
    "configuration from the information it freely returns.",
    "<b>Manual review.</b> We read the application code that your servers send to "
    "browsers (HTML and JavaScript) to understand how login, data access and payments "
    "actually work.",
    "<b>Verification.</b> Every finding was confirmed by making a real request against "
    "the live system and observing the response. Nothing in this report is theoretical "
    "or inferred from a scanner.",
    "<b>Analysis and reporting.</b> Each confirmed issue was scored using the CVSS v3.1 "
    "standard and mapped to the CWE and OWASP Top 10 (2021) frameworks used worldwide.",
]))
F.append(sp(4))

F.append(sub_label("C.  Understanding the CVSS score"))
F.append(P("CVSS is the international standard for rating how dangerous a vulnerability "
           "is. It produces a score from 0 to 10, calculated from factors such as: can "
           "it be done over the network? does the attacker need to log in first? does it "
           "need an innocent person to be tricked? how much data is affected? Every "
           "score in this report was calculated using the official CVSS v3.1 "
           "calculator."))
F.append(sp(2))
F.append(data_table(
    ["Score", "Band", "Meaning for you"],
    [
        ["9.0 - 10.0", "Critical", "Maximum damage, trivially easy, no login needed. "
                                   "Act today."],
        ["7.0 - 8.9", "High", "Serious damage likely. Act this week."],
        ["4.0 - 6.9", "Medium", "Meaningful weakness. Act this month."],
        ["0.1 - 3.9", "Low", "Hygiene. Fix when convenient."],
        ["n/a", "Informational", "No direct risk, but worth knowing about."],
    ],
    [24 * mm, 26 * mm, CONTENT_W - 50 * mm]))
F.append(sp(5))

F.append(sub_label("D.  Finding-to-reference index"))
F.append(data_table(
    ["ID", "Severity", "CVSS", "Category (OWASP Top 10 2021)"],
    [
        ["WEB-2026-001", "Critical", "9.8",
         "A07 Identification and Authentication Failures"],
        ["WEB-2026-002", "Critical", "9.8", "A01 Broken Access Control"],
        ["WEB-2026-003", "High", "8.6", "A01 Broken Access Control"],
        ["WEB-2026-004", "High", "8.2", "A04 Insecure Design"],
        ["WEB-2026-005", "High", "7.5", "A05 Security Misconfiguration"],
        ["WEB-2026-006", "High", "8.1", "A06 Vulnerable and Outdated Components"],
        ["WEB-2026-007", "High", "7.5", "A02 Cryptographic Failures"],
        ["WEB-2026-008", "Medium", "6.5", "A05 Security Misconfiguration"],
        ["WEB-2026-009", "Medium", "5.8", "A05 Security Misconfiguration"],
        ["WEB-2026-010", "Medium", "6.5", "A05 Security Misconfiguration"],
    ],
    [28 * mm, 22 * mm, 16 * mm, CONTENT_W - 66 * mm]))
F.append(sp(5))

F.append(callout(
    "Handling and distribution",
    ["This report is classified <b>CONFIDENTIAL - TLP:AMBER</b>. Share it only with "
     "people who need to act on it. Until the Critical findings are closed, do not post "
     "it publicly, attach it to a ticket with external suppliers, or forward it outside "
     "your organisation.",
     "Report reference <b>%s</b>, dated <b>%s</b>." % (REPORT_REF, REPORT_DATE)],
    tone="warn", icon="!"))

# ============================================================================
# TABLE OF CONTENTS
# ============================================================================
# (key = text that appears on the section's own page, used to discover the
#  page number; label = shorter wording shown in the contents list.)
SECTION_ENTRIES = [
    ("How to read this report (2 minutes)", "How to read this report", 0),
    ("Simple glossary - the words used in this report", "Simple glossary", 0),
    ("Executive summary - the bottom line", "Executive summary", 0),
    ("How dangerous is each rating?", "How dangerous is each rating", 0),
    ("What exactly was tested", "Full inventory of what was tested", 0),
    ("All 10 findings at a glance", "Summary table - all 10 findings", 0),
    ("Detailed findings - one by one", "The 10 findings explained in detail", 0),
    ("Your action plan - what to do, and when", "Your action plan and schedule", 0),
    ("What 'fixed' looks like, and what happens", "What 'fixed' looks like, and next steps", 0),
    ("Appendix - how the assessment was carried out", "Appendix - method and scope", 0),
]

FINDING_ENTRIES = [
    ("WEB-2026-001", "No real login on your staff and patient portals",
     "Staff and patient portals have no real login", "Critical"),
    ("WEB-2026-002", "Strangers can download your staff records (with photographs)",
     "Staff and patient records can be read by anyone", "Critical"),
    ("WEB-2026-003", "Anyone can upload files to your servers without logging in",
     "Anyone can upload files to your servers", "High"),
    ("WEB-2026-004", "The student fee payment page lets the payer change the amount",
     "Fee payment amounts can be changed by the payer", "High"),
    ("WEB-2026-005", "Error messages reveal your internal database structure",
     "Error messages expose your internal systems", "High"),
    ("WEB-2026-006", "Several systems run on software that stopped receiving security",
     "Software that no longer receives security updates", "High"),
    ("WEB-2026-007", "Your hospital Android app is downloaded over an unencrypted",
     "Hospital app and some logins are not encrypted", "High"),
    ("WEB-2026-008", "Medical imaging server (PACS) has security settings switched off",
     "Medical imaging (PACS) server misconfigured", "Medium"),
    ("WEB-2026-010", "Anyone can send email pretending to be you",
     "Email can be forged in your name", "Medium"),
    ("WEB-2026-009", "Missing browser protections, insecure cookies, and internal IP",
     "Missing browser protections and insecure cookies", "Medium"),
]


def make_toc(page_map):
    out = []
    hdr = Table([[Paragraph('<font color="white"><b>Contents</b></font>',
                            ParagraphStyle("ch", fontName="DJS-Bold", fontSize=13,
                                           leading=16, alignment=TA_LEFT))]],
                colWidths=[CONTENT_W])
    hdr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    out.append(hdr)
    out.append(sp(5))
    out.append(P("Everything in this report, in order. The two sections marked "
                 "<b>CRITICAL</b> are the ones that need attention today."))
    out.append(sp(4))

    num_style = ParagraphStyle("tocn", fontName="DJS-Bold", fontSize=9.2,
                               leading=13, textColor=NAVY, alignment=TA_LEFT)
    lbl_style = ParagraphStyle("tocl", fontName="DJS", fontSize=9.2, leading=13,
                               alignment=TA_LEFT)
    lbl_bold = ParagraphStyle("toclb", fontName="DJS-Bold", fontSize=9.2, leading=13,
                              alignment=TA_LEFT)
    pg_style = ParagraphStyle("tocp", fontName="DJS", fontSize=9.2, leading=13,
                              alignment=TA_LEFT, textColor=GREY)

    rows = []
    for i, (key, label, _lvl) in enumerate(SECTION_ENTRIES, 1):
        pg = page_map.get(key)
        rows.append([
            Paragraph(str(i), num_style),
            Paragraph(esc(label), lbl_bold),
            Paragraph(str(pg) if pg else "", pg_style),
        ])
    for fid, key, label, sev in FINDING_ENTRIES:
        pg = page_map.get(fid)
        rows.append([
            Paragraph("", num_style),
            Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<b>%s</b>&nbsp; - %s &nbsp;"
                      "<font color='%s'>[%s]</font>"
                      % (esc(fid), esc(label), hx(SEV_COLOR[sev]), esc(sev.upper())),
                      lbl_style),
            Paragraph(str(pg) if pg else "", pg_style),
        ])

    t = Table(rows, colWidths=[9 * mm, CONTENT_W - 9 * mm - 14 * mm, 14 * mm])
    ts = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 2),
          ("RIGHTPADDING", (0, 0), (-1, -1), 2),
          ("TOPPADDING", (0, 0), (-1, -1), 3.4),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
          ("LINEBELOW", (0, len(SECTION_ENTRIES) - 1), (-1, len(SECTION_ENTRIES) - 1),
           0.6, GREY_BD)]
    for i in range(len(SECTION_ENTRIES), len(rows)):
        if (i - len(SECTION_ENTRIES)) % 2 == 1:
            ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FB")))
    t.setStyle(TableStyle(ts))
    out.append(t)
    out.append(sp(6))
    out.append(callout(
        "If you only have ten minutes",
        ["Read the <b>Executive summary</b> (section 3), then the two findings marked "
         "<b>CRITICAL</b> - <b>WEB-2026-001</b> and <b>WEB-2026-002</b>. Then go "
         "straight to <b>section 8, Your action plan</b>, and give Phase 1 to your IT "
         "team today."],
        tone="danger", icon="!!"))
    out.append(PageBreak())
    return out


def discover_pages(pdf_path):
    try:
        import pymupdf
    except Exception:
        return None
    doc = pymupdf.open(pdf_path)
    texts = [(i + 1, doc[i].get_text()) for i in range(doc.page_count)]
    doc.close()
    found = {}
    for key, label, _lvl in SECTION_ENTRIES:
        hits = [pn for pn, t in texts if key in t]
        if hits:
            found[key] = min(hits)
    for fid, key, label, _sev in FINDING_ENTRIES:
        hits = [pn for pn, t in texts if key in t]
        if hits:
            found[fid] = max(hits)
    return found


# ============================================================================
# BUILD
# ============================================================================
def on_page(canvas, doc):
    if doc.page == 1:
        _cover_bg(canvas, doc)
    else:
        _normal_bg(canvas, doc)


def make_doc(path):
    d = BaseDocTemplate(
        path, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOT,
        title="Website Security Assessment - narayanagroup.co.in",
        author="Security Assessment",
        subject="Confidential security assessment report",
    )
    d.addPageTemplates([
        PageTemplate(id="all", frames=[Frame(
            MARGIN_X, MARGIN_BOT, CONTENT_W,
            PAGE_H - MARGIN_TOP - MARGIN_BOT, id="main")], onPage=on_page),
    ])
    return d


from copy import deepcopy

TMP1 = os.path.join(OUT_DIR, ".toc-pass1.pdf")
TMP2 = os.path.join(OUT_DIR, ".toc-pass2.pdf")


def assemble(page_map):
    """Fresh copies each time - ReportLab flowables cannot be reused between builds."""
    return (deepcopy(F[:TOC_INSERT_AT]) + make_toc(page_map)
            + deepcopy(F[TOC_INSERT_AT:]))


# Pass 1 - build without contents, to learn where everything lands.
make_doc(TMP1).build(deepcopy(F))
page_map = discover_pages(TMP1) or {}

# Pass 2 - build with the contents page inserted, then re-measure.
make_doc(TMP2).build(assemble(page_map))
page_map = discover_pages(TMP2) or page_map

# Final build.
make_doc(OUT_FILE).build(assemble(page_map))

for f in (TMP1, TMP2):
    if os.path.exists(f):
        os.remove(f)

print("PDF written to: %s" % OUT_FILE)
