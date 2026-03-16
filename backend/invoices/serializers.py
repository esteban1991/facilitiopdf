from rest_framework import serializers
from .models import Invoice, LineItem, SenderProfile


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LineItem
        fields = ["id", "description", "hours", "rate", "amount", "order"]


class SenderProfileSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SenderProfile
        fields = [
            "id",
            "name",
            "address",
            "logo",
            "logo_url",
            "default_currency",
            "default_terms",
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url  # relative path, e.g. /media/logos/xxx.png
        return None


class InvoiceListSerializer(serializers.ModelSerializer):
    total = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "client_name",
            "invoice_date",
            "currency",
            "total",
            "created_at",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    items = LineItemSerializer(many=True)
    total = serializers.ReadOnlyField()
    sender_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "sender_name",
            "sender_address",
            "sender_logo",
            "sender_logo_url",
            "client_name",
            "client_phone",
            "client_email",
            "client_address",
            "invoice_number",
            "invoice_date",
            "currency",
            "terms",
            "items",
            "total",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_sender_logo_url(self, obj):
        if obj.sender_logo:
            return obj.sender_logo.url  # relative path, e.g. /media/logos/xxx.png
        return None

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)
        for i, item_data in enumerate(items_data):
            item_data["order"] = i
            LineItem.objects.create(invoice=invoice, **item_data)
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.items.all().delete()
        for i, item_data in enumerate(items_data):
            item_data["order"] = i
            LineItem.objects.create(invoice=instance, **item_data)

        return instance
