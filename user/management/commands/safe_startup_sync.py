from django.core.management.base import BaseCommand
from user.startup_sync import run_startup_sync, force_reset_sync_status, sync_client_to_satellites, perform_startup_sync


class Command(BaseCommand):
    help = 'Manually run or manage the safe startup sync'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset sync status and force sync to run again',
        )
        parser.add_argument(
            '--force',
            action='store_true', 
            help='Force sync to run even if already completed',
        )
        parser.add_argument(
            '--client-to-satellites',
            action='store_true',
            help='Sync client verification status to all satellites',
        )
        parser.add_argument(
            '--satellite-to-client',
            action='store_true',
            help='Sync satellite data to clients',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting sync status...')
            force_reset_sync_status()
            self.stdout.write(
                self.style.SUCCESS('Sync status reset successfully')
            )
        
        # Handle specific sync directions
        if options['client_to_satellites']:
            self.stdout.write('Syncing client verification status to satellites...')
            sync_client_to_satellites()
            self.stdout.write(
                self.style.SUCCESS('Client-to-satellites sync completed')
            )
        elif options['satellite_to_client']:
            self.stdout.write('Syncing satellite data to clients...')
            perform_startup_sync()
            self.stdout.write(
                self.style.SUCCESS('Satellite-to-client sync completed')
            )
        elif options['force'] or options['reset']:
            self.stdout.write('Running forced startup sync...')
            run_startup_sync()
        else:
            self.stdout.write('Running startup sync...')
            run_startup_sync()
            
        self.stdout.write(
            self.style.SUCCESS('Startup sync command completed')
        )