import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import EmailValidator


# ==================== USER MODEL ====================
class User(AbstractUser):
    email = models.EmailField(unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile_picture = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    # Fix the reverse accessor clash
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True,
        verbose_name="user permissions",
    )

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]  # AbstractUser uses date_joined, not created_at

    def __str__(self):
        return self.email


# ==================== CLASS MODEL ====================
class Class(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=255)
    description = models.TextField()
    class_code = models.CharField(max_length=50, unique=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_classes",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="joined_classes", blank=True
    )

    experts = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="expert_classes", blank=True
    )

    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="admin_classes", blank=True
    )

    invites = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "classes"
        ordering = ["-created_at"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.class_name


# ==================== VALIDATORS ====================
def validate_future_date(value):
    if value <= timezone.now():
        raise ValidationError("Due date must be in the future")


def validate_url(value):
    if value and not value.startswith(("http://", "https://", "ftp://")):
        raise ValidationError("Invalid document URL")


# ==================== TASK MODEL ====================
class Task(models.Model):
    STATUS_CHOICES = [
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class_id = models.ForeignKey(
        "Class",  # Same file, so just 'Class'
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    dueDate = models.DateTimeField(validators=[validate_future_date])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ongoing")

    document = models.URLField(blank=True, null=True, validators=[validate_url])

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ==================== SUBMISSION MODEL ====================
class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task_id = models.ForeignKey(
        "Task",  # Same file, so just 'Task'
        on_delete=models.CASCADE,
        related_name="submissions",
    )

    userId = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    document = models.URLField()

    feedback = models.JSONField(default=list, blank=True)
    user_upvotes = models.JSONField(default=list, blank=True)
    expert_upvotes = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "submissions"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission by {self.userId.username} for {self.task_id.title}"


# ==================== FEEDBACK MODEL ====================
class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission_id = models.ForeignKey(
        "Submission",  # Same file, so just 'Submission'
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )

    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="given_feedbacks",
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        db_table = "feedbacks"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Feedback by {self.user_id.username} on submission {self.submission_id.id}"
        )


# ==================== INVITATION MODEL ====================
class Invitation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class_id = models.ForeignKey(
        "Class",  # Same file, so just 'Class'
        on_delete=models.CASCADE,
        related_name="invitations",
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )

    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_invitations",
    )

    email = models.EmailField(validators=[EmailValidator()])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invitations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation to {self.email} for {self.class_id.class_name}"
