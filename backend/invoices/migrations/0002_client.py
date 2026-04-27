from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoices", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("phone", models.CharField(blank=True, default="", max_length=50)),
                ("email", models.EmailField(blank=True, default="")),
                ("address", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
