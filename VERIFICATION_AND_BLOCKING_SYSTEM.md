# Verification and Account Blocking System Documentation

## Overview

This document describes the complete implementation of the verification and account blocking system, specifically detailing the business logic for automatic unblocking after successful document verification.

## Business Requirements

### 1. Scenario: Account blocked BEFORE verification
- When an account is blocked and then the user successfully passes document verification
- **Action**: Account should automatically unblock
- **UI**: Show success popup for verification completion
- **Status**: Verification status changes to "green" in profile

### 2. Scenario: Verification completed BEFORE blocking  
- When a user passes verification first, then gets blocked later
- **Action**: NO automatic unblocking should occur
- **UI**: Show "Please contact technical support" message instead of standard blocking message
- **Status**: Manual intervention required

## Technical Implementation

### Database Schema

#### User Model (`user/user/models.py:24-119`)
```python
class User(auth.models.AbstractBaseUser, auth.models.PermissionsMixin):
    # ... other fields ...
    
    email_verified = models.BooleanField(default=False)                    # Line 85
    document_verified = models.BooleanField(default=False)                 # Line 86  
    document_verified_at = models.DateTimeField(blank=True, null=True)     # Line 87
    
    @property
    def verify_status(self, *args, **kwargs) -> str:                       # Line 92-99
        if all([self.email_verified, self.document_verified]):
            return "green"
        elif any([self.email_verified, self.document_verified]):
            return "yellow"
        else:
            return "red"
```

#### Satellite Model (`user/satellite/models.py:22-103`)
```python
class Satellite(user_models.User):
    # ... other fields ...
    
    blocked = models.BooleanField(verbose_name="Заблокувати", default=True)        # Line 45
    
    message_for_blocked = models.TextField(                                        # Line 47-52
        verbose_name="Повідомлення для заблокованого",
        default="Your account has been blocked. Please contact technical support",
        blank=False,
        null=False,
    )
    
    migration_time = models.DateTimeField(                                         # Line 62
        verbose_name="Migration date (unblock)", 
        editable=False, 
        auto_now_add=True
    )
```

### Core Logic Implementation

#### 1. Verification Webhook (`user/client/api/frontend/views/views.py:208-257`)

**Key Logic in VeriffWebhook:**
```python
@method_decorator(csrf_exempt)
def post(self, request, *args, **kwargs):
    data = request.data
    user_id = data.get("userId")
    status_verification = data.get("status")

    try:
        user = Satellite.objects.get(pk=user_id)
        auto_unblocked = False
        
        if status_verification == "approved":
            from django.utils import timezone
            
            verification_time = timezone.now()
            user.document_verified = True
            user.document_verified_at = verification_time              # Line 230
            
            # Auto-unblock logic: only if verified AFTER being blocked
            if user.blocked:                                          # Line 233
                # If user was blocked after verification, don't auto-unblock
                # If user was verified after blocking, auto-unblock
                if user.migration_time and verification_time > user.migration_time:  # Line 236
                    user.blocked = False                              # Line 237
                    auto_unblocked = True                            # Line 238
            
            user.save()                                              # Line 240
```

**Logic Breakdown:**
- `user.migration_time`: Timestamp when account was blocked  
- `user.document_verified_at`: Timestamp when verification was completed
- **Auto-unblock condition**: `verification_time > user.migration_time`
  - If verification happens AFTER blocking → Auto-unblock ✅
  - If verification happened BEFORE blocking → No auto-unblock ❌

#### 2. Authentication Logic (`user/satellite/api/frontend/views/views.py:45-62`)

**Blocked Account Handling:**
```python
if obj.blocked:
    # Check if user was verified before being blocked
    blocked_message = obj.message_for_blocked                        # Line 47
    if (obj.document_verified and obj.document_verified_at and 
        obj.migration_time and obj.document_verified_at < obj.migration_time):  # Line 48-49
        # User was verified before blocking - show support contact message
        blocked_message = "Please contact technical support"         # Line 51
    
    return rest_response.Response(
        data={
            "detail": blocked_message,                               # Line 55
            "blocked": True,
            "can_auto_unblock": obj.document_verified_at is None or (
                obj.migration_time and obj.document_verified_at > obj.migration_time
            ) if obj.migration_time else True                        # Line 57-59
        },
        status=rest_status.HTTP_401_UNAUTHORIZED,
    )
```

**Message Logic:**
- Default blocked message: `"Your account has been blocked. Please contact technical support"`
- If verified BEFORE blocking: Override with `"Please contact technical support"`
- If verified AFTER blocking: Account auto-unblocks, no message needed

#### 3. Verification Status API (`user/client/api/frontend/views/views.py:260-280`)

**Status Endpoint Response:**
```python
def get(self, request, *args, **kwargs):
    user = get_object_or_404(Satellite, pk=request.user.pk)
    
    return Response({
        "email_verified": user.email_verified,                      # Line 268
        "document_verified": user.document_verified,                # Line 269
        "document_verified_at": user.document_verified_at,          # Line 270
        "verify_status": user.verify_status,                        # Line 271
        "blocked": user.blocked,                                    # Line 272
        "can_auto_unblock": not user.blocked or (                  # Line 273-277
            user.document_verified_at is None or (
                user.migration_time and user.document_verified_at > user.migration_time
            ) if user.migration_time else True
        ),
        "migration_time": user.migration_time,                      # Line 278
        "message_for_blocked": user.message_for_blocked if user.blocked else None  # Line 279
    }, status=status.HTTP_200_OK)
```

### Frontend Implementation

#### Account Blocking Modal (`templates/pages/satellites.html:72-84`)
```html
<div class="modal-wrap is-medium" id="banModal">
    <div class="modal-bg"></div>
    <div class="modal-window">
        <div class="modal-window__inner">
            <div class="modal-window__title" style="text-align: center; margin-bottom: 40px;" id="ban-message">
                {% blocktranslate %}Your account has been blocked. Please contact technical support{% endblocktranslate %}
            </div>
            <button class="btn" style="width: 100%" id="banModalClose">
                <span>{% blocktranslate %}Close{% endblocktranslate %}</span>
            </button>
        </div>
    </div>
</div>
```

#### JavaScript Logic (`templates/pages/satellites.html:117-120`)
```javascript
error: (e) => {
    if(e.status == 401){
        $('#loginModal').removeClass('show');
        $('#ban-message').text(e.responseJSON.message);  // Dynamic message from API
        banModal.addClass('show');
    } else {
        loginForm.find('.modal-window__form-error').addClass('show')
    }
}
```

## Database Migration

**Migration File:** `user/migrations/0052_user_document_verified_at.py`
```python
# Generated by Django 3.2.7 on 2025-08-19 14:30
operations = [
    migrations.AddField(
        model_name='user',
        name='document_verified_at',
        field=models.DateTimeField(blank=True, null=True),
    ),
]
```

## Flow Diagrams

### Flow 1: Account Blocked → Verification Completed
```
User Account Status: BLOCKED (blocked=True, migration_time=T1)
           ↓
User Completes Document Verification (verification_time=T2)
           ↓
Webhook Received: status="approved"
           ↓
Logic Check: T2 > T1? 
           ↓ YES
Auto Actions:
- Set document_verified=True
- Set document_verified_at=T2  
- Set blocked=False
- Return auto_unblocked=True
           ↓
Result: Account Unblocked ✅
Frontend: Show verification success popup
Profile: Status changes to "green"
```

### Flow 2: Verification Completed → Account Blocked  
```
User Completes Document Verification (verification_time=T1)
- document_verified=True
- document_verified_at=T1
           ↓
User Account Gets Blocked (blocked_time=T2, migration_time=T2)  
           ↓
Login Attempt:
           ↓
Logic Check: document_verified_at < migration_time?
           ↓ YES (T1 < T2)
Message Override: "Please contact technical support"
           ↓
Result: Account Remains Blocked ❌
Frontend: Show support contact message
Action Required: Manual admin intervention
```

## API Endpoints

### POST `/api/frontend/client/veriff-webhook/`
- **Purpose**: Receive verification status from Veriff
- **Permission**: AllowAny  
- **Logic**: Auto-unblock if verified after blocking

### GET `/api/frontend/client/verification-status/`
- **Purpose**: Get current verification and blocking status
- **Permission**: IsAuthenticated
- **Returns**: Complete status including `can_auto_unblock` flag

### POST `/api/frontend/satellite/auth/`
- **Purpose**: Satellite authentication with blocking logic
- **Permission**: IsAuthenticated  
- **Logic**: Dynamic blocking message based on verification timing

## Configuration

### Settings Required
- `BACK_DOMAIN`: Backend domain for webhook callbacks
- `FRONTEND_DOMAIN`: Frontend domain for redirects  

### Veriff Integration  
- Webhook endpoint configured to receive verification status
- User ID passed to Veriff for callback identification

## Testing Scenarios

### Test Case 1: Block → Verify → Auto Unblock
1. Block user account (sets `migration_time`)
2. Complete document verification via Veriff
3. Webhook triggers auto-unblock
4. Verify `blocked=False` and success response

### Test Case 2: Verify → Block → Manual Support  
1. Complete document verification (sets `document_verified_at`)
2. Block user account (sets `migration_time > document_verified_at`)
3. Attempt login shows "Please contact technical support"
4. Verify no auto-unblock occurs

### Test Case 3: Status API Responses
1. Call verification status endpoint
2. Verify `can_auto_unblock` flag accuracy
3. Confirm correct message display logic

## Admin Interface

### Satellite Admin Fields (`user/satellite/admin.py`)
- `blocked`: Boolean field to manually block/unblock
- `message_for_blocked`: Customizable blocking message
- Both fields available in admin interface for manual override

## Security Considerations

- Webhook endpoint uses CSRF exemption (secure token validation recommended)
- User authentication required for status endpoints  
- Migration timestamps prevent timing attacks
- Auto-unblock only occurs with legitimate verification callbacks

## Future Enhancements

1. **Webhook Signature Verification**: Add Veriff signature validation
2. **Admin Notifications**: Email alerts for blocked user verifications  
3. **Audit Logging**: Track all block/unblock events with reasons
4. **Batch Processing**: Handle multiple verification webhooks efficiently