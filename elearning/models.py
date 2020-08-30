from django.db import models
from django.contrib.auth.models import User, Permission, Group

# Create your models here.

class Profile(models.Model):
    name = models.CharField(max_length=100)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=200, null=True)
    vat_number = models.CharField(max_length=10, null=True)
    mailing = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nazwa kategorii")
    slug = models.SlugField(verbose_name="Slug")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']

class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nazwa kursu")
    description = models.TextField(verbose_name="Opis kursu")
    tutor = models.ForeignKey(User, related_name='course_tutor', on_delete=models.CASCADE, verbose_name="Prowadzący")
    price = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Cena netto kursu")
    is_active = models.BooleanField(default=True, verbose_name="Czy kurs jest aktywny")
    category = models.ForeignKey(Category, related_name="course_category", on_delete=models.CASCADE, verbose_name="Kategoria")
    order = models.ManyToManyField(User, related_name="course_user", through='Order')
    #order_set    course.order_set.all()

    def __str__(self):
        return f"{self.name}"


def video_directory_path(instance, filename):
    return 'kurs_{0}/{1}'.format(instance.course.name, filename).replace(" ","_")

class CourseDetail(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to=video_directory_path)
    is_free = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"{self.title}"

class Order(models.Model):
    user = models.ForeignKey(User, related_name="order_user", on_delete=models.CASCADE, verbose_name="Kursant")
    course = models.ForeignKey(Course, related_name="order_course", on_delete=models.CASCADE, verbose_name="Kurs")
    start_date = models.DateField(verbose_name="Początek kursu")
    end_date = models.DateField(verbose_name="Koniec Kursu")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    vat = models.DecimalField(max_digits=6, decimal_places=2)
    is_paid = models.BooleanField(default=False, verbose_name="Czy zapłacone")

    def gross_price(self):
        return self.price + self.vat


