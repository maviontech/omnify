"""
Tests for user models: User, UserSession, account security.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from apps.users.models import User, UserSession


class TestUser:
    """Test custom User model."""

    def test_create_user(self, db, tenant):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            tenant=tenant,
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self, db):
        user = User.objects.create_superuser(
            email='super@omnify.com',
            password='superpass123',
            first_name='Super',
            last_name='Admin',
        )
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_email_is_required(self, db):
        with pytest.raises(ValueError, match="email"):
            User.objects.create_user(email='', password='testpass')

    def test_email_is_unique(self, db, tenant):
        User.objects.create_user(email='dup@test.com', password='p', tenant=tenant)
        with pytest.raises(Exception):
            User.objects.create_user(email='dup@test.com', password='p', tenant=tenant)

    def test_get_full_name(self, admin_user):
        assert admin_user.get_full_name() == 'Admin User'

    def test_get_short_name(self, admin_user):
        assert admin_user.get_short_name() == 'Admin'

    def test_str_returns_email(self, admin_user):
        assert str(admin_user) == 'admin@test-hospital.com'


class TestAccountLocking:
    """Test account locking after failed login attempts."""

    def test_not_locked_initially(self, admin_user):
        assert admin_user.is_locked() is False
        assert admin_user.failed_login_attempts == 0

    def test_increment_failed_login(self, admin_user):
        admin_user.increment_failed_login()
        assert admin_user.failed_login_attempts == 1
        assert admin_user.is_locked() is False

    def test_locks_after_5_failures(self, admin_user):
        for _ in range(5):
            admin_user.increment_failed_login()
        assert admin_user.failed_login_attempts == 5
        assert admin_user.is_locked() is True

    def test_lock_expires_after_30_minutes(self, admin_user):
        for _ in range(5):
            admin_user.increment_failed_login()
        # Simulate time passing
        admin_user.locked_until = timezone.now() - timedelta(minutes=1)
        admin_user.save()
        assert admin_user.is_locked() is False

    def test_reset_failed_login(self, admin_user):
        for _ in range(5):
            admin_user.increment_failed_login()
        admin_user.reset_failed_login()
        assert admin_user.failed_login_attempts == 0
        assert admin_user.locked_until is None
        assert admin_user.is_locked() is False

    def test_mfa_defaults(self, admin_user):
        assert admin_user.mfa_enabled is False
        assert admin_user.mfa_secret == ''
