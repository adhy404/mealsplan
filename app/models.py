from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


# ---------------- CATEGORY ----------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            # ✅ ensure UNIQUE slug
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="recipes")

    title = models.CharField(max_length=200)
    description = models.TextField()

    image = models.ImageField(upload_to='recipes/', blank=True, null=True)

    ingredients = models.TextField(blank=True)
    steps = models.TextField(blank=True)

    cooking_time = models.IntegerField(blank=True, null=True)
    servings = models.IntegerField(blank=True, null=True)

    is_premium = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# ---------------- FAVORITE ----------------
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ❤️ {self.recipe.title}"


# ---------------- RATING ----------------
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    value = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title} ({self.value})"


# ---------------- PROFILE ----------------
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


# ---------------- MEAL PLAN ----------------
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ---------------- MEAL PLAN ITEMS ----------------
class MealPlanItem(models.Model):
    plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Lunch', 'Lunch'),
        ('Dinner', 'Dinner'),
    ]

    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)

    def __str__(self):
        return f"{self.plan.name} - {self.day} - {self.meal_type}"