from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic

from .models import Course, Enrollment, Submission
from . import utils


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )

    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        existing_user = User.objects.filter(username=username).first()

        if not existing_user:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            login(request, user)
            return redirect("onlinecourse:index")

        context['message'] = "User already exists."
        return render(
            request,
            'onlinecourse/user_registration_bootstrap.html',
            context
        )


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')

        context['message'] = "Invalid username or password."
        return render(
            request,
            'onlinecourse/user_login_bootstrap.html',
            context
        )

    return render(
        request,
        'onlinecourse/user_login_bootstrap.html',
        context
    )


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = utils.check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = utils.check_if_enrolled(user, course)
    if user.is_authenticated:
        if not is_enrolled:
            # Create an enrollment
            Enrollment.objects.create(user=user, course=course, mode='honor')
            course.total_enrollment += 1
            course.save()

        return HttpResponseRedirect(reverse(
            viewname='onlinecourse:course_details',
            args=(course.id,)
        ))

    return redirect('onlinecourse:login')


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = utils.check_if_enrolled(user, course)
    if user.is_authenticated:
        if is_enrolled:
            enrollment = Enrollment.objects.get(user=user, course=course)
            submission = Submission.objects.create(enrollment=enrollment)

            submitted_answers = [
                int(value)
                for key, value in request.POST.items()
                if key.startswith('choice')
            ]
            submission.choices.add(*submitted_answers)

            return HttpResponseRedirect(reverse(
                viewname='onlinecourse:show_exam_result',
                args=(course.id, submission.id,)
            ))

        return HttpResponseRedirect(reverse(
            viewname='onlinecourse:enroll',
            args=(course.id,)
        ))

    return redirect('onlinecourse:login')


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    choices = submission.choices.all()

    total_score, score = 0, 0
    for question in course.question_set.all():
        total_score += question.grade
        if question.is_get_score(choices):
            score += question.grade

    context = {
        "course": course,
        "choices": choices,
        "grade": int(score / total_score * 100),
    }

    return render(
        request,
        'onlinecourse/exam_result_bootstrap.html',
        context
    )
