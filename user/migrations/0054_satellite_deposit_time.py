from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0053_alter_requisites_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='satellite',
            name='deposit_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deposit date'),
        ),
    ]
