from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UploadFileSerializer,UserSerializer,UserLoginSerializer,AccountVerifiedSerializer
from .models import UploadFile
import os
from .utils import get_tokens_for_user
import mimetypes
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import HttpResponse, Http404
from rest_framework import status
from math import ceil
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.pagination import PageNumberPagination
from upload.pagination import CustomPagination

# Create your views here.

BASE_DIR = "/tmp/tecblic_data/"

# class UserPasswordResetView(APIView):
#     def post(self,request,uid,token):
#         serializer = UserPasswordResetSerializer(data = request.data,context = {'uid':uid,'token':token})
#         if serializer.is_valid(raise_exception=True):
#             return Response({'msg':'Password Reset Successfully'},status=status.HTTP_200_OK)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self,request):
        serializer = UserLoginSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            print("imherere------------")       
            user = authenticate(email=email,password=password)
            if not user:
                return Response({"AccountNotExist":"Your Account is Not Exist"},status=status.HTTP_400_BAD_REQUEST)
            if not user.email_verified:
                return Response({"EmailNotVerified":"Your Email is not Verified"},status=status.HTTP_400_BAD_REQUEST)
            # token = get_tokens_for_user(user)
            refresh = RefreshToken.for_user(user)

            response =  {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(response,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        

class Register(APIView):
    def post(self,request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"Please Check your Mail for verifing Account"},status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)

# class Login():
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5

class UploadApi(APIView,CustomPagination):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    def post(self,request):
        dir = os.path.join(BASE_DIR+f"user_{request.user.user_name}/")
        if not os.path.exists(dir):
            os.makedirs(dir)
        f1 = request.FILES['file']
        request.data['file_name'] = f1.name
        request.data['file_path'] = dir
        request.data['user'] = request.user.id
        serializer = UploadFileSerializer(data = request.data)
        if serializer.is_valid():
            fout = open(dir+f1.name, 'wb+')

            file_content = ContentFile( request.FILES['file'].read() )

            # Iterate through the chunks.
            for chunk in file_content.chunks():
                fout.write(chunk)
            fout.close()            
            serializer.save()
            return Response({"msg":"FIle Uploded Successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        # upload = self.filter_queryset(request=request,model = UploadFile,view=self.__class__).order_by('file_name')
        upload = UploadFile.objects.filter(user = request.user).order_by('file_name')
        page = request.query_params.get("page") if request.query_params.get("page") else 1
        limit = request.query_params.get("limit") if request.query_params.get("limit") else 5
        results,count = self.paginate(page=page, request=request, limit=limit, queryset=upload, view=self)
        serializer = UploadFileSerializer(data = results,many=True)
        serializer.is_valid()
        return Response({"Data":serializer.data,"page":ceil(count/5),"user":request.user.user_name})

    def delete(self,request,id):
        file = UploadFile.objects.filter(id=id)
        if os.path.exists(file[0].file_path+file[0].file_name):
          os.remove(file[0].file_path+file[0].file_name)
          file.delete()
          return Response({"msg":"file deleteed successfully"},status=status.HTTP_202_ACCEPTED)

# def download(request):
#     file_path = "/home/tecblic/Downloads/Log Sheet.xlsx"
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
#             return response
#     raise Http404

def download(request,id):
    uploadfile = UploadFile.objects.get(id=id)
    file_path = uploadfile.file_path + uploadfile.file_name
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb') ,as_attachment=True)
    return response

class UserPasswordResetView(APIView):
    def get(self,request,uid,token):
        serializer = AccountVerifiedSerializer(data = request.data,context = {'uid':uid,'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg':'Account Verified Successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class LogOutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        refresh_token = request.headers["Authorization"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response('User Logged out successfully')