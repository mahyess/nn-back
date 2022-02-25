import datetime
import re
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .gender import Gender


class Role(models.Model):
    title = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class User(AbstractUser):
    uid = models.CharField(unique=True, null=True, blank=True, max_length=255)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, null=True)
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="role", null=True, blank=True
    )

    phone_number = models.CharField(max_length=20, null=True, blank=True)

    NORMAL = "nl"
    PAGE = "pg"
    CELEBRITY = "cb"
    CATEGORY_CHOICES = ((NORMAL, "Normal"), (PAGE, "Page"), (CELEBRITY, "Celebrity"))
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default=NORMAL)
    full_name = models.CharField(max_length=180, null=True)

    # online = models.BooleanField(null=False, blank=False, default=False)

    REQUIRED_FIELDS = ["email", "uid"]

    def __str__(self):
        return self.username

    class Meta:
        db_table = "User"

    def clean(self):
        super().clean()
        # on create only
        # --------------
        if not self.id:
            # username
            username_pattern = (
                "^(?=.{4,18}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"
            )
            username_validator = re.findall(username_pattern, self.username)
            if not username_validator:
                raise ValidationError(
                    detail={
                        "username": "username must be 4-18 char long and must not contain any special chars "
                        "or white spaces except _ "
                    },
                    code=status.HTTP_400_BAD_REQUEST,
                )

        # email
        if self.email:
            if (
                self.__class__.objects.filter(email=self.email)
                .exclude(id=self.id)
                .exists()
            ):
                raise ValidationError(
                    detail={"email": "Email already taken."},
                    code=status.HTTP_400_BAD_REQUEST,
                )
            self.email = self.__class__.objects.normalize_email(self.email)

        # # password
        # try:
        #     validate_password(self.password)
        # except ValidationError as e:
        #     print(e)
        #     raise ValidationError(detail=e,
        #                           code=status.HTTP_400_BAD_REQUEST)

        # phone number
        if self.phone_number:
            if self.__class__.objects.filter(phone_number=self.phone_number).exists():
                raise ValidationError(
                    detail={"phone_number": "User with phone number exists."},
                    code=status.HTTP_400_BAD_REQUEST,
                )

        if not self.gender or self.gender == "":
            raise ValidationError(
                detail={"gender": "gender is required."},
                code=status.HTTP_400_BAD_REQUEST,
            )
        elif type(self.gender) != Gender:
            raise ValidationError(
                detail={"gender": "Invalid gender."}, code=status.HTTP_400_BAD_REQUEST
            )

        # names
        if (
            not self.first_name
            or self.first_name == ""
            or not self.last_name
            or self.last_name == ""
        ):
            raise ValidationError(
                detail={"names": "first name and last name is required."},
                code=status.HTTP_400_BAD_REQUEST,
            )

        if not self.email and not self.phone_number:
            raise ValidationError(
                detail={"email": "Either email or phone number is required."},
                code=status.HTTP_400_BAD_REQUEST,
            )

    def save(self, *args, **kwargs):
        # if not self.is_superuser:
        #     self.full_clean()

        if not self.id:
            self.uid = str(uuid.uuid4().hex)

        self.full_name = f"{self.first_name} {self.last_name}"
        super(User, self).save(*args, **kwargs)

    def last_seen(self):
        return cache.get(f"user_{self.username}_seen")

    def online(self):
        if self.last_seen():
            now = timezone.now()
            return now > self.last_seen() + datetime.timedelta(
                seconds=settings.USER_ONLINE_TIMEOUT
            )
        return False

    # @property
    # def full_name(self):
    #     return self.first_name + " " + self.last_name

    @property
    def category_verbose(self):
        return dict(User.CATEGORY_CHOICES)[self.category]
