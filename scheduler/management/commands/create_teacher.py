from django.core.management.base import BaseCommand
from scheduler.models import User

class Command(BaseCommand):
    help = 'Create a teacher user'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the teacher')
        parser.add_argument('--email', type=str, help='Email for the teacher')
        parser.add_argument('--password', type=str, help='Password for the teacher')
        parser.add_argument('--first_name', type=str, help='First name for the teacher')
        parser.add_argument('--last_name', type=str, help='Last name for the teacher')
        parser.add_argument('--subject', type=str, help='Subject the teacher teaches')
        parser.add_argument('--age', type=int, help='Age of the teacher', default=30)
        parser.add_argument('--phone', type=int, help='Phone number', default=0)

    def handle(self, *args, **options):
        username = options['username'] or 'teacher1'
        email = options['email'] or 'teacher@example.com'
        password = options['password'] or 'teacherpass123'
        first_name = options['first_name'] or 'John'
        last_name = options['last_name'] or 'Doe'
        subject = options['subject'] or 'Mathematics'
        age = options['age']
        phone = options['phone']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'User "{username}" already exists!')
            )
            return

        # Create the teacher user
        teacher = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='teacher',
            age=age,
            subject=subject,
            phone=phone
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created teacher user "{username}"')
        )
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Subject: {subject}')
        self.stdout.write(f'Role: {teacher.role}')
