from django import forms
from .models import User, Category, Order, Course
from django.contrib.auth.forms import AuthenticationForm
from django.forms import ModelChoiceField

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        error_messages = {
            'slug': {"invalid":"Należy wprowadzić polskie litery oraz usnąć znaki spacji"}
        }

class CategoryForm2(forms.Form):
    name = forms.CharField(max_length=50, label="Nazwa kategorii")
    slug = forms.SlugField(label="Slug", error_messages={"invalid":"Należy wprowadzić polskie litery"})

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=100, label="Nazwa profilu")
    company_name = forms.CharField(max_length=200, label="Nazwa firmy")
    vat_number = forms.CharField(max_length=10, label="VAT")
    mailing = forms.BooleanField(label="Zgoda na otrzymywanie maili")

class EditCourseTutorForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label="Kategoira", disabled=True, required=False)

    class Meta:
        model = Course
        exclude =['order', 'tutor']

    def clean(self):
        self.cleaned_data["tutor"] = 2
        self.cleaned_data["category"] = Category.objects.get(pk=1)
        return self.cleaned_data

class EditCourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude =['order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tutor'].queryset = User.objects.filter(groups__name="tutor")

class AddCourseTutorForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['order','tutor']

    def clean(self):
        self.cleaned_data["tutor"] = 2
        return self.cleaned_data

class AddCourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ['order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tutor'].queryset = User.objects.filter(groups__name="tutor")

class AddCourseDetailForm(forms.Form):
    title = forms.CharField(max_length=100, label="Nazwa modołu kursu")
    file = forms.FileField(label="Plik z nagraniem")
    is_free = forms.BooleanField(label="Czy moduł dostępny jest bez opłaty", initial=False, required=False)

class EditCourseDetailForm(forms.Form):
    title = forms.CharField(max_length=100, label="Nazwa modołu kursu")
    file = forms.FileField(label="Plik z nagraniem", required=False)
    is_free = forms.BooleanField(label="Czy moduł dostępny jest bez opłaty", initial=False, required=False)

class DateInput(forms.DateInput):
    input_type = "date"


class OrderFormAdmin(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Kursant", disabled=True, required=False)
    course = forms.ModelChoiceField(queryset=Course.objects.all(), label="Kurs", disabled=True, required=False)
    start_date = forms.DateField(widget=DateInput, label="Początek kursu", disabled=True, required=False)
    end_date = forms.DateField(widget=DateInput, label="Koniec kursu")
    gross_price = forms.DecimalField(disabled=True, label="Cena kursu", required=False)
    is_paid = forms.BooleanField(label="Czy kurs został opłacony", required=False)


class EditProfileForm(forms.ModelForm):
    password = forms.CharField(label='Hasło',
                               widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Powtórz hasło',
                                widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name','email']
        labels = {"first_name": "Imię", "last_name": "Nazwisko", "email": "Adres mailowy"}


    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Podane hasła nie są takie same.')
        return cd['password2']



class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': (
            "Niepoprawny login"
        ),
        'inactive': ("Konoto jest nieaktywne."),
    }

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Użytkownik'
        self.fields['password'].label = 'Hasło'

    class Meta:
        labels = {'username': 'Użytkownik', 'password': 'Hasło'}

class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(label="Login")
    password = forms.CharField(label='Hasło',
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Powtórz hasło',
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username','email']
        labels = {"first_name":"Imię", "last_name":"Nazwisko","email":"Adres mailowy"}

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Podane hasła nie są takie same.')
        return cd['password2']
