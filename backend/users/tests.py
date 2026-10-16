import uuid
from urllib.parse import urlencode
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from users.utils.email_service import send_password_reset_email

User = get_user_model()

PASSWORD = "Str0ng!Pass"
NEW_PASSWORD = "N3w!Secret"


class UsersAPITestBase(APITestCase):
    def setUp(self):
        # Patch where the functions are looked up (users.views), not where they
        # are defined: views.py did `from ... import send_verification_email`,
        # so it holds its own reference. Started in setUp (not a class
        # decorator) because class-level @patch skips inherited subclasses.
        self.send_code = self._patch("users.views.send_verification_email")
        self.send_reset = self._patch("users.views.send_password_reset_email")

    def _patch(self, target):
        patcher = patch(target, return_value=True)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def make_user(self, email="user@example.com", password=PASSWORD, **extra):
        extra.setdefault("is_active", True)
        extra.setdefault("email_verified", extra["is_active"])
        return User.objects.create_user(email=email, password=password, **extra)

    def login(self, email="user@example.com", password=PASSWORD):
        return self.client.post(reverse("token_obtain_pair"), {"email": email, "password": password})

    def auth_as(self, user):
        access = self.login(user.email).data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")


class RegistrationTests(UsersAPITestBase):
    url = reverse("register")

    def test_valid_registration_creates_inactive_user_and_sends_code(self):
        res = self.client.post(self.url, {"email": "new@example.com", "password": PASSWORD, "confirm_password": PASSWORD})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="new@example.com")
        self.assertFalse(user.is_active)
        self.send_code.assert_called_once_with("new@example.com", user.verification_code)

    def test_duplicate_email_rejected(self):
        self.make_user(email="taken@example.com")
        res = self.client.post(self.url, {"email": "taken@example.com", "password": PASSWORD, "confirm_password": PASSWORD})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="taken@example.com").count(), 1)
        self.send_code.assert_not_called()

    def test_weak_passwords_rejected(self):
        for weak in ["Sh0rt!", "alllower1!", "NoDigits!!", "NoSpecial11", "Newuser1!x"]:
            with self.subTest(password=weak):
                res = self.client.post(self.url, {"email": "newuser@example.com", "password": weak, "confirm_password": weak})
                self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.exists())
        self.send_code.assert_not_called()


class LoginAndRefreshTests(UsersAPITestBase):
    def test_login_returns_tokens_and_user(self):
        self.make_user()
        res = self.login()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)
        self.assertEqual(res.data["user"]["email"], "user@example.com")

    def test_wrong_password_rejected(self):
        self.make_user()
        res = self.login(password="Wr0ng!Pass")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["non_field_errors"], ["Invalid email or password."])

    def test_unverified_user_cannot_log_in(self):
        self.make_user(is_active=False)
        res = self.login()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("access", res.data)
        self.send_code.assert_called_once()  # no code sent recently, so a fresh one goes out

    def test_refresh_issues_new_access_token(self):
        self.make_user()
        refresh = self.login().data["refresh"]

        res = self.client.post(reverse("token_refresh"), {"refresh": refresh})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        # The frontend saves data.refresh after refreshing; needs ROTATE_REFRESH_TOKENS.
        self.assertNotEqual(res.data["refresh"], refresh)

    def test_garbage_refresh_token_rejected(self):
        res = self.client.post(reverse("token_refresh"), {"refresh": "not-a-token"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class EmailVerificationTests(UsersAPITestBase):
    url = reverse("verify_email")

    def setUp(self):
        super().setUp()
        self.user = self.make_user(is_active=False, verification_code="123456")

    def test_valid_code_activates_user(self):
        res = self.client.post(self.url, {"email": self.user.email, "code": "123456"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertTrue(self.user.email_verified)
        self.assertIsNone(self.user.verification_code)

    def test_invalid_code_rejected(self):
        res = self.client.post(self.url, {"email": self.user.email, "code": "000000"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    # Regression: a used code is stored as None, so a request without a code
    # used to match (None == None) and let an admin-deactivated user reactivate.
    def test_missing_code_does_not_reactivate_user(self):
        self.user.verification_code = None
        self.user.save()

        res = self.client.post(self.url, {"email": self.user.email})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class DisabledAccountTests(UsersAPITestBase):
    """An admin-disabled user (verified, inactive) must not be able to self-reactivate."""

    def setUp(self):
        super().setUp()
        self.user = self.make_user(is_active=False, email_verified=True)

    def test_login_rejected_without_sending_code(self):
        res = self.login()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["non_field_errors"], ["This account has been disabled."])
        self.send_code.assert_not_called()

    def test_resend_verification_sends_nothing(self):
        res = self.client.post(reverse("resend_verification"), {"email": self.user.email})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.send_code.assert_not_called()

    def test_verify_email_does_not_reactivate(self):
        self.user.verification_code = "123456"  # e.g. a stale code left over
        self.user.save()

        res = self.client.post(reverse("verify_email"), {"email": self.user.email, "code": "123456"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class PasswordResetTests(UsersAPITestBase):
    def test_forgot_password_sets_token_and_sends_link(self):
        user = self.make_user()
        res = self.client.post(reverse("forgot_password"), {"email": user.email})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertIsNotNone(user.password_reset_token)
        self.send_reset.assert_called_once_with(user.email, str(user.password_reset_token))

    def test_forgot_password_response_does_not_reveal_accounts(self):
        known = self.make_user()
        cooling_down = self.make_user(email="recent@example.com", password_reset_requested_at=now())
        url = reverse("forgot_password")

        responses = [self.client.post(url, {"email": e}) for e in (known.email, cooling_down.email, "nobody@example.com")]

        self.assertEqual({r.status_code for r in responses}, {status.HTTP_200_OK})
        self.assertEqual(len({str(r.data) for r in responses}), 1)
        # Only the known user outside the cooldown actually gets an email.
        self.send_reset.assert_called_once()
        self.assertEqual(self.send_reset.call_args.args[0], known.email)

    def _user_with_token(self, requested_at=None, email="user@example.com"):
        return self.make_user(email=email, password_reset_token=uuid.uuid4(), password_reset_requested_at=requested_at or now())

    def test_reset_with_valid_token_changes_password_once(self):
        user = self._user_with_token()
        payload = {"token": str(user.password_reset_token), "new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD}

        res = self.client.post(reverse("reset_password"), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password(NEW_PASSWORD))

        # Replaying the same link must fail: the token is recorded as used.
        res = self.client.post(reverse("reset_password"), payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_with_expired_token_rejected(self):
        user = self._user_with_token(requested_at=now() - timedelta(hours=2))
        res = self.client.post(
            reverse("reset_password"),
            {"token": str(user.password_reset_token), "new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password(PASSWORD))

    def test_validate_reset_token(self):
        valid = self._user_with_token()
        expired = self._user_with_token(requested_at=now() - timedelta(hours=2), email="expired@example.com")
        url = reverse("validate-reset-token")

        self.assertEqual(self.client.post(url, {"token": str(valid.password_reset_token)}).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(url, {"token": str(expired.password_reset_token)}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_with_unknown_token_rejected(self):
        res = self.client.post(
            reverse("reset_password"),
            {"token": str(uuid.uuid4()), "new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)


class ResetEmailTests(APITestCase):
    @override_settings(FRONTEND_URL="https://app.example.com")
    @patch("users.utils.email_service.EmailClient")
    def test_reset_link_uses_frontend_url(self, client_cls):
        send_password_reset_email("user@example.com", "tok")

        message = client_cls.from_connection_string.return_value.begin_send.call_args.args[0]
        self.assertIn("https://app.example.com/reset-password?token=tok", message["content"]["plainText"])


class ProfileAndAccountSettingsTests(UsersAPITestBase):
    def setUp(self):
        super().setUp()
        self.user = self.make_user()
        self.auth_as(self.user)

    def test_profile_requires_auth(self):
        self.client.credentials()  # drop the token
        res = self.client.get(reverse("user_profile"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_and_update_profile(self):
        res = self.client.put(reverse("user_profile"), {"first_name": "Ada", "city": "London"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(reverse("user_profile"))
        self.assertEqual(res.data["first_name"], "Ada")
        self.assertEqual(res.data["city"], "London")

    def test_change_password(self):
        res = self.client.post(
            reverse("change-password"),
            {"old_password": PASSWORD, "new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(NEW_PASSWORD))

    def test_change_password_wrong_old_password(self):
        res = self.client.post(
            reverse("change-password"),
            {"old_password": "Wr0ng!Pass", "new_password": NEW_PASSWORD, "confirm_password": NEW_PASSWORD},
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_email_flow(self):
        res = self.client.post(reverse("change-email"), {"new_email": "moved@example.com"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.send_code.assert_called_once_with("moved@example.com", self.user.email_change_code)

        res = self.client.post(reverse("verify-new-email"), {"code": "wrong"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(reverse("verify-new-email"), {"code": self.user.email_change_code})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "moved@example.com")

    def test_change_email_to_taken_address_rejected(self):
        self.make_user(email="other@example.com")
        res = self.client.post(reverse("change-email"), {"new_email": "other@example.com"})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.send_code.assert_not_called()


class AdminAccessTests(UsersAPITestBase):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser(email="admin@example.com", password=PASSWORD)
        self.user = self.make_user()

    def test_anonymous_and_regular_users_blocked(self):
        detail = reverse("admin_user_detail", args=[self.user.id])
        for who in (None, self.user):
            self.client.credentials()
            if who:
                self.auth_as(who)
            with self.subTest(user=who):
                self.assertIn(self.client.get(reverse("admin_users")).status_code, (401, 403))
                self.assertIn(self.client.delete(detail).status_code, (401, 403))
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_admin_can_list_update_and_delete_users(self):
        self.auth_as(self.admin)
        detail = reverse("admin_user_detail", args=[self.user.id])

        res = self.client.get(reverse("admin_users"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual({u["email"] for u in res.data}, {"admin@example.com", "user@example.com"})
        self.assertTrue(all(u["email_verified"] for u in res.data))

        res = self.client.get(detail)
        self.assertTrue(res.data["email_verified"])

        res = self.client.put(detail, {"is_active": False}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        res = self.client.delete(detail)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_admin_update_parses_form_encoded_booleans(self):
        self.auth_as(self.admin)
        detail = reverse("admin_user_detail", args=[self.user.id])
        form = "application/x-www-form-urlencoded"

        res = self.client.put(detail, urlencode({"is_active": "false"}), content_type=form)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)  # bool("false") would have been True

        res = self.client.put(detail, urlencode({"is_staff": "maybe"}), content_type=form)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)

    def test_admin_get_missing_user_404(self):
        self.auth_as(self.admin)
        res = self.client.get(reverse("admin_user_detail", args=[99999]))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
