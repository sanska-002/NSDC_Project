# ExamShield — Online Exam Taking System

A compact Django full-stack project for timed multiple-choice exams, automatic scoring, results, and best-effort tab-switch submission.

## Features
- Public list of published exams.
- Student login using Django authentication.
- Admin-created exams and multiple-choice questions.
- Timed attempt with countdown.
- Best-effort auto-submit when the exam tab becomes hidden.
- Server-side scoring and result history.
- Admin view of attempts and answers.
- Responsive Bootstrap-based UI.

## Quick start (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py makemigrations exams
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/ for the student site and http://127.0.0.1:8000/admin/ for administration.

## Create an exam
1. Log into `/admin/` with the superuser account.
2. Add an Exam, set duration, and tick `is_published`.
3. Add Questions inline. Each question needs four options, one correct option, and marks.
4. Create a separate student user from Django admin (or use the built-in user management).
5. Log in as the student, open the exam, and start.

## Important anti-cheating limitation
The browser's `visibilitychange` event detects when the document becomes hidden in common tab-switch/minimize cases. It cannot reliably detect every application switch, browser/tool interaction, a second device, developer tools, or a modified client. Network loss or force-closing the browser can also prevent the browser from receiving a submission confirmation. Server-side time checks and scoring are authoritative, but this is not a high-stakes proctoring system.

For real examinations, use supervised testing, randomized question/option order, server-side attempt limits, audit logs, and a purpose-built proctoring solution with explicit consent and privacy safeguards. Do not promise that cheating is impossible.

## Before production
- Replace the development `SECRET_KEY` with an environment variable.
- Set `DEBUG=False` and configure `ALLOWED_HOSTS`.
- Configure HTTPS, secure cookies, logging, backups, rate limits, and email-based password reset.
- Review privacy, retention, and accessibility requirements.
- Add tests and run `python manage.py test`.

## Scope
This is a fast-start educational project. It does not include webcam monitoring, live proctoring, advanced question types, or real-time invigilator tools.
