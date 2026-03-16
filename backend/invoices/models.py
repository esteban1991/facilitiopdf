from django.db import models


class SenderProfile(models.Model):
    """Singleton – stores the freelancer's default sender info."""

    name = models.CharField(max_length=200, default="")
    address = models.TextField(default="")
    logo = models.ImageField(upload_to="logos/", null=True, blank=True)
    default_currency = models.CharField(max_length=5, default="$")
    default_terms = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Sender Profile"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Profile: {self.name}"


class Invoice(models.Model):
    # Sender snapshot (filled from profile at creation, editable per-invoice)
    sender_name = models.CharField(max_length=200, default="")
    sender_address = models.TextField(default="")
    sender_logo = models.ImageField(upload_to="logos/", null=True, blank=True)

    # Client
    client_name = models.CharField(max_length=200, default="")
    client_phone = models.CharField(max_length=50, blank=True, default="")
    client_email = models.EmailField(blank=True, default="")
    client_address = models.TextField(blank=True, default="")

    # Invoice meta
    invoice_number = models.IntegerField(default=1)
    invoice_date = models.DateField()
    currency = models.CharField(max_length=5, default="$")

    # Terms & conditions
    terms = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-invoice_number"]

    def __str__(self):
        return f"Invoice #{self.invoice_number} – {self.client_name}"

    @property
    def total(self):
        return sum(item.amount for item in self.items.all())


class LineItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="items"
    )
    description = models.TextField(default="")
    hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Item #{self.order} – Invoice #{self.invoice.invoice_number}"
