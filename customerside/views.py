from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
# from .models import CustomUser
from smartdocx.models import UploadFiles, CustomUser
from smartdocx.serializer import UploadFilesSerializer
# from utils.imagekit_storage import upload_to_imagekit
# from smartdocx.serializers import UploadFilesSerializer
# from .helper import upload_to_imagekit
# import helper
# @api_view(['GET', 'POST'])
# # @permission_classes([AllowAny])
# @authentication_classes([])  # No authentication required
# @permission_classes([])      # No permissions required
# @parser_classes([MultiPartParser, FormParser])
# def upload_file_view(request, unique_url):
#     print("Uploading file view")

#     if request.method == 'GET':
#         try:
#             user = CustomUser.objects.filter(unique_url=unique_url).first()
#             if not user:
#                 return Response({"error": "Shop not Exist, Try with other Shop, Please Check URL"})

#             # print("Slug URL:", unique_url)
#             # print("User:", user)
#             # return Response({"message": f"Upload form for unique_url: {unique_url}. Use POST to upload file."})
#             return Response({"message": f"Upload form for unique_url: {unique_url}. Use POST to upload file."})
        
#         except:
#             return Response({"error": "Shop not Exist, Try with other Shop"}), 404


#     data = request.data.copy()

#     user = CustomUser.objects.filter(unique_url=unique_url).first()
#     # if not user:
#     #     return Response({"error": "Invalid unique_url"}, status=400)

#     print("Posting data:", data)
#     # print("Request user:", request.user)
#     # print("Unique URL:", unique_url)

#     owner = unique_url.split('-')[0]
#     # print("Owner extracted:", owner)

#     # Assign Owner as user id (or the correct field)
#     data['Owner'] = user.id  # Ensure this matches the serializer/model
#     data['Unique_url'] = unique_url


#     serializer = UploadFilesSerializer(data=data)

#     if serializer.is_valid():
#         print("Serializer is valid")
#         serializer.save()
#         return Response(serializer.data, status=201)
#     else:
#         print('Serializer validation errors:', serializer.errors)
#         return Response(serializer.errors, status=400)










# views.py (assuming you import necessary components)

# from rest_framework.decorators import api_view # Assuming you use Django REST Framework
# from rest_framework.response import Response
from django.db import transaction # For atomic operations

# from .models import UploadFiles, CustomUser # Your models
# from .serializers import UploadFilesSerializer # Your serializer
from .utils import ImageKitClient # Import the function from Step 1
@api_view(['GET', 'POST'])
# @permission_classes([AllowAny])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
@parser_classes([MultiPartParser, FormParser])
def upload_file_view(request, unique_url):
    print("Uploading file view")

    # --- GET Request Handling (Existing code - kept for context) ---
    if request.method == 'GET':
        try:
            user = CustomUser.objects.filter(unique_url=unique_url).first()
            if not user:
                return Response({"error": "Shop not Exist, Try with other Shop, Please Check URL"})
            return Response({"message": f"Upload form for unique_url: {unique_url}. Use POST to upload file."})
        except Exception:
            return Response({"error": "Shop not Exist, Try with other Shop"}), 404
    # --- END GET Request Handling ---

    # --- POST Request Handling ---
    if request.method == 'POST':
        # 1. Get User/Owner
        user = CustomUser.objects.filter(unique_url=unique_url).first()
        if not user:
            return Response({"error": "Invalid unique_url / Shop not exist"}, status=400)

        # 2. Extract Data and File
        data = request.data.copy()
        uploaded_file = request.FILES.get('FileUpload') # Assuming 'FileUpload' is the file input name

        if not uploaded_file:
            return Response({"error": "File to upload is missing."}, status=400)
            
        print("this is going to upload ")
        imgkit = ImageKitClient(uploaded_file)
        result = imgkit.upload_media
        print("File uploaded to ImageKit")
        file_url = result['url']
        # print("this is file url kd fdklf : ", file_url)

        # 4. Prepare Data for Django Model/Serializer
        data['Owner'] = user.id
        data['Unique_url'] = unique_url
        data['FileUpload'] = file_url # Add the URL from ImageKit
    
        # 5. Validate and Save Django Model
        serializer = UploadFilesSerializer(data=data)

        if serializer.is_valid():
            with transaction.atomic():
                # Save the model instance with the ImageKit URL/ID
                instance = serializer.save()
                
                # OPTIONAL: You might want to save the original filename as well if needed
                # instance.OriginalFileName = base_filename 
                # instance.save() 
                
            return Response(serializer.data, status=201)
        else:
            print('Serializer validation errors:', serializer.errors)
            return Response(serializer.errors, status=400)
    
    return Response({"error": "Method not allowed"}, status=405) # Should be handled by @api_view