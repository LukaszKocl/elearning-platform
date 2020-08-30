from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import Group
from django.views import View
from django.urls import reverse
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Category, Course, CourseDetail, Order, User, Permission
import datetime
from elearning import forms

# Create your views here.
class Index(View):
    def get(self, request):
        user = request.user
        courses = None

        if user.is_authenticated:
            user = User.objects.get(pk=user.id)
            courses = Course.objects.filter(order__id=user.id, order_course__is_paid=True)
            group = user.groups.all()

            request.session["group"] = group[0].id
            request.session["super_user"] = user.is_superuser

        categories = Category.objects.all()

        return render(request, "index.html", {'categories': categories,
                                              "courses": courses,
                                              "group": request.session.get("group"),
                                              "superuser":request.session.get("super_user")})

class MyLoginView(LoginView):
    authentication_form = forms.CustomAuthenticationForm
    form_class = forms.CustomAuthenticationForm


class RegistrationUserView(View):
    def get(self, request):
        form = forms.UserRegistrationForm()
        return render(request, "rejestracja.html", {"form":form})

    def post(self, request):
        form = forms.UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(
                form.cleaned_data['password'])
            new_user.save()

            group = Group.objects.get(pk=2)
            new_user.groups.add(group)
            return render(request,
                          'registration/register_done.html',
                          {'new_user': new_user})

        form = forms.UserRegistrationForm()
        return render(request, "rejestracja.html", {"form": form})


class AddCategoryView(PermissionRequiredMixin, View):
    permission_required = 'elearning.add_category'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"


    def get(self, request):
        form = forms.CategoryForm()
        category = Category.objects.all()

        return render(request, "form.html", {
                "form": form,
                "button_text":"Dodaj kategorię",
                "categories": category,
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                })

    def post(self, request):
        form = forms.CategoryForm(request.POST)
        category = Category.objects.all()

        if form.is_valid():
            form.save()

            return redirect(reverse("index"))
        return render(request, "form.html", {
                    "form": form,
                    "button_text": "Dodaj kategorię",
                    "categories": category,
                    "group": request.session.get("group"),
                    "superuser": request.session.get("super_user"),
                    })

class EditCategoryView(PermissionRequiredMixin,View):
    permission_required = 'elearning.change_category'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        category = get_object_or_404(Category, pk=id)
        form = forms.CategoryForm(instance=category)
        categories = Category.objects.all()

        return render(request, "form.html", {
                    "form": form,
                    "button_text": "Modyfikuj kategorię",
                    "categories": categories,
                    "group": request.session.get("group"),
                    "superuser": request.session.get("super_user"),
                    })

    def post(self, request, id):
        category = Category.objects.get(pk=id)
        form = forms.CategoryForm(request.POST, instance=category)
        category = Category.objects.all()

        if form.is_valid():
            form.save()
            return redirect(reverse("index"))

        return render(request, "form.html", {
                "form": form,
                "button_text": "Modyfikuj kategorię",
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                "categories": category
            })

class DeleteCategoryView(PermissionRequiredMixin, View):
    permission_required = 'elearning.delete_category'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        category = Category.objects.get(pk=id)
        category.delete()
        return redirect(reverse("index"))

class ListCourseView(View):
    def get(self, request, id):
        course = Course.objects.filter(category_id=id)
        category = Category.objects.all()
        user = request.user
        tutor_courses = None

        if user.is_authenticated:
            tutor_courses = Course.objects.filter(tutor=user)

        return render(request, "course.html", {
                "courses": course,
                "categories": category,
                "tutor_courses": tutor_courses,
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                "id_course": id,
                })

class ActivateCourseView(LoginRequiredMixin, View):
    def get(self, request, id):
        current_time = datetime.datetime.now()
        course = Course.objects.get(pk=id)

        Order.objects.create(user=request.user,
                            course=course,
                            start_date=current_time,
                            end_date=current_time + datetime.timedelta(days=365),
                            price=course.price,
                            vat=round(float(course.price) * 1.23, 2),
                            is_paid=False)

        return redirect('index')

class AddCourseView(PermissionRequiredMixin,View):
    permission_required = 'elearning.add_course'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request):
        form = None
        category = Category.objects.all()

        if request.session.get("super_user", False):
            form = forms.AddCourseAdminForm()
        else:
            form = forms.AddCourseTutorForm()

        return render(request, "form.html", {
                "form":form,
                "categories":category,
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                "button_text":"Dodaj kurs"})

    def post(self, request):
        form = None
        category = Category.objects.all()

        if request.session.get("super_user", False):
            form = forms.AddCourseAdminForm(request.POST)
        else:
            form = forms.AddCourseTutorForm(request.POST)

        if form.is_valid():
            if request.session.get("super_user", False):
                form.save()
            else:
                course = form.save(commit=False)
                course.tutor = User.objects.get(pk=request.user.id)
                course.save()
                form.save_m2m()

            return redirect(reverse("index"))

        return render(request, "form.html", {
                "form": form,
                "categories": category,
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                "button_text": "Dodaj kurs"})


class EditCourseView(PermissionRequiredMixin, View):
    permission_required = 'elearning.change_course'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        form = None
        course = Course.objects.get(pk=id)
        category = Category.objects.all()

        if request.session.get("super_user", False):
            form = forms.EditCourseAdminForm(instance=course)
        else:
            form = forms.EditCourseTutorForm(instance=course)

        return render(request, "form.html", {
                "form": form,
                "categories":category,
                "group": request.session.get("group"),
                "superuser": request.session.get("super_user"),
                "button_text": "Modyfikuj kurs",
        })

    def post(self, request, id):
        form = None
        course = Course.objects.get(pk=id)
        category = Category.objects.all()

        if request.session.get("super_user", False):
            form = forms.EditCourseAdminForm(request.POST, instance=course)
        else:
            form = forms.EditCourseTutorForm(request.POST, instance=course)

        if form.is_valid():
            if request.session.get("super_user", False):
                form.save()
            else:
                course_edit = form.save(commit=False)
                course_edit.tutor = User.objects.get(pk=request.user.id)
                course_edit.category = course.category
                course_edit.save()
                form.save_m2m()

            return redirect(reverse("course-list", args=[course.category_id]))
        return render(request, "form.html", {
                            "form": form,
                            "categories": category,
                            "group": request.session.get("group"),
                            "superuser": request.session.get("super_user"),
                            "button_text": "Modyfikuj kurs",
                        })

class DeleteCourseView(PermissionRequiredMixin, View):
    permission_required = 'elearning.change_course'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        course = Course.objects.get(pk=id)
        course.delete()
        return redirect(reverse("course-list", args=[course.category_id]))

class CourseDetailView(View):
    def get(self, request, id):
        module = CourseDetail.objects.filter(course_id=id)
        user = request.user
        order = 0
        tutor_course = None

        if user.is_authenticated:
            order = Order.objects.filter(course_id=id, user_id=user.id, is_paid=True).count()
            tutor_course = Course.objects.filter(tutor=user, id=id)

        return render(request, "coursedetail.html", {
            "modules": module,
            "order": order,
            "tutor_course": tutor_course,
            "group": request.session.get("group"),
            "superuser": request.session.get("super_user")
            })


class CourseVideoView(LoginRequiredMixin, View):
    def get(self, request, course_id, video_id):
        order = 0
        tutor_course = None
        video_number = None
        user = request.user

        if user.is_superuser:
            video_number = CourseDetail.objects.filter(pk=video_id)
        else:
            video_number = CourseDetail.objects.filter(pk=video_id, course__order__id=user.id)

        tutor_course = Course.objects.filter(tutor=user, id=course_id)

        if tutor_course.count() > 0:
            video_number = tutor_course[0].coursedetail_set.filter(id=video_id)

        order = Order.objects.filter(course_id=course_id, user_id=user.id, is_paid=True).count()
        module = CourseDetail.objects.filter(course_id=course_id)

        return render(request, "coursedetail.html", {
            "modules": module,
            "order": order,
            "tutor_course": tutor_course,
            "video_number": video_number,
            "group": request.session.get("group"),
            "superuser": request.session.get("super_user")
            })

class AddCourseDetailView(PermissionRequiredMixin, View):
    permission_required = 'elearning.add_coursedetail'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        form = forms.AddCourseDetailForm()
        category = Category.objects.all()
        course = Course.objects.get(pk=id)
        module = CourseDetail.objects.filter(course_id=id)

        return render(request, "form_video.html", {
                        "form": form,
                        "categories": category,
                        "course": course.name,
                        "modules": module,
                        "group": request.session.get("group"),
                        "superuser": request.session.get("super_user"),
                        "button_text":"Dodaj moduł"})

    def post(self, request, id):
        form = forms.AddCourseDetailForm(request.POST, request.FILES)
        course = Course.objects.get(pk=id)
        category = Category.objects.all()
        module = CourseDetail.objects.filter(course_id=id)

        if form.is_valid():
            title = form.cleaned_data["title"]
            file = form.cleaned_data["file"]
            is_free = form.cleaned_data["is_free"]

            CourseDetail.objects.create(title=title,
                                  file=file,
                                  is_free=is_free,
                                  created=datetime.datetime.now(),
                                  course=course)

            return redirect(reverse("course-detail-add", args=[course.id]))

        return render(request, "form_video.html", {
                        "form": form,
                        "categories": category,
                        "course": course.name,
                        "modules": module,
                        "group": request.session.get("group"),
                        "superuser": request.session.get("super_user"),
                        "button_text": "Dodaj moduł"
                        })


class EditCourseDetailView(PermissionRequiredMixin, View):
    permission_required = 'elearning.change_coursedetail'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        category = Category.objects.all()
        module = CourseDetail.objects.get(pk=id)
        modules = CourseDetail.objects.filter(course_id=module.course_id)
        form = forms.EditCourseDetailForm(model_to_dict(module))

        return render(request, "form_video.html", {
                    "form": form,
                    "categories": category,
                    "modules": modules,
                    "module": module,
                    "course": module.course.name,
                    "group": request.session.get("group"),
                    "superuser": request.session.get("super_user"),
                    "button_text": "Modyfikuj moduł kursu"
                })

    def post(self, request,id):
        category = Category.objects.all()
        module = CourseDetail.objects.get(pk=id)
        modules = CourseDetail.objects.filter(course_id=module.course_id)
        form = forms.EditCourseDetailForm(request.POST, request.FILES)

        if form.is_valid():
            module.title = form.cleaned_data['title']
            module.is_free = form.cleaned_data['is_free']
            if form.cleaned_data['file']:
                module.file = form.cleaned_data['file']

            module.save()
            return redirect(reverse('course-video', args=[module.course_id,module.id]))


        return render(request, "form_video.html", {
                    "form": form,
                    "categories": category,
                    "modules": modules,
                    "module": module,
                    "course": module.course.name,
                    "group": request.session.get("group"),
                    "superuser": request.session.get("super_user"),
                    "button_text": "Modyfikuj moduł kursu"
                })

class DeleteCourseDetailView(PermissionRequiredMixin, View):
    permission_required = 'elearning.delete_coursedetail'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        module = CourseDetail.objects.get(pk=id)
        category_id = module.course_id
        module.delete()
        return redirect(reverse("course-detail-list", args=[category_id]))


class AddOrderView(View):
    def get(self, request):
        form = forms.OrderForm()

        return render(request, "form.html", {"form": form, "button_text": "Dodaj zamówienie"})

    def post(self, request):
        form = forms.OrderForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            course = form.cleaned_data["course"]
            start_date = User.objects.get("start_date")
            end_date = form.cleaned_data["end_date"]
            price = form.cleaned_data["price"]
            vat = form.cleaned_data["vat"]
            is_paid = form.cleaned_data["is_paid"]

            Order.objects.create(user=user,
                                  course=course,
                                  start_date=start_date,
                                  end_date=end_date,
                                  price=price,
                                  vat=vat,
                                  is_paid=is_paid)

            return redirect(reverse("index"))
        return render(request, "form.html", {
                    "form": form, "button_text": "Dodaj zamówienie"})

class EditOrderView(PermissionRequiredMixin, View):
    permission_required = 'elearning.change_order'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        order = Order.objects.get(pk=id)
        category = Category.objects.all()

        form = forms.OrderFormAdmin(initial={
            "user": order.user,
            "course": order.course,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "gross_price": order.gross_price(),
            "is_paid": order.is_paid
        })

        return render(request, "form.html", {
                        "form": form,
                        "button_text": "Edytuj zamówienie",
                        "group": request.session.get("group"),
                        "superuser": request.session.get("super_user"),
                        "categories": category})

    def post(self, request, id):
        form = forms.OrderFormAdmin(request.POST)
        category = Category.objects.all()

        if form.is_valid():
            order = Order.objects.get(pk=id)
            order.end_date = form.cleaned_data["end_date"]
            order.is_paid = form.cleaned_data["is_paid"]

            order.save()
            return redirect(reverse("order-history-admin"))

        return render(request, "form.html", {
            "form": form,
            "button_text": "Edytuj zamówienie",
            "group": request.session.get("group"),
            "superuser": request.session.get("super_user"),
            "categories": category})


class DeleteOrderView(PermissionRequiredMixin, View):
    permission_required = 'elearning.delete_order'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        order = Order.objects.get(pk=id)
        order.delete()
        return redirect(reverse("order-history-admin"))

class HistoryOrderPupilView(PermissionRequiredMixin, View):
    permission_required = 'elearning.view_order'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request):
        orders = Order.objects.filter(user_id=request.user.id)
        category = Category.objects.all()

        return render(request, "orderHistory.html", {
                    "orders": orders,
                    "categories": category,
                    "group": request.session.get("group"),
                    "superuser": request.session.get("super_user"),
                    })

class HistoryOrderAdminlView(PermissionRequiredMixin, View):
    permission_required = 'elearning.admin_order'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request):
        orders = Order.objects.all()
        category = Category.objects.all()

        return render(request, "orderHistory.html", {
                            "orders": orders,
                            "categories": category,
                            "group": request.session.get("group"),
                            "superuser": request.session.get("super_user")
                            })

class ProfileView(PermissionRequiredMixin, View):
    permission_required = 'auth.change_user'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        category = Category.objects.all()
        form = forms.EditProfileForm(instance=user)

        return render(request, "form.html", {
                            "form": form,
                            "categories": category,
                            "button_text": "Modyfikuj",
                            "group": request.session.get("group"),
                            "superuser": request.session.get("super_user"),
                            })

    def post(self, request):
        category = Category.objects.all()
        user = User.objects.get(pk=request.user.id)
        form = forms.EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            if form.cleaned_data['password']:
                new_user = form.save(commit=False)
                new_user.set_password(
                    form.cleaned_data['password'])
                new_user.save()
                update_session_auth_hash(request, new_user)
            else:
                form.save()

            return redirect(reverse('index'))

        return render(request, "form.html", {
            "form": form,
            "categories": category,
            "group": request.session.get("group"),
            "superuser": request.session.get("super_user"),
            "button_text": "Modyfikuj",
        })


class EditUserView(PermissionRequiredMixin, View):
    permission_required = 'auth.admin_edit_user'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        user = User.objects.get(pk=id)
        category = Category.objects.all()
        form = forms.EditProfileForm(instance=user)

        return render(request, "form.html", {
                            "form": form,
                            "categories": category,
                            "button_text": "Modyfikuj",
                            "group": request.session.get("group"),
                            "superuser": request.session.get("super_user"),
                            })

    def post(self, request, id):
        category = Category.objects.all()
        user = User.objects.get(pk=id)
        form = forms.EditProfileForm(request.POST, instance=user)

        if form.is_valid():
            if form.cleaned_data['password']:
                new_user = form.save(commit=False)
                new_user.set_password(
                    form.cleaned_data['password'])
                new_user.save()
                update_session_auth_hash(request, new_user)
            else:
                form.save()

            return redirect(reverse('index'))

        return render(request, "form.html", {
            "form": form,
            "categories": category,
            "group": request.session.get("group"),
            "superuser": request.session.get("super_user"),
            "button_text": "Modyfikuj",
        })


class ListUsersView(PermissionRequiredMixin, View):
    permission_required = 'auth.view_user'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request):
        users = User.objects.filter().exclude(is_superuser=True)
        category = Category.objects.all()

        return render(request, "userLists.html", {
                            "categories": category,
                            "users":users,
                            "group": request.session.get("group"),
                            "superuser": request.session.get("super_user"),
                            "button_text": "Modyfikuj",
                            })

class DeleteUserView(PermissionRequiredMixin, View):
    permission_required = 'auth.delete_user'
    redirect_field_name = None
    permission_denied_message = "Dostęp zabroniony"

    def get(self, request, id):
        user = User.objects.get(pk=id)
        user.delete()
        return redirect(reverse("user-list"))
