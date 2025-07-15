from rest_framework import serializers
from .models import Lesson

from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data['role'],
            age=validated_data['age'],
            subject=validated_data['subject'],
            points=validated_data['role'],
            phone=validated_data['phone']
        )
        return user
    

# Serializer that converts Lesson model instances to JSON and vice versa,
# enabling creation, retrieval, and update of lessons through the API
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

