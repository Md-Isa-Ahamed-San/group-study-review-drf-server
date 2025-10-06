import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone


# ==================== USER MODEL ====================
# We inherit from AbstractUser to get Django's built-in authentication fields
# (like password, last_login, is_superuser) while still being able to customize it.
class User(AbstractUser):

    email = models.EmailField(unique=True)

    # We are using a UUID for the primary key instead of the default integer ID.
    # This is a good practice for security as it prevents enumeration attacks
    # and hides the total number of users.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # An optional field to store the URL of the user's profile picture.
    # `blank=True` allows the field to be empty in forms (like the Django admin).
    # `null=True` allows the database to store a NULL value for this field.
    profile_picture = models.URLField(blank=True, null=True)

    # This field is inherited from AbstractUser but is good to be aware of.
    # It controls whether the user is considered "active". Instead of deleting a user,
    # it's often better to set `is_active` to False (a "soft delete").
    is_active = models.BooleanField(default=True)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # --- IMPORTANT: Fix for Custom User Models ---
    # When you use a custom user model, you must redefine the many-to-many relationships
    # to Django's built-in Group and Permission models.
    #
    # The Problem: Both the original `auth.User` and your new `User` model have a
    # relationship with `Group` and `Permission`. By default, Django creates a "reverse"
    # accessor from Group back to User called `user_set`. This creates a name clash.
    #
    # The Solution: We provide a unique `related_name` to tell Django what to call the
    # reverse relationship from Group/Permission back to *our* custom User model.
    # This resolves the conflict.
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",  # A unique name for the reverse relationship
        blank=True,
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",  # Another unique name
        blank=True,
        verbose_name="user permissions",
    )

    # The Meta class allows us to configure model-specific options.
    class Meta:
        # Explicitly sets the name of the database table for this model.
        db_table = "users"
        # Sets the default ordering for when you query for users.
        # We order by `date_joined` in descending order (newest users first).
        # `date_joined` is a field provided by Django's AbstractUser.
        ordering = ["-date_joined"]

    # The __str__ method defines the human-readable representation of the object.
    # This is what you'll see in the Django admin or when you print a User object.
    def __str__(self):
        return self.email

# ==================== CLASS MODEL ====================
class Class(models.Model):
    """
    Represents a classroom or a group where users can collaborate.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=255)
    description = models.TextField()
    # A unique, user-friendly code that members can use to join the class.
    class_code = models.CharField(max_length=50, unique=True)

    # A foreign key to the User who created the class.
    # The `related_name` 'created_classes' allows us to easily query all classes
    # created by a specific user (e.g., `user.created_classes.all()`).
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_classes",
    )

    # Automatically records the timestamp when a class is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    # ManyToManyFields to the User model to define different roles within the class.
    # Each has a unique `related_name` to distinguish the relationships from the User's perspective.
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="joined_classes", blank=True
    )
    experts = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="expert_classes", blank=True
    )
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="admin_classes", blank=True
    )

    class Meta:
        db_table = "classes"
        ordering = ["-created_at"]
        # These names are used in the Django admin interface for better readability.
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.class_name


# ==================== VALIDATORS ====================
# Custom validation functions that can be applied to model fields.

def validate_future_date(value):
    """Ensures that the provided datetime value is in the future."""
    if value <= timezone.now():
        raise ValidationError("Due date must be in the future")


def validate_url(value):
    """A simple validator to check if a string looks like a basic URL."""
    if value and not value.startswith(("http://", "https://", "ftp://")):
        raise ValidationError("Invalid document URL")


# ==================== TASK MODEL ====================
class Task(models.Model):
    """
    Represents an assignment or task assigned within a Class.
    """
    # Defines a set of choices for the `status` field.
    # This provides a dropdown menu in the Django admin and validates the input.
    STATUS_CHOICES = [
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Links this task to the Class it belongs to.
    # The `related_name` 'tasks' allows access to all tasks for a class instance (e.g., `my_class.tasks.all()`).
    class_obj = models.ForeignKey(
        "Class",
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    # `auto_now=True` automatically updates this field to the current timestamp every time the model is saved.
    updated_at = models.DateTimeField(auto_now=True)

    # This field uses the custom `validate_future_date` validator.
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
    """
    Represents a user's submission for a specific Task.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    task= models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )

    submitted_at = models.DateTimeField(auto_now_add=True)

    document = models.URLField()

    user_upvotes = models.JSONField(default=list, blank=True)
    expert_upvotes = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "submissions"
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"Submission by {self.user.username} for {self.task.title}"


# ==================== FEEDBACK MODEL ====================
class Feedback(models.Model):
    """
    Represents feedback given by a user on a specific Submission.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    submission = models.ForeignKey(
        "Submission",
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )

    user = models.ForeignKey(
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
            f"Feedback by {self.user.username} on submission {self.submission.id}"
        )


# ==================== INVITATION MODEL ====================
class Invitation(models.Model):
    """
    Manages invitations for users to join a Class.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class_obj = models.ForeignKey(
        "Class",
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

    # Stores the email the invitation was sent to, which is useful
    # if the invited user is not yet registered.
    email = models.EmailField(validators=[EmailValidator()])

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    token = models.CharField(max_length=255, unique=True)
   
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invitations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation to {self.email} for {self.class_obj.class_name}"

