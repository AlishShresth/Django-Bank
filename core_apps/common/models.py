import uuid
from typing import Any, Optional
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


User = get_user_model()


class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """Custom QuerySet for soft delete functionality"""

    def delete(self):
        """Soft delete all objects in the queryset"""
        return self.update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Permanently delete all objects in the queryset"""
        return super().delete()

    def alive(self):
        """Return only non-deleted objects"""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only deleted objects"""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects by default"""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        """Return all objects including soft-deleted ones"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        """Return only soft-deleted objects"""
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()


class SoftDeleteModel(models.Model):
    """Abstract base model that provides soft delete functionality"""

    is_deleted = models.BooleanField(
        _("Is Deleted"),
        default=False,
        db_index=True,
    )
    deleted_at = models.DateTimeField(
        _("Deleted At"),
        null=True,
        blank=True,
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="%(class)s_deletes",
        verbose_name=_("Deleted By"),
    )

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def soft_delete(self, deleted_by=None):
        """Soft delete this object"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def restore(self):
        """Restore this soft-deleted object"""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

    def delete(self, using=None, keep_parents=False):
        """Override delete to perform soft delete by default"""
        self.soft_delete()

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete this object from the database"""
        super.delete(using=using, keep_parents=keep_parents)


class ContentView(TimeStampedModel):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, verbose_name=_("Content Type")
    )
    object_id = models.UUIDField(verbose_name=_("Object ID"))
    content_object = GenericForeignKey("content_type", "object_id")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_views",
        verbose_name=_("User"),
    )
    viewer_ip = models.GenericIPAddressField(
        verbose_name=_("Viewer IP Address"),
        null=True,
        blank=True,
    )
    last_viewed = models.DateTimeField()

    class Meta:
        verbose_name = _("Content View")
        verbose_name_plural = _("Content Views")
        unique_together = ["content_type", "object_id", "user", "viewer_ip"]

    def __str__(self) -> str:
        return f"{self.content_type} viewed by {self.user.get_full_name if self.user else 'Anonymous'} from IP {self.viewer_ip}"

    @classmethod
    def record_view(
        cls, content_object: Any, user: Optional[User], viewer_ip: Optional[str]
    ) -> None:
        content_type = ContentType.objects.get_for_model(content_object)

        try:
            view, created = cls.objects.get_or_create(
                content_type=content_type,
                object_id=content_object.id,
                defaults={
                    "user": user,
                    "viewer_ip": viewer_ip,
                    "last_viewed": timezone.now(),
                },
            )
            if not created:
                view.last_viewed = timezone.now()
                view.save()
        except IntegrityError:
            pass
