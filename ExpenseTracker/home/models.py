from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

SELECT_CATEGORY_CHOICES = [
    ("Food", "Food"),
    ("Travel", "Travel"),
    ("Shopping", "Shopping"),
    ("Necessities", "Necessities"),
    ("Entertainment", "Entertainment"),
    ("Other", "Other")
]

ADD_EXPENSE_CHOICES = [
    ("Expense", "Expense"),
    ("Income", "Income")
]

class Addmoney_info(models.Model):
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    add_money = models.CharField(max_length=10, choices=ADD_EXPENSE_CHOICES)
    quantity = models.BigIntegerField()
    Date = models.DateField(default=now)
    Category = models.CharField(max_length=20, choices=SELECT_CATEGORY_CHOICES, default='Food')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'addmoney'
