from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class UserAccount(models.Model):
    ROLE_CHOICES = [
        ('full_admin', 'Full Admin'),
        ('basic_admin', 'Basic Admin'),
        ('advanced_admin', 'Advanced Admin'),
        ('hr_manager', 'HR Manager'),
        ('recruiter', 'Recruiter'),
    ]

    PERMISSION_CHOICES = [(i, str(i)) for i in range(1, 11)]  # 1 to 10

    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permission = models.IntegerField(choices=PERMISSION_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(10)])
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"