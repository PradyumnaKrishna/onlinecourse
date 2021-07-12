from django.db import models
from django.conf import settings
from django.utils.timezone import now


# Instructor model
class Instructor(models.Model):
    """ instructor model """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField()

    def __str__(self):
        return self.user.username


# Learner model
class Learner(models.Model):
    """ learner model """
    STUDENT = 'STUDENT'
    DEVELOPER = 'DEVELOPER'
    DATA_SCIENTIST = 'DATA_SCIENTIST'
    DATABASE_ADMIN = 'DATABASE_ADMIN'

    OCCUPATION_CHOICES = [
        (STUDENT, 'Student'),
        (DEVELOPER, 'Developer'),
        (DATA_SCIENTIST, 'Data Scientist'),
        (DATABASE_ADMIN, 'Database Admin')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    occupation = models.CharField(
        null=False,
        max_length=20,
        choices=OCCUPATION_CHOICES,
        default=STUDENT
    )
    social_link = models.URLField(max_length=200)

    def __str__(self):
        return f'{self.user.username}, {self.occupation}'


# Course model
class Course(models.Model):
    """ course model """
    name = models.CharField(null=False, max_length=30, default='online course')
    image = models.ImageField(upload_to='course_images/')
    description = models.CharField(max_length=1000)
    pub_date = models.DateField(null=True)

    instructors = models.ManyToManyField(Instructor)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrollment'
    )

    total_enrollment = models.IntegerField(default=0)
    is_enrolled = False

    def __str__(self):
        return f"Name: {self.name}, Description: {self.description}"


# Lesson model
class Lesson(models.Model):
    """ lesson model """
    title = models.CharField(max_length=200, default="title")
    order = models.IntegerField(default=0)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField()


# Enrollment model
class Enrollment(models.Model):
    """ enrollment model """
    AUDIT = 'AUDIT'
    HONOR = 'HONOR'
    BETA = 'BETA'

    COURSE_MODES = [
        (AUDIT, 'Audit'),
        (HONOR, 'Honor'),
        (BETA, 'BETA')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date_enrolled = models.DateField(default=now)
    mode = models.CharField(max_length=5, choices=COURSE_MODES, default=AUDIT)
    rating = models.FloatField(default=5.0)


# Question model
class Question(models.Model):
    """ question model """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    text = models.CharField(max_length=150)
    grade = models.FloatField()

    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(
            is_correct=True,
            id__in=selected_ids
        ).count()

        return all_answers == selected_correct


# Choice model
class Choice(models.Model):
    """ choice model """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=150)
    is_correct = models.BooleanField()


# Submission model
class Submission(models.Model):
    """ submission model """
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    choices = models.ManyToManyField(Choice)
