from base64 import urlsafe_b64decode

from django import http, shortcuts
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import models as django_models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from drf_spectacular import utils as drf_utils
from rest_framework import generics, status
from rest_framework import mixins as rest_mixins
from rest_framework import permissions as rest_permissions
from rest_framework import renderers as rest_renderers
from rest_framework import response as rest_response
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from utils.third_party.api.rest_framework import mixins as utils_mixins
from ..utils import send_email_message_verification, create_veriff_session, check_empty_fields
from ..sync_utils import auto_sync_on_api_access
from user.satellite.models import Satellite

from ..... import models as user_models
from .....satellite import models as satellite_models
from ..serializers import serializers as client_serializers
from .....permissions import IsNotBlocked


class ClientViewSet(
    utils_mixins.PrefetchableRetrieveMixin,
    rest_mixins.UpdateModelMixin,
):
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = shortcuts.get_object_or_404(queryset, pk=self.request.user.pk)
        self.check_object_permissions(self.request, obj)
        return obj

    @drf_utils.extend_schema(
        description="USER AUTH. Any id (for example, client/me/) returns info about authenticated user and list of all satellites.",
        responses=client_serializers.ReadClientSerializer,
    )
    def retrieve(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().retrieve(request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Update client profile information.",
        request=client_serializers.WriteClientSerializer,
        responses=client_serializers.ReadClientSerializer,
    )
    def update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().update(request=request, *args, **kwargs)

    @drf_utils.extend_schema(
        description="USER AUTH. Partially update client profile information.",
        request=client_serializers.WriteClientSerializer,
        responses=client_serializers.ReadClientSerializer,
    )
    def partial_update(self, request: http.HttpRequest, *args, **kwargs) -> rest_response.Response:
        return super().partial_update(request=request, *args, **kwargs)

    def _prefetch_retrieve(self, queryset: django_models.QuerySet) -> django_models.QuerySet:
        return queryset.prefetch_related(
            django_models.Prefetch(
                "satellites",
                queryset=satellite_models.Satellite.objects.order_by(django_models.F("order").asc(nulls_first=True)),
            )
        )

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return client_serializers.WriteClientSerializer
        return client_serializers.ReadClientSerializer

    renderer_classes = [rest_renderers.JSONRenderer]
    queryset = user_models.Client.objects
    serializer_class = client_serializers.ReadClientSerializer
    permission_classes = [rest_permissions.IsAuthenticated, IsNotBlocked]


class CreateClient(generics.CreateAPIView):
    queryset = user_models.Client.objects.all()
    serializer_class = client_serializers.CreateClientSerializer
    permission_classes = [rest_permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["is_active"] = False

        request._full_data = data
        return self.create(request, *args, **kwargs)


class EmailVerification(APIView):
    permission_classes = (rest_permissions.IsAuthenticated, IsNotBlocked)

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(Satellite, pk=request.user.pk)

        if not user.email:
            return Response({"detail": "The email field is empty"}, status=status.HTTP_400_BAD_REQUEST)

        if user.email_verified:
            return Response({"detail": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activate_path = reverse("email-activate", kwargs={"uid64": uid, "token": token})
        activate_url = f"{settings.BACK_DOMAIN}{activate_path}"

        send_email_message_verification(user, activate_url)

        return Response({"detail": "Verification email send"}, status=status.HTTP_200_OK)


class ActivateEmailAPIView(APIView):
    permission_classes = (rest_permissions.AllowAny,)

    def get(self, request, uid64, token):
        """
        Email verification endpoint.

        NOTE: This uses GET (not POST) because it's accessed via email link.
        Security is ensured by:
        1. Cryptographically secure token (default_token_generator)
        2. Token is tied to user state and expires
        3. URL parameters (uid64/token) are unpredictable

        While GET requests shouldn't normally change state, email verification
        is an accepted exception since links in emails must use GET.
        """
        try:
            uid = force_str(urlsafe_base64_decode(uid64))
            user = Satellite.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Satellite.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            # Check if already verified to prevent unnecessary updates
            if not user.email_verified:
                from django.utils import timezone
                user.email_verified = True
                user.save()

                # Also update the associated Client's email_verified field if exists
                if hasattr(user, 'satellite_client') and user.satellite_client:
                    user.satellite_client.email_verified = True
                    user.satellite_client.save()

                    # Update all satellites belonging to this client
                    for satellite in user.satellite_client.satellites.all():
                        if not satellite.email_verified:
                            satellite.email_verified = True
                            satellite.save()

        redirect_url = f"{settings.BACK_DOMAIN}/verified"

        return HttpResponseRedirect(redirect_url)
    
class StartVerificationSession(APIView):
    permission_classes = (rest_permissions.IsAuthenticated, IsNotBlocked)

    def post(self, request):
        # Check if user is a Satellite (when satellite is logged in directly)
        if hasattr(request.user, 'satellite'):
            # Satellite is directly authenticated
            user = get_object_or_404(Satellite, pk=request.user.pk)
        # Check if user is a Client (when client is verifying their satellite)
        elif hasattr(request.user, 'client'):
            client = get_object_or_404(user_models.Client, pk=request.user.pk)
            
            # Check if specific satellite ID was provided
            satellite_id = request.data.get('satellite_id')
            
            if satellite_id:
                # Get specific satellite by ID
                try:
                    satellite = client.satellites.get(id=satellite_id)
                except Satellite.DoesNotExist:
                    return Response({"detail": "Satellite not found for this client."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Get the first satellite from the client to use for verification
                satellite = client.satellites.first()
                if not satellite:
                    return Response({"detail": "No satellites found for this client."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = satellite
        else:
            return Response({"detail": "User type not supported"}, status=400)

        if user.document_verified:
            return Response({"detail": "Document is already verified."}, status=status.HTTP_400_BAD_REQUEST)
        
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        empty_fields = check_empty_fields(user)

        if empty_fields:
            return Response(
                {"detail": f"Please fill in the following fields: {', '.join(empty_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        session_url = create_veriff_session(user, request=request)

        context = {
            'session_url': session_url,
            'detail': 'Verification session started successfully.'
        }

        return Response(context, status=status.HTTP_200_OK)


class StartBlockedSatelliteVerification(APIView):
    """Handle verification for blocked satellites without requiring authentication"""
    permission_classes = [rest_permissions.AllowAny]
    
    def post(self, request):
        # Get satellite UUID and credentials from request
        uuid = request.data.get('uuid')
        username = request.data.get('username')  # This is actually the satellite's username, not email
        password = request.data.get('password')
        
        if not all([uuid, username, password]):
            return Response(
                {"detail": "UUID, username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Try to find and authenticate the satellite
        try:
            satellite = Satellite.objects.get(uuid=uuid)
        except Satellite.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify the credentials
        from django.contrib.auth import authenticate
        user_auth = authenticate(username=username, password=password)
        
        if not user_auth or user_auth.pk != satellite.pk:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if satellite is actually blocked
        if not satellite.blocked:
            return Response(
                {"detail": "This endpoint is only for blocked accounts"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already verified
        if satellite.document_verified:
            return Response(
                {"detail": "Document is already verified."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for empty required fields
        empty_fields = check_empty_fields(satellite)
        
        if empty_fields:
            return Response(
                {"detail": f"Please fill in the following fields: {', '.join(empty_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Veriff session
        try:
            session_url = create_veriff_session(satellite, request=request)
        except Exception as e:
            return Response(
                {"detail": f"Failed to create verification session: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        context = {
            'session_url': session_url,
            'detail': 'Verification session started successfully.'
        }
        
        return Response(context, status=status.HTTP_200_OK)


class CreateSupportTicket(generics.CreateAPIView):
    queryset = user_models.SupportTicket.objects.all()
    serializer_class = client_serializers.CreateSupportTicketSerializer
    permission_classes = [rest_permissions.AllowAny]


class CreatePayment(generics.CreateAPIView):
    queryset = user_models.Payment.objects.all()
    serializer_class = client_serializers.CreatePaymentSerializer
    permission_classes = [rest_permissions.AllowAny]

    @drf_utils.extend_schema(
        description="NO AUTH. Create succesfull payment.",
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GetPlan(generics.RetrieveAPIView):
    queryset = user_models.PricingPlan.objects.all()
    serializer_class = client_serializers.RetrievePlanSerializer
    permission_classes = [rest_permissions.AllowAny]

    @drf_utils.extend_schema(
        description="NO AUTH. Get plan.",
        parameters=[
            drf_utils.OpenApiParameter(
                name="name",
                description="Plus or Basic",
                required=True,
                type=drf_utils.OpenApiTypes.STR,
            )
        ],
    )
    def get(self, request, *args, **kwargs):
        full_name = self.request.GET.get("name")
        instance = shortcuts.get_object_or_404(self.queryset, full_name=full_name)
        serializer = self.get_serializer(instance)
        return rest_response.Response(serializer.data)

class VeriffWebhook(APIView):
    permission_classes = [rest_permissions.AllowAny]

    def verify_signature(self, request):
        """Verify Veriff webhook signature to ensure authenticity"""
        import hmac
        import hashlib
        from django.conf import settings

        # Get signature from header (Veriff sends it as X-AUTH-CLIENT or X-HMAC-SIGNATURE)
        signature = request.headers.get('X-AUTH-CLIENT') or request.headers.get('X-HMAC-SIGNATURE')
        if not signature:
            return False

        # Get Veriff shared secret from settings (configured in settings/project/veriff.py)
        veriff_secret = getattr(settings, 'SHARED_SECRET', None)
        if not veriff_secret:
            # Log warning if secret not configured
            import logging
            logger = logging.getLogger(__name__)
            logger.error("VERIFF SHARED_SECRET not configured in settings")
            return False

        # Calculate expected signature
        payload = request.body
        expected_signature = hmac.new(
            veriff_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(signature, expected_signature)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        # SECURITY: Verify webhook signature if SHARED_SECRET is configured
        # This is optional to maintain backward compatibility until signature is enabled in Veriff
        from django.conf import settings
        if hasattr(settings, 'SHARED_SECRET') and settings.SHARED_SECRET:
            if not self.verify_signature(request):
                import logging
                logger = logging.getLogger(__name__)
                logger.warning("Veriff webhook received with invalid signature")
                return Response(
                    {"detail": "Invalid signature"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            # Log warning that webhook is not secured
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("Veriff webhook running WITHOUT signature verification - configure SHARED_SECRET to enable security")

        data = request.data
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Veriff webhook payload: {data}")
        
        # Parse Veriff webhook payload
        # Veriff sends: {"status": "success", "verification": {"id": "...", "status": "approved", "vendorData": "user_id", ...}}
        verification_data = data.get("verification", {})
        user_id = verification_data.get("vendorData") or data.get("userId")
        status_verification = verification_data.get("status") or data.get("status")
        decision_code = verification_data.get("code")
        
        logger.info(f"Veriff webhook parsed: user_id={user_id}, status={status_verification}, code={decision_code}")

        if not user_id:
            return Response({"detail": "No user identifier in webhook"}, status=status.HTTP_400_BAD_REQUEST)

        # Оновити статус користувача
        try:
            user = Satellite.objects.get(pk=user_id)
            auto_unblocked = False
            was_blocked = user.blocked
            was_verified = user.document_verified
            
            if status_verification == "approved":
                from django.utils import timezone
                
                verification_time = timezone.now()
                user.document_verified = True
                user.document_verified_at = verification_time
                
                # Auto-unblock logic:
                # If blocked AND was NOT previously verified → auto-unblock (Scenario 1)
                # If blocked AND was already verified before → do NOT auto-unblock (Scenario 2)
                if user.blocked and not was_verified:
                    user.blocked = False
                    auto_unblocked = True
                    logger.info(f"Satellite {user_id} auto-unblocked after first verification")
                elif user.blocked and was_verified:
                    logger.info(f"Satellite {user_id} remains blocked — was already verified before blocking")
                
                user.save()
                
                # Also update the associated Client's document_verified field if exists
                if hasattr(user, 'satellite_client') and user.satellite_client:
                    user.satellite_client.document_verified = True
                    user.satellite_client.document_verified_at = verification_time
                    user.satellite_client.save()
                    
                    # Update all satellites belonging to this client
                    for satellite in user.satellite_client.satellites.all():
                        satellite.document_verified = True
                        satellite.document_verified_at = verification_time
                        satellite.save()
                
            elif status_verification == "declined":
                logger.info(f"Satellite {user_id} verification declined, code: {decision_code}")
                
            elif status_verification == "resubmission_requested":
                logger.info(f"Satellite {user_id} resubmission requested, code: {decision_code}")

        except Satellite.DoesNotExist:
            logger.error(f"Veriff webhook: Satellite {user_id} not found")
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "detail": "Webhook received",
            "verification_successful": status_verification == "approved",
            "auto_unblocked": auto_unblocked,
            "user_status": user.verify_status if status_verification == "approved" else None,
            "blocked": user.blocked if status_verification == "approved" else None,
            "can_auto_unblock": not was_verified if was_blocked else None
        }, status=status.HTTP_200_OK)


class BlockedVerificationStatusAPIView(APIView):
    """Check verification status for blocked satellites (no auth required).
    Used by frontend to poll after opening Veriff in a new tab."""
    permission_classes = [rest_permissions.AllowAny]
    
    def post(self, request):
        uuid = request.data.get('uuid')
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([uuid, username, password]):
            return Response(
                {"detail": "UUID, username and password are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            satellite = Satellite.objects.get(uuid=uuid)
        except Satellite.DoesNotExist:
            return Response(
                {"detail": "Not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify credentials
        from django.contrib.auth import authenticate
        user_auth = authenticate(username=username, password=password)
        
        if not user_auth or user_auth.pk != satellite.pk:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response({
            "blocked": satellite.blocked,
            "document_verified": satellite.document_verified,
            "verify_status": satellite.verify_status,
        }, status=status.HTTP_200_OK)


class VerificationStatusAPIView(APIView):
    permission_classes = (rest_permissions.IsAuthenticated, IsNotBlocked)

    def get(self, request, *args, **kwargs):
        """Get current verification status for the authenticated user"""
        
        # Auto-sync satellite data to client before returning status
        satellite, client, was_synced = auto_sync_on_api_access(request.user)
        
        # Check if user is a Satellite
        if hasattr(request.user, 'satellite'):
            user = get_object_or_404(Satellite, pk=request.user.pk)
            return Response({
                "email_verified": user.email_verified,
                "document_verified": user.document_verified,
                "document_verified_at": user.document_verified_at,
                "verify_status": user.verify_status,
                "blocked": user.blocked,
                "can_auto_unblock": user.blocked and not user.document_verified,
                "migration_time": user.migration_time,
                "message_for_blocked": user.message_for_blocked if user.blocked else None
            }, status=status.HTTP_200_OK)
        
        # Check if user is a Client
        elif hasattr(request.user, 'client'):
            client = get_object_or_404(user_models.Client, pk=request.user.pk)
            
            # Check if client has any blocked satellites
            blocked_satellites = client.satellites.filter(blocked=True)
            has_blocked_satellites = blocked_satellites.exists()
            
            # Get verification status from client
            return Response({
                "email_verified": client.email_verified,
                "document_verified": client.document_verified,
                "document_verified_at": client.document_verified_at,
                "verify_status": client.verify_status,
                "blocked": has_blocked_satellites,  # Client is considered "blocked" if any satellites are blocked
                "can_auto_unblock": not has_blocked_satellites or not client.document_verified,
                "migration_time": None,
                "message_for_blocked": "Your satellites have been blocked. Complete verification to regain access." if has_blocked_satellites else None
            }, status=status.HTTP_200_OK)
        
        else:
            return Response({"detail": "User type not supported"}, status=400)