from rest_framework.exceptions import PermissionDenied


class PermissionMixin:
    """Memeriksa apakah pengguna memiliki permission tertentu di gunakan permissionMixin."""

    def permission_check(self, perm):
        """Memeriksa apakah pengguna memiliki permission tertentu."""
        if not self.request.user.has_perm(perm):
            print(f"User does not have permission to perform this action: {perm}")
            raise PermissionDenied("You do not have permission to perform this action.")
