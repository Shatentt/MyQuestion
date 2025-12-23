from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from app.models import Answer, Profile, Question, Tag


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user = auth.authenticate(self.request, username=username, password=password)
            
            if self.user is None:
                raise forms.ValidationError("Invalid username and/or password!", code='invalid_login')
        return cleaned_data
    
    def get_user(self):
        return self.user

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, max_length=30, label="Display Name")
    repeat_password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")

        if password and repeat_password and password != repeat_password:
            self.add_error('repeat_password', "Passwords do not match")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
            Profile.objects.create(
                user=user, 
                avatar=self.cleaned_data.get('avatar')
            )
            
        return user

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(required=False, label="Tags", widget=forms.TextInput())
    
    class Meta:
        model = Question
        fields = ['title', 'text']

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags')
        if not raw_tags:
            return []
        
        tag_names = [t.strip() for t in raw_tags.split() if t.strip()]
        return tag_names

    def save(self, user=None, commit=True):
        question = super().save(commit=False)
        
        if user:
            question.user = user
            
        if commit:
            question.save()
            tag_names = self.cleaned_data.get('tags')
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
                
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'answer_input', 'placeholder': 'Enter your answer here...'})
        }

class SettingsForm(forms.ModelForm):
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'single-line_input field_input'}))
    username = forms.CharField(label="Login", widget=forms.TextInput(attrs={'class': 'single-line_input field_input'}))
    first_name = forms.CharField(label="NickName", required=False, widget=forms.TextInput(attrs={'class': 'single-line_input field_input'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.profile.avatar:
            self.fields['avatar'].initial = self.instance.profile.avatar

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        
        if email and User.objects.filter(email__iexact=email).exclude(username=self.instance.username).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        
        avatar = self.cleaned_data.get('avatar')
        
        if avatar:
            user.profile.avatar = avatar
            user.profile.save()
        
        return user