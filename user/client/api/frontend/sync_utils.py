"""
Utility functions for syncing data between Satellite and Client models
"""

from user.client.models import Client
from user.satellite.models import Satellite

def sync_satellite_to_client(satellite, client=None, force=False):
    """
    Sync satellite data to its associated client
    
    Args:
        satellite: Satellite instance
        client: Client instance (optional, will be retrieved if not provided)
        force: If True, overwrite existing client data
    
    Returns:
        bool: True if any data was synced, False otherwise
    """
    if not client:
        if hasattr(satellite, 'satellite_client') and satellite.satellite_client:
            client = satellite.satellite_client
        else:
            return False
    
    updated = False
    
    # Sync basic profile data
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
    
    # Sync verification status (only if client doesn't have it)
    if satellite.email_verified and (not client.email_verified or force):
        client.email_verified = satellite.email_verified
        updated = True
    
    if satellite.document_verified and (not client.document_verified or force):
        client.document_verified = satellite.document_verified
        client.document_verified_at = satellite.document_verified_at
        updated = True
    
    # Save client if any data was updated
    if updated:
        client.save()
    
    return updated


def auto_sync_on_api_access(user):
    """
    Automatically sync satellite data to client when API is accessed
    This helps ensure client data is up-to-date without manual intervention
    
    Args:
        user: The authenticated user (could be Satellite or Client)
    
    Returns:
        tuple: (satellite_instance, client_instance, was_synced)
    """
    if isinstance(user, Satellite):
        # User is a Satellite
        satellite = user
        if hasattr(satellite, 'satellite_client') and satellite.satellite_client:
            client = satellite.satellite_client
            was_synced = sync_satellite_to_client(satellite, client, force=False)
            return satellite, client, was_synced
        return satellite, None, False
    
    elif isinstance(user, Client):
        # User is a Client
        client = user
        # Find a satellite to potentially sync from (use the first one)
        satellite = client.satellites.first()
        if satellite:
            was_synced = sync_satellite_to_client(satellite, client, force=False)
            return satellite, client, was_synced
        return None, client, False
    
    return None, None, False