from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0054_satellite_deposit_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='satellite',
            name='migration_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Migration date (unblock)'),
        ),
        migrations.AlterField(
            model_name='satellite',
            name='second_migration_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Migration date (withdrawal)'),
        ),
    ]
