from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from pydantic import BaseModel
from typing import Dict, Optional
import stripe
import json
from app.core.config import settings
from app.api.v1.auth import get_current_user
from firebase_admin import firestore

# Initialize Stripe
stripe.api_key = settings.STRIPE_API_KEY

router = APIRouter()
db = firestore.client()

# Models
class CheckoutSessionRequest(BaseModel):
    resumeId: Optional[str] = None
    priceId: str
    mode: str  # "payment" or "subscription"
    successUrl: Optional[str] = None
    cancelUrl: Optional[str] = None

class PortalSessionRequest(BaseModel):
    returnUrl: Optional[str] = None

class SubscriptionStatusResponse(BaseModel):
    isSubscribed: bool
    subscriptionEnd: Optional[str] = None

# Endpoints
@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Get user from Firestore
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        
        # Set up Stripe customer if it doesn't exist
        stripe_customer_id = user_data.get("stripe_id")
        
        if not stripe_customer_id:
            # Create a new Stripe customer
            customer = stripe.Customer.create(
                email=user_data["email"],
                metadata={"firebase_uid": user_id}
            )
            stripe_customer_id = customer.id
            
            # Update user with Stripe ID
            user_ref.update({"stripe_id": stripe_customer_id})
        
        # Define success and cancel URLs
        success_url = request.successUrl or "http://localhost:4321/payment-success?session_id={CHECKOUT_SESSION_ID}"
        cancel_url = request.cancelUrl or "http://localhost:4321/payment-cancel"
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": request.priceId,
                    "quantity": 1,
                },
            ],
            mode=request.mode,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "firebase_uid": user_id,
                "resume_id": request.resumeId or ""
            }
        )
        
        return {"sessionId": checkout_session.id, "url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating checkout session: {str(e)}"
        )

@router.post("/create-portal-session")
async def create_portal_session(
    request: PortalSessionRequest,
    user: Dict = Depends(get_current_user)
):
    try:
        user_id = user["uid"]
        
        # Get user from Firestore
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_data = user_doc.to_dict()
        stripe_customer_id = user_data.get("stripe_id")
        
        if not stripe_customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe customer found for this user"
            )
        
        # Create Stripe customer portal session
        return_url = request.returnUrl or "http://localhost:4321/dashboard"
        
        portal_session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )
        
        return {"url": portal_session.url}
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating portal session: {str(e)}"
        )

@router.get("/subscription-status", response_model=SubscriptionStatusResponse)
async def check_subscription_status(user: Dict = Depends(get_current_user)):
    try:
        user_id = user["uid"]
        
        # Get user from Firestore
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            return {"isSubscribed": False}
        
        user_data = user_doc.to_dict()
        
        return {
            "isSubscribed": user_data.get("subscription", False),
            "subscriptionEnd": user_data.get("subscription_end")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking subscription status: {str(e)}"
        )

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, response: Response):
    # Get the webhook payload
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        # Handle the event
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            
            # Get customer and user info
            customer_id = session["customer"]
            firebase_uid = session["metadata"]["firebase_uid"]
            resume_id = session["metadata"].get("resume_id")
            
            # Update user subscription status
            user_ref = db.collection("users").document(firebase_uid)
            
            if session["mode"] == "subscription":
                # Handle subscription payment
                user_ref.update({
                    "subscription": True,
                    "stripe_id": customer_id
                })
            
            elif session["mode"] == "payment" and resume_id:
                # Handle one-time payment
                resume_ref = db.collection("resumes").document(resume_id)
                resume_ref.update({
                    "export_status": "paid"
                })
                
                # Also record the payment
                db.collection("payments").add({
                    "user_id": firebase_uid,
                    "stripe_payment_id": session["payment_intent"],
                    "amount": session["amount_total"] / 100,  # Convert from cents
                    "product_type": "export",
                    "resume_id": resume_id,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
        
        elif event["type"] == "customer.subscription.updated":
            subscription = event["data"]["object"]
            customer_id = subscription["customer"]
            
            # Find user with this Stripe customer ID
            users = db.collection("users").where("stripe_id", "==", customer_id).limit(1).stream()
            user_doc = next(users, None)
            
            if user_doc:
                user_ref = db.collection("users").document(user_doc.id)
                
                # Update subscription status based on subscription status
                is_active = subscription["status"] in ["active", "trialing"]
                
                user_ref.update({
                    "subscription": is_active,
                    "subscription_end": subscription["current_period_end"]
                })
        
        elif event["type"] == "customer.subscription.deleted":
            subscription = event["data"]["object"]
            customer_id = subscription["customer"]
            
            # Find user with this Stripe customer ID
            users = db.collection("users").where("stripe_id", "==", customer_id).limit(1).stream()
            user_doc = next(users, None)
            
            if user_doc:
                user_ref = db.collection("users").document(user_doc.id)
                user_ref.update({
                    "subscription": False
                })
        
        return {"status": "success"}
    
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing webhook: {str(e)}"
        )