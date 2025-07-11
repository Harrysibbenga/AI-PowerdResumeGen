from fastapi import APIRouter
from . import users, password, email, two_factor, login, session, admin, register

router = APIRouter()

router.include_router(admin.router, tags=["Admin"])
router.include_router(email.router, tags=["Email"])
router.include_router(login.router, tags=["Login"])
router.include_router(password.router, tags=["Password"])
router.include_router(register.router, tags=["Registration"])
router.include_router(session.router, tags=["Session"])
router.include_router(two_factor.router, tags=["2FA"])
router.include_router(users.router, tags=["Users"])