# from django.contrib.auth.base_user import BaseUserManager
# from django.utils.translation import gettext_lazy as _


# class CustomUserManager(BaseUserManager):
#     """
#     Custom user model manager where email is the unique identifiers
#     for authentication instead of usernames.
#     """

#     def create_user(self, email, password, username, first_name, last_name, ):
#         """
#         Create and save a user with the given email and password.
#         """
#         if not email:
#             raise ValueError(_("The Email must be set"))
#         if not username:
#             raise ValueError(_('User must have a username'))

#         email = self.normalize_email(email)
#         user = self.model(email=email, username=username,
#                           first_name=first_name, last_name=last_name)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password, username, first_name, last_name):
#         """
#         Create and save a SuperUser with the given email and password.
#         """
#         user = self.create_user(
#             email=self.normalize_email(email),
#             username=username,
#             password=password,
#             first_name=first_name,
#             last_name=last_name
#         )

#         user.is_admin = True
#         user.is_active = True
#         user.is_staff = True
#         user.is_superuser = True

#         user.save(using=self._db)


from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
