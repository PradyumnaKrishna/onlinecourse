from .models import Enrollment


def check_if_enrolled(user, course):
    if user.id is not None:
        if Enrollment.objects.filter(user=user, course=course).first():
            return True

    return False
