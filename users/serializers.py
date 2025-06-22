from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import Group, Permission



""" ###############################################################################
########################-User Registration Serializer-#########################
############################################################################### """


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this mail already exist.")
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        if not email:
            raise serializers.ValidationError("L'email est requis.")
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password']) 

        user.save()
        return user


""" ###############################################################################
##############################-Groupe Serializer-##############################
############################################################################### """

class UserMappingDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'email']


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']  


class GroupSerializer(serializers.ModelSerializer):
    # users = UserMappingDataSerializer(
    #     many=True,
    #     read_only=True,  
    #     source='user_set'  
    # )
    permissions = PermissionSerializer(many=True, read_only=True)  

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions'] 



""" ###############################################################################
###############################-User Serializer-###############################
############################################################################### """


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,  
        queryset=Group.objects.all(),
        slug_field='name'  
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'groups']


""" ###############################################################################
#########################-Change Password Serializer-##########################
############################################################################### """


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("Your old password and your new password can't be the same.")
        return data


""" ###############################################################################
#########################-Reset Password Serializer-###########################
############################################################################### """


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data


""" ###############################################################################
##########################-Custom Token Serializer-############################
############################################################################### """

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        return data