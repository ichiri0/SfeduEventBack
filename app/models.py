from django.contrib.auth.models import User
from django.db import models


class Institute(models.Model):

    name = models.CharField(max_length=100, blank=False,
                            null=False, verbose_name="Наименование")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Институт"
        verbose_name_plural = "Институты"

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse("Institute_detail", kwargs={"pk": self.pk})


class Direction(models.Model):

    institute = models.ForeignKey(
        to=Institute, on_delete=models.CASCADE, verbose_name="Институт")
    name = models.CharField(max_length=100, blank=False,
                            null=False, verbose_name="Наименование")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self):
        return self.institute.name + ' ' + self.name

    # def get_absolute_url(self):
    #     return reverse("Institute_detail", kwargs={"pk": self.pk})


class Departament(models.Model):

    direction = models.ForeignKey(
        Direction, on_delete=models.CASCADE, verbose_name="Направление")
    name = models.CharField(max_length=100, blank=False,
                            null=False, verbose_name="Наименование")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"

    def __str__(self):
        return self.direction.name + ' ' + self.name

    # def get_absolute_url(self):
    #     return reverse("Institute_detail", kwargs={"pk": self.pk})


class GroupCourse(models.Model):

    course_stage = models.IntegerField(verbose_name="Номер курса")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return str(self.course_stage)

    # def get_absolute_url(self):
    #     return reverse("Institute_detail", kwargs={"pk": self.pk})


class Group(models.Model):

    departament = models.ForeignKey(
        Departament, on_delete=models.CASCADE, verbose_name="Кафедра")
    # group_name = models.CharField(max_length=100, blank=False, null=False)
    full_name = models.CharField(
        max_length=100, blank=False, null=False, verbose_name="Полное название")
    group_course = models.ForeignKey(
        to=GroupCourse, on_delete=models.CASCADE, verbose_name="Курс")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.departament.name + ' ' + self.full_name + ' ' + str(self.group_course.course_stage)

    # def get_absolute_url(self):
    #     return reverse("Institute_detail", kwargs={"pk": self.pk})


class Role(models.Model):
    name = models.CharField(max_length=30, blank=False,
                            null=False, verbose_name="Наименование")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")

    is_can_post_event = models.BooleanField(
        default=False, verbose_name="Может создавать мероприятия")

    class Meta:
        verbose_name = "Роль"
        verbose_name_plural = "Роли"

    def __str__(self):
        return self.name


class UserProfile(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь")
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, verbose_name="Роль")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"{self.user.username} {self.user.email} {self.user.first_name} {self.user.last_name} {self.role.name}"


class Event(models.Model):
    organizator = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, blank=False,
                            null=False, verbose_name="Наименование")
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание")
    latitude = models.FloatField(null=True, blank=True, verbose_name="Широта")
    longitude = models.FloatField(
        null=True, blank=True, verbose_name="Долгота")

    datetime_of_event = models.DateTimeField(
        verbose_name="Дата и время проведения", null=True, blank=True)

    image = models.ImageField(
        verbose_name="Фото", upload_to='events/', null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return self.name
