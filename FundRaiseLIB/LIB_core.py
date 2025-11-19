from FundRaiseDAL import DAL_core
from FundRaiseDAL import DAL_recipient, DAL_service, DAL_donor


class AuthManager:
    """Handles login and registration logic."""

    def authenticate_user(self, email, password):
        """Returns (user_id, user_type) on success, (None, None) on failure."""
        return DAL_core.authenticate_user(email, password)

    def register_user(self, name, email, password, role):
        """Registers a new user after basic validation.

        Returns (True, user_id) or (False, error_message).
        """
        # Accept optional role-specific data via kwargs for future DAL handling
        role_data = None
        if isinstance(role, tuple) and len(role) == 2:
            # caller may pass (role, role_data)
            role, role_data = role
        # Basic validation
        name = (name or '').strip()
        email = (email or '').strip()
        if not name or not email or not password:
            return False, "All fields are required."
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."

        # Check if email already exists
        existing = DAL_core.fetch_user_by_email(email)
        if existing:
            return False, "Email is already registered."

        # Create user (DAL_core will hash the password)
        success, result = DAL_core.create_user(name, email, password, role)
        if success:
            # Note: role_data is currently collected by the GUI and passed here
            # but insertion into role-specific tables (Recipients/Services/Donors)
            # should be implemented in DAL layer. For now, return success and
            # the new user_id so the caller can act on role_data if desired.
            return True, result
        return False, result


class ProfileManager:
    """Simple wrapper to fetch and update user + role-specific profile data."""

    def get_profile(self, user_id):
        """Return a dict with common user fields and role-specific fields.

        Example return:
        {
            'user_id': 1,
            'name': 'Alice',
            'email': 'a@b.com',
            'role': 'Donor',
            'role_profile': { ... }
        }
        """
        user = DAL_core.fetch_user_by_id(user_id)
        if not user:
            return None
        # user => (user_id, name, email, user_type)
        uid, name, email, role = user
        result = {'user_id': uid, 'name': name, 'email': email, 'role': role}

        # Attach basic optional columns if present in Users table
        # DAL_core.fetch_user_by_id currently returns only basic fields; try to fetch phone/address if available
        # Some DB schemas may include these columns; attempt best-effort by reading via DAL_core
        # (keep None if not available)
        result['phone_number'] = None
        result['address'] = None

        # Role-specific
        if role == 'Recipient':
            rp = DAL_recipient.fetch_recipient_profile(uid)
            if rp:
                # rp expected: (user_id, contact_email, join_date)
                result['role_profile'] = {'contact_email': rp[1]}
            else:
                result['role_profile'] = {}
        elif role == 'Donor':
            try:
                dp = DAL_donor.fetch_donor_profile(uid)
            except Exception:
                dp = None
            if dp:
                # dp expected: (user_id, is_anonymous_default, join_date)
                result['role_profile'] = {'is_anonymous_default': bool(dp[1])}
            else:
                result['role_profile'] = {}
        elif role == 'Service':
            sp = DAL_service.fetch_service_profile(uid)
            if sp:
                # sp expected: (user_id, service_name, service_description, tax_id_number)
                result['role_profile'] = {
                    'service_name': sp[1],
                    'service_description': sp[2],
                    'tax_id_number': sp[3]
                }
            else:
                result['role_profile'] = {}
        else:
            result['role_profile'] = {}

        return result

    def update_profile(self, user_id, name=None, phone_number=None, address=None, role=None, role_data=None):
        """Update common + role-specific profile fields.

        Returns (True, msg) or (False, error)
        """
        # Update common Users fields
        ok, msg = DAL_core.update_user_profile(user_id, name=name, phone_number=phone_number, address=address)
        if not ok:
            return False, msg

        # Role-specific upsert
        if role and role_data is not None:
            if role == 'Recipient':
                contact = role_data.get('contact_email', None)
                return DAL_recipient.upsert_recipient_profile(user_id, contact)
            elif role == 'Donor':
                is_anon = bool(role_data.get('is_anonymous_default', False))
                return DAL_donor.upsert_donor_profile(user_id, is_anon)
            elif role == 'Service':
                sname = role_data.get('service_name', '')
                sdesc = role_data.get('service_description', '')
                tax = role_data.get('tax_id_number', '')
                return DAL_service.upsert_service_profile(user_id, sname, sdesc, tax)

        return True, 'Success'
