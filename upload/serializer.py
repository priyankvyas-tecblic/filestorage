from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .models import UploadFile,User
from .utils import Util
class UploadFileSerializer(ModelSerializer):
    class Meta:
        model = UploadFile
        fields = '__all__'
    def create(self, validated_data):
        instance = UploadFile(user = validated_data['user'])
        instance.file_name = validated_data['file_name']
        instance.file_path = validated_data['file_path']
        instance.save()
        return instance
        
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['email','user_name','password']

    def validate(self, attrs):
        email = attrs['email']
        if not email.split('@')[1] == 'tecblic.com':
            raise serializers.ValidationError({'EmailNotAllowed':'email only ending with tecblic.com is allowed'})
        return attrs
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        uid = urlsafe_base64_encode(force_bytes(user.id))
        print("uid=",uid)
        token = PasswordResetTokenGenerator().make_token(user)
        link = "http://localhost:8000/api/Verified/"+uid+'/'+token+'/'
        data = {
                'subject':"Account verification",
                'body':f'click Following Link for verified your Account {link}',
                'to_email':user.email
            }
        Util.send_email(data)
        return User
    
class UserLoginSerializer(serializers.Serializer):
  email = serializers.EmailField()
  password = serializers.CharField()

# class SendPasswordResetSerializer(serializers.Serializer):
#     email = serializers.EmailField(max_length=255)
#     class Meta:
#         fields = ['email']
#     def validate(self, attrs):
#         email = attrs.get('email')
#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uid = urlsafe_base64_encode(force_bytes(user.id))
#             print("uid=",uid)
#             token = PasswordResetTokenGenerator().make_token(user)
#             print("Password Reset token = ",token)
#             link = "http://localhost:8000/api/Verified/"+uid+'/'+token+'/'
#             print("Password Reset link = ",link)
#             data = {
#                 'subject':"Reset your password",
#                 'body':f'click Following Link for Reset your Password {link}',
#                 'to_email':user.email
#             }
#             Util.send_email(data)
#         else:
#             raise serializers.ValidationError('you are not a register user')
#         return attrs

class AccountVerifiedSerializer(serializers.Serializer):
    
    def validate(self, attrs):
        try:
            uid = self.context.get('uid')
            token = self.context.get('token')
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id= id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                raise serializers.ValidationError('Token is not valid or Expired')
            user.email_verified = True
            user.save()
            return super().validate(attrs)
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user,token)
            raise serializers.ValidationError('Token is not valid or Expired')
