from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from smartdocx.models import UploadFiles, CustomUser
from smartdocx.serializer import UploadFilesSerializer

def format_shop_data_for_frontend(raw_data: dict) -> dict:
    """
    Transforms raw Python owner data into the structured format expected by the React frontend.
    
    Args:
        raw_data: The dictionary containing all owner and shop details from the backend.
        
    Returns:
        A new dictionary with keys mapped to the frontend's required structure.
    """
    
    # Define a default service and placeholder image for fields that might be missing
    DEFAULT_SERVICE = "Stationary & General Goods"
    PLACEHOLDER_IMAGE = "https://placehold.co/150x150/007bff/ffffff?text=Shop+Image"

    # Use .get() with a fallback value to safely access dictionary keys
    formatted_data = {
        # --- Shop Details Mapping ---
        'name': raw_data.get('shop_name', 'Unnamed Shop'),
        'service': DEFAULT_SERVICE, # Placeholder value since 'service' wasn't in the raw data
        'location': raw_data.get('owner_shop_address', 'Address Not Available'),
        'image': raw_data.get('owner_shop_image', PLACEHOLDER_IMAGE),

        # --- Contact/Owner Info Mapping ---
        # Prepending "Owned by" for a display-ready string, matching the original JS example
        'ownerName': f"Owned by {raw_data.get('owner_fullname', 'Shop Owner')}",
        'phone': raw_data.get('owner_phone_number', 'N/A'),
        'email': raw_data.get('email', 'N/A'),
        
        # Assuming the WhatsApp number is the same as the primary phone number
        'whatsapp': raw_data.get('owner_phone_number', 'N/A'),
    }
    
    return formatted_data



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
            owner_info = CustomUser.objects.filter(unique_url=unique_url).values('username', 'email', 'shop_name', 'owner_fullname', 'owner_phone_number', 'owner_shop_address', 'owner_shop_image').first()

            if not user:
                return Response({"error": "Shop not Exist, Try with other Shop, Please Check URL"})
            return Response({"message": f"Upload form for unique_url: {unique_url}. Use POST to upload file.", "owner_info": format_shop_data_for_frontend(owner_info)})
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
            
        imgkit = ImageKitClient(uploaded_file)
        result = imgkit.upload_media
        file_url = result['url']
        file_id = result.get('fileId') or result.get('file_id')  # Check ImageKit response structure

        # 4. Prepare Data for Django Model/Serializer
        data['Owner'] = user.id
        data['Unique_url'] = unique_url
        data['FileUpload'] = file_url # Add the URL from ImageKit
        data['FileUploadID'] = file_id
    
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