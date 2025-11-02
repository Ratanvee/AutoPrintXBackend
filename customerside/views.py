from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from smartdocx.models import UploadFiles, CustomUser
from smartdocx.serializer import UploadFilesSerializer
from django.db import transaction
import traceback
import logging
from app import settings

# Set up logging
logger = logging.getLogger(__name__)

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
        'service': DEFAULT_SERVICE,
        'location': raw_data.get('owner_shop_address', 'Address Not Available'),
        'image': raw_data.get('owner_shop_image', PLACEHOLDER_IMAGE),

        # --- Contact/Owner Info Mapping ---
        'ownerName': f"Owned by {raw_data.get('owner_fullname', 'Shop Owner')}",
        'phone': raw_data.get('owner_phone_number', 'N/A'),
        'email': raw_data.get('email', 'N/A'),
        'whatsapp': raw_data.get('owner_phone_number', 'N/A'),
    }
    
    return formatted_data


@api_view(['GET', 'POST'])
@authentication_classes([])  # No authentication required
@permission_classes([])      # No permissions required
@parser_classes([MultiPartParser, FormParser])
def upload_file_view(request, unique_url):
    """
    Handle file uploads and shop information retrieval.
    
    GET: Returns shop information
    POST: Uploads files and creates order
    """
    
    logger.info(f"Request received: {request.method} for unique_url: {unique_url}")

    # --- GET Request Handling ---
    if request.method == 'GET':
        try:
            # Check if user exists
            user = CustomUser.objects.filter(unique_url=unique_url).first()
            
            if not user:
                logger.warning(f"Shop not found for unique_url: {unique_url}")
                return Response(
                    {
                        "error": "Shop does not exist. Please check the URL and try again.",
                        "message": "The shop you're looking for could not be found."
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get owner information
            owner_info = CustomUser.objects.filter(unique_url=unique_url).values(
                'username', 'email', 'shop_name', 'owner_fullname', 
                'owner_phone_number', 'owner_shop_address', 'owner_shop_image'
            ).first()

            if not owner_info:
                logger.error(f"Owner info not found for user: {unique_url}")
                return Response(
                    {
                        "error": "Shop information is incomplete.",
                        "message": "Unable to retrieve complete shop details."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Successfully retrieved shop info for: {unique_url}")
            return Response({
                "message": f"Upload form for shop: {owner_info.get('shop_name', 'Unknown')}. Use POST to upload files.", 
                "owner_info": format_shop_data_for_frontend(owner_info),
                "success": True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"GET request error for {unique_url}: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {
                    "error": "An error occurred while fetching shop information.",
                    "message": "Please try again later or contact support.",
                    "details": str(e) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --- POST Request Handling ---
    if request.method == 'POST':
        try:
            logger.info(f"Processing file upload for unique_url: {unique_url}")
            
            # 1. Validate User/Shop
            user = CustomUser.objects.filter(unique_url=unique_url).first()
            if not user:
                logger.warning(f"Upload attempt for non-existent shop: {unique_url}")
                return Response(
                    {
                        "error": "Invalid shop URL.",
                        "message": "The shop does not exist. Please check the URL."
                    }, 
                    status=status.HTTP_404_NOT_FOUND
                )

            # 2. Validate File Upload
            uploaded_file = request.FILES.get('FileUpload')
            
            if not uploaded_file:
                logger.warning(f"Upload attempt without file for {unique_url}")
                return Response(
                    {
                        "error": "No file uploaded.",
                        "message": "Please select a file to upload."
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Validate File Size (25MB limit)
            MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes
            file_size_mb = uploaded_file.size / (1024 * 1024)
            
            if uploaded_file.size > MAX_FILE_SIZE:
                logger.warning(
                    f"File too large: {file_size_mb:.2f}MB for {unique_url}"
                )
                return Response(
                    {
                        "error": f"File size exceeds 25MB limit.",
                        "message": f"Your file is {file_size_mb:.2f}MB. Please upload a file smaller than 25MB.",
                        "file_size": f"{file_size_mb:.2f}MB",
                        "max_size": "25MB"
                    },
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                )
            
            # 4. Validate File Type (optional - add your allowed types)
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if f'.{file_extension}' not in allowed_extensions:
                logger.warning(
                    f"Invalid file type: {file_extension} for {unique_url}"
                )
                return Response(
                    {
                        "error": "Invalid file type.",
                        "message": f"File type '.{file_extension}' is not supported.",
                        "allowed_types": ", ".join(allowed_extensions)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(
                f"Uploading file: {uploaded_file.name} "
                f"({file_size_mb:.2f}MB) for {unique_url}"
            )
            
            # 5. Upload to ImageKit
            try:
                from .utils import ImageKitClient
                imgkit = ImageKitClient(uploaded_file)
                result = imgkit.upload_media
                
                if not result:
                    logger.error(f"ImageKit upload failed for {unique_url}")
                    return Response(
                        {
                            "error": "File upload to cloud storage failed.",
                            "message": "Please try again or contact support."
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                file_url = result.get('url')
                file_id = result.get('fileId') or result.get('file_id')
                
                if not file_url:
                    logger.error(f"ImageKit returned no URL for {unique_url}")
                    return Response(
                        {
                            "error": "File upload incomplete.",
                            "message": "Upload was successful but no file URL was returned."
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                logger.info(f"Successfully uploaded to ImageKit: {file_id}")
                
            except Exception as e:
                logger.error(
                    f"ImageKit upload error for {unique_url}: "
                    f"{str(e)}\n{traceback.format_exc()}"
                )
                return Response(
                    {
                        "error": "Cloud storage upload failed.",
                        "message": "Unable to upload file to storage. Please try again.",
                        "details": str(e) if settings.DEBUG else None
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # 6. Prepare Data for Database
            upload_data = {
                'Owner': user.id,
                'Unique_url': unique_url,
                'FileUpload': file_url,
                'FileUploadID': file_id,
            }
            
            # Add other form fields
            for key, value in request.data.items():
                if key != 'FileUpload':  # Skip the file field
                    upload_data[key] = value
            
            logger.info(f"Validating serializer for {unique_url}")
        
            # 7. Validate and Save to Database
            serializer = UploadFilesSerializer(data=upload_data)

            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        instance = serializer.save()
                        logger.info(
                            f"Order saved successfully: ID {instance.id} "
                            f"for {unique_url}"
                        )
                        
                    return Response(
                        {
                            "success": True,
                            "message": "Order submitted successfully!",
                            "data": serializer.data,
                            "order_id": upload_data.get('OrderId'),
                            "file_name": uploaded_file.name,
                            "file_size": f"{file_size_mb:.2f}MB"
                        },
                        status=status.HTTP_201_CREATED
                    )
                    
                except Exception as e:
                    logger.error(
                        f"Database save error for {unique_url}: "
                        f"{str(e)}\n{traceback.format_exc()}"
                    )
                    return Response(
                        {
                            "error": "Failed to save order to database.",
                            "message": "Your file was uploaded but order creation failed.",
                            "details": str(e) if settings.DEBUG else None
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.warning(
                    f"Serializer validation failed for {unique_url}: "
                    f"{serializer.errors}"
                )
                
                # Format validation errors for better user experience
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                return Response(
                    {
                        "error": "Invalid order data.",
                        "message": "Please check your input and try again.",
                        "validation_errors": error_messages,
                        "details": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(
                f"Unexpected POST error for {unique_url}: "
                f"{str(e)}\n{traceback.format_exc()}"
            )
            return Response(
                {
                    "error": "An unexpected error occurred.",
                    "message": "Please try again later or contact support.",
                    "details": str(e) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    # Method not allowed
    return Response(
        {
            "error": "Method not allowed.",
            "message": "Only GET and POST requests are supported."
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )