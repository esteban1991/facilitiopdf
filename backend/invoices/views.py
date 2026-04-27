import os
from io import BytesIO

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Client, Invoice, LineItem, SenderProfile
from .serializers import ClientSerializer, InvoiceListSerializer, InvoiceSerializer, SenderProfileSerializer


# ── PDF helpers ───────────────────────────────────────────────────────────────

def _build_invoice_pdf(invoice):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable, Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    buffer = BytesIO()
    page_w, _ = A4
    margin = 18 * mm
    content_w = page_w - 2 * margin

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
    )

    # ── Colors ──
    C_DARK   = colors.HexColor("#111111")
    C_GRAY   = colors.HexColor("#777777")
    C_MID    = colors.HexColor("#555555")
    C_LIGHT  = colors.HexColor("#f5f5f5")
    C_BORDER = colors.HexColor("#dddddd")
    C_ACCENT = colors.HexColor("#888888")

    def S(name, **kw):
        d = dict(fontName="Helvetica", fontSize=11, textColor=C_DARK, leading=15)
        d.update(kw)
        return ParagraphStyle(name, **d)

    styles = {
        "sender_name" : S("sn",  fontSize=20, fontName="Helvetica-Bold", leading=24),
        "sender_addr" : S("sa",  fontSize=9,  textColor=C_GRAY, leading=14),
        "inv_title"   : S("it",  fontSize=20, fontName="Helvetica-Bold", alignment=TA_RIGHT),
        "sect_label"  : S("sl",  fontSize=8,  fontName="Helvetica-Bold", textColor=C_ACCENT, leading=10),
        "client_name" : S("cn",  fontSize=13, fontName="Helvetica-Bold", leading=17),
        "client_det"  : S("cd",  fontSize=10, textColor=C_MID, leading=16),
        "meta_lbl"    : S("ml",  fontSize=11, fontName="Helvetica-Bold", textColor=C_MID),
        "meta_val"    : S("mv",  fontSize=11, textColor=C_DARK, alignment=TA_RIGHT),
        "th"          : S("th",  fontSize=8,  fontName="Helvetica-Bold", textColor=C_ACCENT, leading=10),
        "th_r"        : S("thr", fontSize=8,  fontName="Helvetica-Bold", textColor=C_ACCENT, leading=10, alignment=TA_RIGHT),
        "td"          : S("td",  fontSize=10, textColor=colors.HexColor("#333333"), leading=15),
        "td_r"        : S("tdr", fontSize=10, textColor=C_DARK, leading=15, alignment=TA_RIGHT),
        "total_lbl"   : S("tl",  fontSize=11, fontName="Helvetica-Bold", textColor=C_DARK, alignment=TA_RIGHT),
        "total_val"   : S("tv",  fontSize=12, fontName="Helvetica-Bold", textColor=C_DARK, alignment=TA_RIGHT),
        "terms_lbl"   : S("terml", fontSize=8, fontName="Helvetica-Bold", textColor=C_ACCENT, leading=10),
        "terms_txt"   : S("termt", fontSize=10, textColor=C_MID, leading=15),
    }

    def vstack(items, width, align="LEFT"):
        t = Table([[i] for i in items], colWidths=[width])
        t.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("ALIGN",         (0, 0), (-1, -1), align),
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ]))
        return t

    story = []
    left_w  = content_w * 0.55
    right_w = content_w * 0.45
    pad     = 4 * mm

    # ── HEADER ──────────────────────────────────────────────────────────────
    left_items = [
        Paragraph(invoice.sender_name or "", styles["sender_name"]),
        Spacer(1, 2 * mm),
        Paragraph((invoice.sender_address or "").replace("\n", "<br/>"), styles["sender_addr"]),
    ]

    right_items = [Paragraph("INVOICE", styles["inv_title"])]

    # Use invoice logo, fall back to profile logo
    logo_path = None
    if invoice.sender_logo and os.path.exists(invoice.sender_logo.path):
        logo_path = invoice.sender_logo.path
    else:
        profile = SenderProfile.get()
        if profile.logo and os.path.exists(profile.logo.path):
            logo_path = profile.logo.path

    if logo_path:
        ext = os.path.splitext(logo_path)[1].lower()
        try:
            if ext == ".svg":
                from svglib.svglib import svg2rlg
                from reportlab.graphics import renderPDF  # noqa – ensures backend loaded
                drawing = svg2rlg(logo_path)
                if drawing:
                    # Scale drawing to fit 26mm × 19mm preserving aspect ratio
                    target_w = 26 * mm
                    scale = target_w / drawing.width
                    drawing.width  = target_w
                    drawing.height = drawing.height * scale
                    drawing.transform = (scale, 0, 0, scale, 0, 0)
                    drawing.hAlign = "RIGHT"
                    right_items += [Spacer(1, 2 * mm), drawing]
            elif ext in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
                img = RLImage(logo_path, width=26 * mm, height=19 * mm, kind="proportional")
                img.hAlign = "RIGHT"
                right_items += [Spacer(1, 2 * mm), img]
        except Exception:
            pass

    header = Table(
        [[vstack(left_items, left_w), vstack(right_items, right_w, align="RIGHT")]],
        colWidths=[left_w, right_w],
    )
    header.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6 * mm),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW",     (0, 0), (-1, 0),  1.5, colors.HexColor("#e8e8e8")),
    ]))
    story += [header, Spacer(1, 10 * mm)]

    # ── BILLING + META ───────────────────────────────────────────────────────
    bill_items = [
        Paragraph("BILL TO", styles["sect_label"]),
        Spacer(1, 2 * mm),
        Paragraph(invoice.client_name or "", styles["client_name"]),
        Spacer(1, 1 * mm),
    ]
    detail_lines = []
    if invoice.client_phone:
        detail_lines.append(f"TELF: {invoice.client_phone}")
    if invoice.client_email:
        detail_lines.append(f"EMAIL: {invoice.client_email}")
    if invoice.client_address:
        detail_lines.append(invoice.client_address.replace("\n", "<br/>"))
    if detail_lines:
        bill_items.append(Paragraph("<br/>".join(detail_lines), styles["client_det"]))

    meta_items = [
        Paragraph("Invoice #",    styles["meta_lbl"]),
        Paragraph(str(invoice.invoice_number), styles["meta_val"]),
        Spacer(1, 2 * mm),
        Paragraph("Invoice Date", styles["meta_lbl"]),
        Paragraph(str(invoice.invoice_date), styles["meta_val"]),
    ]

    billing = Table(
        [[vstack(bill_items, left_w), vstack(meta_items, right_w, align="RIGHT")]],
        colWidths=[left_w, right_w],
    )
    billing.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story += [billing, Spacer(1, 10 * mm)]

    # ── ITEMS TABLE ──────────────────────────────────────────────────────────
    col_w  = 30 * mm          # wider so amounts never wrap
    desc_w = content_w - 3 * col_w

    rows = [[
        Paragraph("DESCRIPTION", styles["th"]),
        Paragraph("HOURS",       styles["th_r"]),
        Paragraph("RATE",        styles["th_r"]),
        Paragraph("AMOUNT",      styles["th_r"]),
    ]]

    for item in invoice.items.all():
        hours  = str(item.hours)  if item.hours  is not None else "—"
        rate   = f"{invoice.currency}{item.rate:.2f}" if item.rate is not None else "—"
        amount = f"{item.amount:.2f}"
        rows.append([
            Paragraph(str(item.description or ""), styles["td"]),
            Paragraph(hours,  styles["td_r"]),
            Paragraph(rate,   styles["td_r"]),
            Paragraph(amount, styles["td_r"]),
        ])

    # Total row — cols 0-2 merged so "TOTAL" label has full room
    rows.append([
        Paragraph("TOTAL", styles["total_lbl"]),
        "",
        "",
        Paragraph(f"{invoice.currency}{invoice.total:.2f}", styles["total_val"]),
    ])

    items_table = Table(rows, colWidths=[desc_w, col_w, col_w, col_w], repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",    (0, 0),  (-1, 0),  C_LIGHT),
        ("ALIGN",         (1, 0),  (-1, 0),  "RIGHT"),
        ("TOPPADDING",    (0, 0),  (-1, 0),  3.5 * mm),
        ("BOTTOMPADDING", (0, 0),  (-1, 0),  3.5 * mm),
        ("LEFTPADDING",   (0, 0),  (-1, 0),  pad),
        ("RIGHTPADDING",  (0, 0),  (-1, 0),  pad),
        # Body
        ("ALIGN",         (1, 1),  (-1, -2), "RIGHT"),
        ("VALIGN",        (0, 0),  (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 1),  (-1, -2), 4.5 * mm),
        ("BOTTOMPADDING", (0, 1),  (-1, -2), 4.5 * mm),
        ("LEFTPADDING",   (0, 1),  (-1, -2), pad),
        ("RIGHTPADDING",  (0, 1),  (-1, -2), pad),
        # Total row — merge first 3 cols, style last col
        ("SPAN",          (0, -1), (2, -1)),
        ("BACKGROUND",    (0, -1), (-1, -1), C_LIGHT),
        ("ALIGN",         (0, -1), (2, -1),  "RIGHT"),
        ("ALIGN",         (3, -1), (3, -1),  "RIGHT"),
        ("TOPPADDING",    (0, -1), (-1, -1), 4 * mm),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 4 * mm),
        ("LEFTPADDING",   (0, -1), (-1, -1), pad),
        ("RIGHTPADDING",  (0, -1), (-1, -1), pad),
        # Grid
        ("GRID",          (0, 0),  (-1, -1), 0.5, C_BORDER),
    ]))
    story.append(items_table)

    # ── TERMS ────────────────────────────────────────────────────────────────
    if invoice.terms:
        story += [
            Spacer(1, 10 * mm),
            HRFlowable(width=content_w, thickness=0.5, color=colors.HexColor("#e8e8e8")),
            Spacer(1, 5 * mm),
            Paragraph("TERMS & CONDITIONS", styles["terms_lbl"]),
            Spacer(1, 2 * mm),
            Paragraph(invoice.terms.replace("\n", "<br/>"), styles["terms_txt"]),
        ]

    doc.build(story)
    return buffer.getvalue()


# ── Views ─────────────────────────────────────────────────────────────────────

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class SenderProfileView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile = SenderProfile.get()
        serializer = SenderProfileSerializer(profile, context={"request": request})
        return Response(serializer.data)

    def patch(self, request):
        profile = SenderProfile.get()
        serializer = SenderProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return InvoiceListSerializer
        return InvoiceSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    @action(detail=False, methods=["get"])
    def next_number(self, request):
        last = Invoice.objects.order_by("-invoice_number").first()
        next_num = (last.invoice_number + 1) if last else 1
        return Response({"next_number": next_num})

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        last = Invoice.objects.order_by("-invoice_number").first()
        next_num = (last.invoice_number + 1) if last else 1

        new_invoice = Invoice.objects.create(
            sender_name=original.sender_name,
            sender_address=original.sender_address,
            sender_logo=original.sender_logo,
            client_name=original.client_name,
            client_phone=original.client_phone,
            client_email=original.client_email,
            client_address=original.client_address,
            invoice_number=next_num,
            invoice_date=original.invoice_date,
            currency=original.currency,
            terms=original.terms,
        )
        for item in original.items.all():
            LineItem.objects.create(
                invoice=new_invoice,
                description=item.description,
                hours=item.hours,
                rate=item.rate,
                amount=item.amount,
                order=item.order,
            )
        serializer = InvoiceSerializer(new_invoice, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_logo(self, request, pk=None):
        invoice = self.get_object()
        logo_file = request.FILES.get("logo")
        if not logo_file:
            return Response({"error": "No logo file provided."}, status=status.HTTP_400_BAD_REQUEST)
        invoice.sender_logo = logo_file
        invoice.save()
        serializer = InvoiceSerializer(invoice, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        invoice = self.get_object()
        try:
            pdf_bytes = _build_invoice_pdf(invoice)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"PDF generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
        )
        return response
