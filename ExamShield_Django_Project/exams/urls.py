from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("exam/<int:exam_id>/start/", views.start_exam, name="start_exam"),
    path("attempt/<int:attempt_id>/", views.take_exam, name="take_exam"),
    path("attempt/<int:attempt_id>/submit/", views.submit_exam, name="submit_exam"),
    path("results/", views.results, name="results"),
    path("result/<int:attempt_id>/", views.result_detail, name="result_detail"),
]
