from django.core.management.base import BaseCommand
from django.db import transaction
from user.client.models import Client
from user.satellite.models import Satellite


class Command(BaseCommand):
    help = 'Sync satellite account data to client accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force overwrite existing client data',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('Starting satellite to client data sync...')
        )
        
        # Find satellites that don't have complete client data
        satellites_to_sync = []
        
        for satellite in Satellite.objects.all():
            # Check if satellite has a client
            if hasattr(satellite, 'satellite_client') and satellite.satellite_client:
                client = satellite.satellite_client
                
                # Check if client is missing key data that exists in satellite
                needs_sync = False
                
                if satellite.name and (not client.name or force):
                    needs_sync = True
                if satellite.last_name and (not client.last_name or force):
                    needs_sync = True
                if satellite.email and (not client.email or force):
                    needs_sync = True
                if satellite.phone and (not client.phone or force):
                    needs_sync = True
                if satellite.country and (not client.country or force):
                    needs_sync = True
                if satellite.city and (not client.city or force):
                    needs_sync = True
                if satellite.address and (not client.address or force):
                    needs_sync = True
                if satellite.born and (not client.born or force):
                    needs_sync = True
                    
                if needs_sync:
                    satellites_to_sync.append((satellite, client))
            else:
                # Satellite doesn't have a client - this might need manual investigation
                self.stdout.write(
                    self.style.WARNING(f'Satellite {satellite.username} has no associated client')
                )
        
        if not satellites_to_sync:
            self.stdout.write(
                self.style.SUCCESS('No satellites need syncing. All client data is complete!')
            )
            return
        
        self.stdout.write(f'Found {len(satellites_to_sync)} satellites that need syncing')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))
            for satellite, client in satellites_to_sync:
                self.stdout.write(f'\nWould sync satellite {satellite.username} -> client {client.username}:')
                self._show_sync_plan(satellite, client, force)
            return
        
        # Perform the actual sync
        synced_count = 0
        with transaction.atomic():
            for satellite, client in satellites_to_sync:
                try:
                    self._sync_satellite_to_client(satellite, client, force)
                    synced_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Synced {satellite.username} -> {client.username}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'✗ Failed to sync {satellite.username}: {e}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully synced {synced_count} satellite accounts to clients')
        )
    
    def _show_sync_plan(self, satellite, client, force):
        """Show what would be synced"""
        changes = []
        
        if satellite.name and (not client.name or force):
            changes.append(f'  name: "{client.name}" -> "{satellite.name}"')
        if satellite.last_name and (not client.last_name or force):
            changes.append(f'  last_name: "{client.last_name}" -> "{satellite.last_name}"')
        if satellite.email and (not client.email or force):
            changes.append(f'  email: "{client.email}" -> "{satellite.email}"')
        if satellite.phone and (not client.phone or force):
            changes.append(f'  phone: "{client.phone}" -> "{satellite.phone}"')
        if satellite.country and (not client.country or force):
            changes.append(f'  country: "{client.country}" -> "{satellite.country}"')
        if satellite.city and (not client.city or force):
            changes.append(f'  city: "{client.city}" -> "{satellite.city}"')
        if satellite.address and (not client.address or force):
            changes.append(f'  address: "{client.address}" -> "{satellite.address}"')
        if satellite.born and (not client.born or force):
            changes.append(f'  born: "{client.born}" -> "{satellite.born}"')
            
        for change in changes:
            self.stdout.write(change)
    
    def _sync_satellite_to_client(self, satellite, client, force):
        """Sync satellite data to client"""
        updated = False
        
        if satellite.name and (not client.name or force):
            client.name = satellite.name
            updated = True
        if satellite.last_name and (not client.last_name or force):
            client.last_name = satellite.last_name
            updated = True
        if satellite.email and (not client.email or force):
            client.email = satellite.email
            updated = True
        if satellite.phone and (not client.phone or force):
            client.phone = satellite.phone
            updated = True
        if satellite.country and (not client.country or force):
            client.country = satellite.country
            updated = True
        if satellite.city and (not client.city or force):
            client.city = satellite.city
            updated = True
        if satellite.address and (not client.address or force):
            client.address = satellite.address
            updated = True
        if satellite.born and (not client.born or force):
            client.born = satellite.born
            updated = True
            
        # Also sync verification status if needed
        if satellite.email_verified and (not client.email_verified or force):
            client.email_verified = satellite.email_verified
            updated = True
        if satellite.document_verified and (not client.document_verified or force):
            client.document_verified = satellite.document_verified
            client.document_verified_at = satellite.document_verified_at
            updated = True
            
        if updated:
            client.save()