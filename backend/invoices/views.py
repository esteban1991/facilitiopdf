import base64
import os

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invoice, SenderProfile
from .serializers import InvoiceListSerializer, InvoiceSerializer, SenderProfileSerializer


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

    @action(detail=True, methods=["post"], parser_classes=[MultiPartParser, FormParser])
    def upload_logo(self, request, pk=None):
        invoice = self.get_object()
        logo_file = request.FILES.get("logo")
        if not logo_file:
            return Response(
                {"error": "No logo file provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        invoice.sender_logo = logo_file
        invoice.save()
        serializer = InvoiceSerializer(invoice, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def pdf(self, request, pk=None):
        invoice = self.get_object()

        logo_data = None
        if invoice.sender_logo:
            logo_path = invoice.sender_logo.path
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_bytes = f.read()
                ext = os.path.splitext(logo_path)[1].lower().lstrip(".")
                if ext == "jpg":
                    ext = "jpeg"
                logo_b64 = base64.b64encode(logo_bytes).decode("utf-8")
                logo_data = f"data:image/{ext};base64,{logo_b64}"

        html_string = render_to_string(
            "invoices/invoice_pdf.html",
            {"invoice": invoice, "logo_data": logo_data},
        )

        try:
            import weasyprint

            pdf_bytes = weasyprint.HTML(string=html_string).write_pdf()
        except Exception as e:
            return Response(
                {"error": f"PDF generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
        )
        return response
