from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserSkills, JobRole, Career, SKILL_LEVEL_CHOICES
from .ml_model import predict_careers
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def home(request):
    return render(request, 'advisor/home.html')

def about(request):
    return render(request, 'advisor/about.html')

def contact(request):
    return render(request, 'advisor/contact.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('home')  # Redirect to the home page or dashboard
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

@login_required
@login_required
def skills_assessment(request):
    if request.method == 'POST':
        # Collect only selected skills
        selected_skills = {}
        for field in [
            'database_fundamentals',
            'computer_architecture',
            'distributed_computing_systems',
            'cyber_security',
            'networking',
            'software_development',
            'programming_skills',
            'project_management',
            'computer_forensics_fundamentals',
            'technical_communication',
            'ai_ml',
            'software_engineering',
            'business_analysis',
            'communication_skills',
            'data_science',
            'troubleshooting_skills',
            'graphics_designing'
        ]:
            value = request.POST.get(field)
            if value:  # Only include if user selected it
                selected_skills[field] = int(value)

        # Save UserSkills with defaults (0 for missing ones)
        skills = UserSkills(user=request.user, **{f: selected_skills.get(f, 0) for f in selected_skills})
        skills.save()

        # Run predictions on selected skills
        predictions = predict_careers(skills)

        # Get job roles in the order of predictions
        jobs = JobRole.objects.filter(title__in=predictions)

        context = {
            'predictions': predictions,
            'jobs': jobs,
            'selected_skills': selected_skills
        }

        return render(request, 'advisor/results.html', context)

    return render(request, 'advisor/assessment.html', {'SKILL_LEVEL_CHOICES': SKILL_LEVEL_CHOICES})


def knowledge_page(request):
    """
    View to display the knowledge page with career options, job roles, and relevant information.
    """
    try:
        careers = Career.objects.all()
        job_roles = JobRole.objects.all()
    except Career.DoesNotExist or JobRole.DoesNotExist:
        raise Http404("Knowledge content not found")

    context = {
        'careers': careers,
        'job_roles': job_roles,
        'skill_levels': SKILL_LEVEL_CHOICES,  
    }

    return render(request, 'advisor/knowledge_page.html', context)

def job_details(request, job_id):
    try:
        job = JobRole.objects.get(id=job_id)
        return render(request, 'advisor/job_details.html', {'job': job})
    except JobRole.DoesNotExist:
        return redirect('home')
def feedback_view(request):
    return render(request, 'advisor/feedback.html')

def mock_test(request):
    return render(request, 'advisor/mock_test.html')
