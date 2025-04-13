import os
import json
import stripe
from dotenv import load_dotenv
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends, status
from firebase_admin import firestore
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Set Stripe API key
stripe.api_key = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# Create router
router = APIRouter()

# Get Firestore database
db = firestore.client()

class StripeWebhookEvent(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]

@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle Stripe webhook events
    
    This endpoint processes Stripe webhook events to update subscription status,
    handle payments, and manage user access to premium features.
    """
    # Get raw request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature header")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {str(e)}")
    
    # Process different event types
    event_type = event["type"]
    
    # Handle checkout session completed
    if event_type == "checkout.session.completed":
        await handle_checkout_completed(event["data"]["object"])
    
    # Handle subscription updated
    elif event_type == "customer.subscription.updated":
        await handle_subscription_updated(event["data"]["object"])
    
    # Handle subscription deleted
    elif event_type == "customer.subscription.deleted":
        await handle_subscription_deleted(event["data"]["object"])
    
    # Return success response
    return {"status": "success", "event_type": event_type}

async def handle_checkout_completed(session: Dict[str, Any]):
    """Handle checkout.session.completed event"""
    # Get metadata from session
    metadata = session.get("metadata", {})
    firebase_uid = metadata.get("firebase_uid")
    resume_id = metadata.get("resume_id", "")
    
    if not firebase_uid:
        print(f"Warning: No Firebase UID in metadata for session {session['id']}")
        return
    
    # Get customer ID
    customer_id = session.get("customer")
    
    # Update user record
    user_ref = db.collection("users").document(firebase_uid)
    
    # Check if this was a subscription or one-time payment
    if session.get("mode") == "subscription":
        # Update user's subscription status
        user_ref.update({
            "subscription": True,
            "stripe_id": customer_id,
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        print(f"Subscription activated for user {firebase_uid}")
    
    elif session.get("mode") == "payment" and resume_id:
        # Handle one-time payment for resume export
        resume_ref = db.collection("resumes").document(resume_id)
        
        # Update resume export status
        resume_ref.update({
            "export_status": "paid",
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        
        # Record the payment
        db.collection("payments").add({
            "user_id": firebase_uid,
            "resume_id": resume_id,
            "stripe_payment_id": session.get("payment_intent"),
            "amount": session.get("amount_total") / 100,  # Convert from cents
            "currency": session.get("currency", "usd"),
            "product_type": "export",
            "created_at": firestore.SERVER_TIMESTAMP
        })
        
        print(f"One-time payment processed for resume {resume_id}")

async def handle_subscription_updated(subscription: Dict[str, Any]):
    """Handle customer.subscription.updated event"""
    # Get customer ID
    customer_id = subscription.get("customer")
    
    if not customer_id:
        print(f"Warning: No customer ID in subscription {subscription['id']}")
        return
    
    # Find user with this Stripe customer ID
    users = db.collection("users").where("stripe_id", "==", customer_id).limit(1).stream()
    user_doc = next(users, None)
    
    if not user_doc:
        print(f"Warning: No user found with Stripe customer ID {customer_id}")
        return
    
    user_ref = db.collection("users").document(user_doc.id)
    
    # Update subscription status based on subscription status
    is_active = subscription["status"] in ["active", "trialing"]
    
    user_ref.update({
        "subscription": is_active,
        "subscription_end": subscription.get("current_period_end"),
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    print(f"Subscription updated for user {user_doc.id} - Status: {subscription['status']}")

async def handle_subscription_deleted(subscription: Dict[str, Any]):
    """Handle customer.subscription.deleted event"""
    # Get customer ID
    customer_id = subscription.get("customer")
    
    if not customer_id:
        print(f"Warning: No customer ID in subscription {subscription['id']}")
        return
    
    # Find user with this Stripe customer ID
    users = db.collection("users").where("stripe_id", "==", customer_id).limit(1).stream()
    user_doc = next(users, None)
    
    if not user_doc:
        print(f"Warning: No user found with Stripe customer ID {customer_id}")
        return
    
    user_ref = db.collection("users").document(user_doc.id)
    
    # Update user's subscription status
    user_ref.update({
        "subscription": False,
        "subscription_end": firestore.SERVER_TIMESTAMP,
        "updated_at": firestore.SERVER_TIMESTAMP
    })
    
    print(f"Subscription canceled for user {user_doc.id}")