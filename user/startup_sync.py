"""
Safe startup data synchronization between Satellite and Client models
This module ensures data integrity when the application starts
"""
import logging
import time
from .logging_config import setup_sync_logging
from django.db import transaction, connection
from django.core.cache import cache
from django.conf import settings
from user.client.models import Client
from user.satellite.models import Satellite

logger = setup_sync_logging()

# Cache key for tracking sync status
SYNC_CACHE_KEY = "satellite_client_sync_completed"
SYNC_LOCK_KEY = "satellite_client_sync_lock"
SYNC_VERSION_KEY = "satellite_client_sync_version"

# Current sync version - increment this when sync logic changes
CURRENT_SYNC_VERSION = 2  # Aggressive sync version


def is_database_ready():
    """Check if database is ready and accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        logger.warning(f"Database not ready: {e}")
        return False


def should_run_sync():
    """
    Determine if sync should run based on various safety checks
    """
    # Check if we're in a test environment
    if hasattr(settings, 'TESTING') and settings.TESTING:
        logger.info("Skipping startup sync in test environment")
        return False
    
    # Check if database is ready
    if not is_database_ready():
        logger.warning("Database not ready, skipping startup sync")
        return False
    
    # Check if sync is already in progress (distributed lock)
    if cache.get(SYNC_LOCK_KEY):
        logger.info("Startup sync already in progress, skipping")
        return False
    
    # Check if sync was already completed for this version
    completed_version = cache.get(SYNC_VERSION_KEY)
    if completed_version == CURRENT_SYNC_VERSION:
        logger.info(f"Startup sync already completed for version {CURRENT_SYNC_VERSION}")
        return False
    
    return True


def acquire_sync_lock(timeout=300):
    """
    Acquire a distributed lock to prevent multiple sync processes
    """
    # Check if lock already exists
    if cache.get(SYNC_LOCK_KEY):
        logger.warning("Sync lock already exists, skipping sync")
        return False
    
    # Try to set the lock
    cache.set(SYNC_LOCK_KEY, True, timeout=timeout)
    
    # Verify we got the lock (simple race condition check)
    if cache.get(SYNC_LOCK_KEY):
        logger.info("Acquired startup sync lock")
        return True
    else:
        logger.warning("Failed to acquire startup sync lock")
        return False


def release_sync_lock():
    """Release the sync lock"""
    cache.delete(SYNC_LOCK_KEY)
    logger.info("Released startup sync lock")


def safe_sync_satellite_to_client(satellite, client):
    """
    Aggressively sync data from satellite to client - 100% overwrite
    
    This function will ALWAYS overwrite client data with satellite data
    when the satellite has data, regardless of existing client values.
    Use with caution in production.
    """
    changes_made = []
    
    try:
        # AGGRESSIVE SYNC: Always overwrite client fields with satellite data
        sync_fields = [
            ('name', 'name'),
            ('last_name', 'last_name'), 
            ('email', 'email'),
            ('phone', 'phone'),
            ('country', 'country'),
            ('city', 'city'),
            ('address', 'address'),
            ('born', 'born'),
        ]
        
        for sat_field, client_field in sync_fields:
            sat_value = getattr(satellite, sat_field)
            client_value = getattr(client, client_field)
            
            # AGGRESSIVE SYNC: Always sync if satellite has data (overwrite client data)
            if sat_value and sat_value != client_value:
                setattr(client, client_field, sat_value)
                changes_made.append(f"{client_field}: '{client_value}' -> '{sat_value}'")
        
        # AGGRESSIVE SYNC: Verification status - always sync from satellite
        if satellite.email_verified != client.email_verified:
            client.email_verified = satellite.email_verified
            changes_made.append(f"email_verified: {client.email_verified} -> {satellite.email_verified}")
        
        if satellite.document_verified != client.document_verified:
            client.document_verified = satellite.document_verified
            if satellite.document_verified and satellite.document_verified_at:
                client.document_verified_at = satellite.document_verified_at
                changes_made.append(f"document_verified: {client.document_verified} -> {satellite.document_verified} (at {satellite.document_verified_at})")
            elif not satellite.document_verified:
                client.document_verified_at = None
                changes_made.append(f"document_verified: {client.document_verified} -> {satellite.document_verified}")
            else:
                changes_made.append("document_verified: False -> True")
        
        return changes_made
        
    except Exception as e:
        logger.error(f"Error during safe sync for satellite {satellite.id}: {e}")
        raise


@transaction.atomic
def perform_startup_sync():
    """
    Main sync function with full safety measures
    """
    sync_stats = {
        'satellites_processed': 0,
        'clients_updated': 0,
        'total_changes': 0,
        'errors': 0,
        'start_time': time.time()
    }
    
    try:
        logger.info("Starting AGGRESSIVE satellite-to-client data sync (100% overwrite)...")
        
        # Get all satellites that have associated clients
        satellites_with_clients = Satellite.objects.select_related('satellite_client').filter(
            satellite_client__isnull=False
        )
        
        total_satellites = satellites_with_clients.count()
        logger.info(f"Found {total_satellites} satellites with associated clients")
        
        if total_satellites == 0:
            logger.info("No satellites with clients found, sync completed")
            return sync_stats
        
        # Performance estimates
        estimated_time = total_satellites * 0.01  # ~10ms per client
        logger.info(f"📊 Performance estimate: ~{estimated_time:.1f}s for {total_satellites} clients")
        
        if total_satellites > 100:
            logger.warning(f"⚠️  Large sync detected ({total_satellites} clients). Using batch processing...")
        elif total_satellites > 500:
            logger.error(f"🚨 Very large sync ({total_satellites} clients). Consider async processing!")
        
        # Process satellites in batches for better performance
        batch_size = 50  # Process 50 at a time
        clients_to_update = []
        
        for i, satellite in enumerate(satellites_with_clients):
            try:
                sync_stats['satellites_processed'] += 1
                client = satellite.satellite_client
                
                # Sync satellite data to client (in memory only)
                changes = safe_sync_satellite_to_client(satellite, client)
                
                if changes:
                    clients_to_update.append((client, satellite, changes))
                    sync_stats['clients_updated'] += 1
                    sync_stats['total_changes'] += len(changes)
                    
                    logger.info(f"Prepared sync: {satellite.username} -> {client.username} ({len(changes)} changes)")
                
                # Batch save every 50 clients or at the end
                if len(clients_to_update) >= batch_size or i == len(satellites_with_clients) - 1:
                    if clients_to_update:
                        # Bulk save clients
                        clients = [item[0] for item in clients_to_update]
                        Client.objects.bulk_update(clients, [
                            'name', 'last_name', 'email', 'phone', 'country', 
                            'city', 'address', 'born', 'email_verified', 
                            'document_verified', 'document_verified_at'
                        ])
                        
                        # Progress reporting
                        progress = (i + 1) / total_satellites * 100
                        logger.info(f"✅ Batch saved {len(clients)} clients [{progress:.1f}% complete - {i+1}/{total_satellites}]")
                        
                        # Log details for this batch (but limit for large syncs)
                        if total_satellites <= 20:  # Detailed logs for small syncs
                            for client, satellite, changes in clients_to_update:
                                logger.info(f"  📤 {satellite.username} -> {client.username}:")
                                for change in changes:
                                    logger.info(f"    - {change}")
                        else:  # Summary logs for large syncs
                            total_changes_in_batch = sum(len(changes) for _, _, changes in clients_to_update)
                            logger.info(f"  📊 Batch summary: {len(clients)} clients, {total_changes_in_batch} total changes")
                        
                        clients_to_update.clear()
                    
            except Exception as e:
                sync_stats['errors'] += 1
                logger.error(f"❌ Failed to sync satellite {satellite.id}: {e}")
                # Continue with other satellites even if one fails
                continue
        
        # Mark sync as completed for this version
        cache.set(SYNC_VERSION_KEY, CURRENT_SYNC_VERSION, timeout=86400 * 30)  # 30 days
        
        sync_duration = time.time() - sync_stats['start_time']
        logger.info(f"Startup sync completed successfully in {sync_duration:.2f}s")
        logger.info(f"Stats: {sync_stats['satellites_processed']} processed, "
                   f"{sync_stats['clients_updated']} clients updated, "
                   f"{sync_stats['total_changes']} total changes, "
                   f"{sync_stats['errors']} errors")
        
        return sync_stats
        
    except Exception as e:
        logger.error(f"Critical error during startup sync: {e}")
        sync_stats['errors'] += 1
        raise


@transaction.atomic 
def sync_client_to_satellites():
    """
    Sync client verification data to all their satellites
    This handles cases where admin panel changes client data
    """
    sync_stats = {
        'clients_processed': 0,
        'satellites_updated': 0, 
        'total_changes': 0,
        'errors': 0,
        'start_time': time.time()
    }
    
    try:
        logger.info("Starting client-to-satellites verification sync...")
        
        # Get all clients that have satellites
        clients_with_satellites = Client.objects.prefetch_related('satellites').filter(
            satellites__isnull=False
        ).distinct()
        
        for client in clients_with_satellites:
            try:
                sync_stats['clients_processed'] += 1
                satellites = client.satellites.all()
                
                for satellite in satellites:
                    changes = []
                    
                    # Sync verification status from client to satellite
                    if client.email_verified != satellite.email_verified:
                        satellite.email_verified = client.email_verified
                        changes.append(f"email_verified: {satellite.email_verified} -> {client.email_verified}")
                    
                    if client.document_verified != satellite.document_verified:
                        satellite.document_verified = client.document_verified
                        satellite.document_verified_at = client.document_verified_at
                        changes.append(f"document_verified: {satellite.document_verified} -> {client.document_verified}")
                    
                    if changes:
                        satellite.save()
                        sync_stats['satellites_updated'] += 1
                        sync_stats['total_changes'] += len(changes)
                        logger.info(f"Synced client {client.username} -> satellite {satellite.username}:")
                        for change in changes:
                            logger.info(f"  - {change}")
                        
            except Exception as e:
                sync_stats['errors'] += 1
                logger.error(f"Failed to sync client {client.id}: {e}")
                continue
        
        sync_duration = time.time() - sync_stats['start_time']
        logger.info(f"Client-to-satellites sync completed in {sync_duration:.2f}s")
        logger.info(f"Stats: {sync_stats['clients_processed']} clients processed, "
                   f"{sync_stats['satellites_updated']} satellites updated, " 
                   f"{sync_stats['total_changes']} total changes, "
                   f"{sync_stats['errors']} errors")
        
        return sync_stats
        
    except Exception as e:
        logger.error(f"Critical error during client-to-satellites sync: {e}")
        sync_stats['errors'] += 1
        raise


def run_startup_sync():
    """
    Main entry point for startup sync with all safety checks
    """
    if not should_run_sync():
        return
    
    # Try to acquire lock
    if not acquire_sync_lock():
        return
    
    try:
        # Perform both sync directions
        logger.info("Running bidirectional sync...")
        
        # 1. Sync satellite data to clients (fill missing client data)
        satellite_to_client_stats = perform_startup_sync()
        logger.info(f"Satellite-to-client sync completed: {satellite_to_client_stats}")
        
        # 2. Sync client verification status to satellites (ensure consistency)
        client_to_satellites_stats = sync_client_to_satellites()
        logger.info(f"Client-to-satellites sync completed: {client_to_satellites_stats}")
        
    except Exception as e:
        logger.error(f"Startup sync failed: {e}")
        # Don't re-raise to prevent app startup failure
        
    finally:
        # Always release the lock
        release_sync_lock()


def force_reset_sync_status():
    """
    Force reset sync status - use only for development/debugging
    """
    cache.delete(SYNC_VERSION_KEY)
    cache.delete(SYNC_LOCK_KEY) 
    cache.delete(SYNC_CACHE_KEY)
    logger.warning("Sync status forcefully reset")