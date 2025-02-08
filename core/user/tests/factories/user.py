# tests/factories/user.py
import factory
from factory.django import DjangoModelFactory
from core.user.models import User, UserInstitution, UserCourseInstance
from core.user.models.user import Roles

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f'{o.first_name.lower()}.{o.last_name.lower()}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
    role = Roles.STUDENT

    @factory.post_generation
    def institutions(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for institution in extracted:
            UserInstitution.objects.create(user=self, institution=institution)

    @factory.post_generation
    def courses(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        for course in extracted:
            UserCourseInstance.objects.create(user=self, course=course)

class UserInstitutionFactory(DjangoModelFactory):
    class Meta:
        model = UserInstitution

    user = factory.SubFactory(UserFactory)
    institution = factory.SubFactory('tests.factories.InstitutionFactory')
    start_date = factory.Faker('date_object')