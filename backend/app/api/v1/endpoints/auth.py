"""Authentication Endpoints"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_active_user,
)
from app.core.config import settings
from app.core.exceptions import AuthenticationException, ConflictException
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UserResponse,
)
import structlog

logger = structlog.get_logger()
router = APIRouter()


@router.post("/local/login", response_model=TokenResponse)
async def local_login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """Local username/password login"""
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user or not user.hashed_password:
        raise AuthenticationException("Invalid credentials")
    
    if not verify_password(login_data.password, user.hashed_password):
        raise AuthenticationException("Invalid credentials")
    
    if not user.is_active:
        raise AuthenticationException("Inactive user")
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info("User logged in", user_id=str(user.id), username=user.username)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/local/register", response_model=UserResponse)
async def register_user(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == register_data.username) | (User.email == register_data.email)
    ).first()
    
    if existing_user:
        raise ConflictException("User already exists")
    
    # Create user
    user = User(
        email=register_data.email,
        username=register_data.username,
        hashed_password=hash_password(register_data.password),
        full_name=register_data.full_name,
        role=UserRole.VIEWER,  # Default role
        auth_provider="local",
        is_active=True,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("User registered", user_id=str(user.id), username=user.username)
    
    return UserResponse.model_validate(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Refresh access token"""
    try:
        payload = decode_token(refresh_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationException("Invalid token type")
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise AuthenticationException("Token refresh failed")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.get("/oauth/start")
async def oauth_start(provider: str):
    """
    Start OAuth flow (redirect to provider)
    Placeholder for OAuth implementation
    """
    if provider == "azure" and settings.OAUTH_AZURE_ENABLED:
        # Redirect to Azure AD
        redirect_url = (
            f"https://login.microsoftonline.com/{settings.OAUTH_AZURE_TENANT_ID}/oauth2/v2.0/authorize"
            f"?client_id={settings.OAUTH_AZURE_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={settings.BACKEND_URL}/api/v1/auth/oauth/callback"
            f"&scope=openid%20profile%20email"
        )
        return {"redirect_url": redirect_url}
    
    elif provider == "google" and settings.OAUTH_GOOGLE_ENABLED:
        # Redirect to Google
        redirect_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={settings.OAUTH_GOOGLE_CLIENT_ID}"
            f"&response_type=code"
            f"&redirect_uri={settings.BACKEND_URL}/api/v1/auth/oauth/callback"
            f"&scope=openid%20profile%20email"
        )
        return {"redirect_url": redirect_url}
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth provider '{provider}' not enabled or supported"
        )


@router.get("/oauth/callback")
async def oauth_callback(code: str, state: str = None):
    """
    OAuth callback
    Placeholder - implement full OAuth flow
    """
    # TODO: Implement full OAuth flow
    # 1. Exchange code for tokens
    # 2. Get user info from provider
    # 3. Create or update user in database
    # 4. Return JWT tokens
    return {"message": "OAuth callback - implement full flow"}


@router.post("/saml/acs")
async def saml_acs():
    """
    SAML Assertion Consumer Service
    Placeholder for SAML implementation
    """
    # TODO: Implement SAML ACS
    return {"message": "SAML ACS - implement full flow"}

