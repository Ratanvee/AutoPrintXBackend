# from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from smartdocx.models import UploadFiles, CustomUser
# from smartdocx.serializer import UploadFilesSerializer
# from django.db import transaction
# import traceback
# import logging
# from app import settings

# # Set up logging
# logger = logging.getLogger(__name__)

# def format_shop_data_for_frontend(raw_data: dict) -> dict:
#     """
#     Transforms raw Python owner data into the structured format expected by the React frontend.
    
#     Args:
#         raw_data: The dictionary containing all owner and shop details from the backend.
        
#     Returns:
#         A new dictionary with keys mapped to the frontend's required structure.
#     """
    
#     # Define a default service and placeholder image for fields that might be missing
#     DEFAULT_SERVICE = "Stationary & General Goods"
#     PLACEHOLDER_IMAGE = "https://placehold.co/150x150/007bff/ffffff?text=Shop+Image"

#     # Use .get() with a fallback value to safely access dictionary keys
#     formatted_data = {
#         # --- Shop Details Mapping ---
#         'name': raw_data.get('shop_name', 'Unnamed Shop'),
#         'service': DEFAULT_SERVICE,
#         'location': raw_data.get('owner_shop_address', 'Address Not Available'),
#         'image': raw_data.get('owner_shop_image', PLACEHOLDER_IMAGE),

#         # --- Contact/Owner Info Mapping ---
#         'ownerName': f"Owned by {raw_data.get('owner_fullname', 'Shop Owner')}",
#         'phone': raw_data.get('owner_phone_number', 'N/A'),
#         'email': raw_data.get('email', 'N/A'),
#         'whatsapp': raw_data.get('owner_phone_number', 'N/A'),
#     }
    
#     return formatted_data


# @api_view(['GET', 'POST'])
# @authentication_classes([])  # No authentication required
# @permission_classes([])      # No permissions required
# @parser_classes([MultiPartParser, FormParser])
# def upload_file_view(request, unique_url):
#     """
#     Handle file uploads and shop information retrieval.
    
#     GET: Returns shop information
#     POST: Uploads files and creates order
#     """
    
#     logger.info(f"Request received: {request.method} for unique_url: {unique_url}")

#     # --- GET Request Handling ---
#     if request.method == 'GET':
#         try:
#             # Check if user exists
#             user = CustomUser.objects.filter(unique_url=unique_url).first()
            
#             if not user:
#                 logger.warning(f"Shop not found for unique_url: {unique_url}")
#                 return Response(
#                     {
#                         "error": "Shop does not exist. Please check the URL and try again.",
#                         "message": "The shop you're looking for could not be found."
#                     }, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )
            
#             # Get owner information
#             owner_info = CustomUser.objects.filter(unique_url=unique_url).values(
#                 'username', 'email', 'shop_name', 'owner_fullname', 
#                 'owner_phone_number', 'owner_shop_address', 'owner_shop_image'
#             ).first()

#             if not owner_info:
#                 logger.error(f"Owner info not found for user: {unique_url}")
#                 return Response(
#                     {
#                         "error": "Shop information is incomplete.",
#                         "message": "Unable to retrieve complete shop details."
#                     },
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             logger.info(f"Successfully retrieved shop info for: {unique_url}")
#             return Response({
#                 "message": f"Upload form for shop: {owner_info.get('shop_name', 'Unknown')}. Use POST to upload files.", 
#                 "owner_info": format_shop_data_for_frontend(owner_info),
#                 "success": True
#             }, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             logger.error(f"GET request error for {unique_url}: {str(e)}\n{traceback.format_exc()}")
#             return Response(
#                 {
#                     "error": "An error occurred while fetching shop information.",
#                     "message": "Please try again later or contact support.",
#                     "details": str(e) if settings.DEBUG else None
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

#     # --- POST Request Handling ---
#     if request.method == 'POST':
#         try:
#             logger.info(f"Processing file upload for unique_url: {unique_url}")
            
#             # 1. Validate User/Shop
#             user = CustomUser.objects.filter(unique_url=unique_url).first()
#             if not user:
#                 logger.warning(f"Upload attempt for non-existent shop: {unique_url}")
#                 return Response(
#                     {
#                         "error": "Invalid shop URL.",
#                         "message": "The shop does not exist. Please check the URL."
#                     }, 
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # 2. Validate File Upload
#             uploaded_file = request.FILES.get('FileUpload')
            
#             if not uploaded_file:
#                 logger.warning(f"Upload attempt without file for {unique_url}")
#                 return Response(
#                     {
#                         "error": "No file uploaded.",
#                         "message": "Please select a file to upload."
#                     }, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # 3. Validate File Size (25MB limit)
#             MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB in bytes
#             file_size_mb = uploaded_file.size / (1024 * 1024)
            
#             if uploaded_file.size > MAX_FILE_SIZE:
#                 logger.warning(
#                     f"File too large: {file_size_mb:.2f}MB for {unique_url}"
#                 )
#                 return Response(
#                     {
#                         "error": f"File size exceeds 25MB limit.",
#                         "message": f"Your file is {file_size_mb:.2f}MB. Please upload a file smaller than 25MB.",
#                         "file_size": f"{file_size_mb:.2f}MB",
#                         "max_size": "25MB"
#                     },
#                     status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
#                 )
            
#             # 4. Validate File Type (optional - add your allowed types)
#             allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
#             file_extension = uploaded_file.name.lower().split('.')[-1]
            
#             if f'.{file_extension}' not in allowed_extensions:
#                 logger.warning(
#                     f"Invalid file type: {file_extension} for {unique_url}"
#                 )
#                 return Response(
#                     {
#                         "error": "Invalid file type.",
#                         "message": f"File type '.{file_extension}' is not supported.",
#                         "allowed_types": ", ".join(allowed_extensions)
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
            
#             logger.info(
#                 f"Uploading file: {uploaded_file.name} "
#                 f"({file_size_mb:.2f}MB) for {unique_url}"
#             )
            
#             # 5. Upload to ImageKit
#             try:
#                 from .utils import ImageKitClient
#                 imgkit = ImageKitClient(uploaded_file)
#                 result = imgkit.upload_media
                
#                 if not result:
#                     logger.error(f"ImageKit upload failed for {unique_url}")
#                     return Response(
#                         {
#                             "error": "File upload to cloud storage failed.",
#                             "message": "Please try again or contact support."
#                         },
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )
                
#                 file_url = result.get('url')
#                 file_id = result.get('fileId') or result.get('file_id')
                
#                 if not file_url:
#                     logger.error(f"ImageKit returned no URL for {unique_url}")
#                     return Response(
#                         {
#                             "error": "File upload incomplete.",
#                             "message": "Upload was successful but no file URL was returned."
#                         },
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )
                
#                 logger.info(f"Successfully uploaded to ImageKit: {file_id}")
                
#             except Exception as e:
#                 logger.error(
#                     f"ImageKit upload error for {unique_url}: "
#                     f"{str(e)}\n{traceback.format_exc()}"
#                 )
#                 return Response(
#                     {
#                         "error": "Cloud storage upload failed.",
#                         "message": "Unable to upload file to storage. Please try again.",
#                         "details": str(e) if settings.DEBUG else None
#                     },
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                 )

#             # 6. Prepare Data for Database
#             upload_data = {
#                 'Owner': user.id,
#                 'Unique_url': unique_url,
#                 'FileUpload': file_url,
#                 'FileUploadID': file_id,
#             }
            
#             # Add other form fields
#             for key, value in request.data.items():
#                 if key != 'FileUpload':  # Skip the file field
#                     upload_data[key] = value
            
#             logger.info(f"Validating serializer for {unique_url}")
        
#             # 7. Validate and Save to Database
#             serializer = UploadFilesSerializer(data=upload_data)

#             if serializer.is_valid():
#                 try:
#                     with transaction.atomic():
#                         instance = serializer.save()
#                         logger.info(
#                             f"Order saved successfully: ID {instance.id} "
#                             f"for {unique_url}"
#                         )
                        
#                     return Response(
#                         {
#                             "success": True,
#                             "message": "Order submitted successfully!",
#                             "data": serializer.data,
#                             "order_id": upload_data.get('OrderId'),
#                             "file_name": uploaded_file.name,
#                             "file_size": f"{file_size_mb:.2f}MB"
#                         },
#                         status=status.HTTP_201_CREATED
#                     )
                    
#                 except Exception as e:
#                     logger.error(
#                         f"Database save error for {unique_url}: "
#                         f"{str(e)}\n{traceback.format_exc()}"
#                     )
#                     return Response(
#                         {
#                             "error": "Failed to save order to database.",
#                             "message": "Your file was uploaded but order creation failed.",
#                             "details": str(e) if settings.DEBUG else None
#                         },
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR
#                     )
#             else:
#                 logger.warning(
#                     f"Serializer validation failed for {unique_url}: "
#                     f"{serializer.errors}"
#                 )
                
#                 # Format validation errors for better user experience
#                 error_messages = []
#                 for field, errors in serializer.errors.items():
#                     for error in errors:
#                         error_messages.append(f"{field}: {error}")
                
#                 return Response(
#                     {
#                         "error": "Invalid order data.",
#                         "message": "Please check your input and try again.",
#                         "validation_errors": error_messages,
#                         "details": serializer.errors
#                     },
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
                
#         except Exception as e:
#             logger.error(
#                 f"Unexpected POST error for {unique_url}: "
#                 f"{str(e)}\n{traceback.format_exc()}"
#             )
#             return Response(
#                 {
#                     "error": "An unexpected error occurred.",
#                     "message": "Please try again later or contact support.",
#                     "details": str(e) if settings.DEBUG else None
#                 },
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
    
#     # Method not allowed
#     return Response(
#         {
#             "error": "Method not allowed.",
#             "message": "Only GET and POST requests are supported."
#         },
#         status=status.HTTP_405_METHOD_NOT_ALLOWED
#     )



# views.py - Enhanced with detailed logging for debugging

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
import json

logger = logging.getLogger(__name__)

def format_shop_data_for_frontend(raw_data: dict) -> dict:
    """Transforms raw Python owner data into the structured format expected by the React frontend."""
    DEFAULT_SERVICE = "Stationary & General Goods"
    PLACEHOLDER_IMAGE = "https://placehold.co/150x150/007bff/ffffff?text=Shop+Image"

    formatted_data = {
        'name': raw_data.get('shop_name', 'Unnamed Shop'),
        'service': DEFAULT_SERVICE,
        'location': raw_data.get('owner_shop_address', 'Address Not Available'),
        'image': raw_data.get('owner_shop_image', PLACEHOLDER_IMAGE),
        'ownerName': f"Owned by {raw_data.get('owner_fullname', 'Shop Owner')}",
        'phone': raw_data.get('owner_phone_number', 'N/A'),
        'email': raw_data.get('email', 'N/A'),
        'whatsapp': raw_data.get('owner_phone_number', 'N/A'),
    }
    return formatted_data


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
@parser_classes([MultiPartParser, FormParser])
def upload_file_view(request, unique_url):
    """
    Handle file uploads and shop information retrieval.
    Supports multiple file uploads (up to 5 files).
    """
    
    logger.info(f"Request received: {request.method} for unique_url: {unique_url}")

    # --- GET Request Handling ---
    if request.method == 'GET':
        try:
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

    # --- POST Request Handling (Multiple Files) ---
    if request.method == 'POST':
        try:
            logger.info(f"Processing file upload for unique_url: {unique_url}")
            
            # 🔍 DEBUG: Log all incoming request data
            logger.info(f"📋 Request.data keys: {list(request.data.keys())}")
            logger.info(f"📋 Request.FILES keys: {list(request.FILES.keys())}")
            
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

            # 2. Get all uploaded files
            uploaded_files = request.FILES.getlist('FileUpload')
            
            if not uploaded_files or len(uploaded_files) == 0:
                logger.warning(f"Upload attempt without files for {unique_url}")
                return Response(
                    {
                        "error": "No files uploaded.",
                        "message": "Please select at least one file to upload."
                    }, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Validate number of files (max 5)
            MAX_FILES = 5
            if len(uploaded_files) > MAX_FILES:
                logger.warning(f"Too many files: {len(uploaded_files)} for {unique_url}")
                return Response(
                    {
                        "error": f"Too many files.",
                        "message": f"Maximum {MAX_FILES} files allowed. You uploaded {len(uploaded_files)} files.",
                        "max_files": MAX_FILES,
                        "uploaded_count": len(uploaded_files)
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 4. Validate files
            MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png']
            
            file_urls_dict = {}
            file_ids_dict = {}
            total_size = 0
            
            # Process each file
            for idx, uploaded_file in enumerate(uploaded_files):
                file_size_mb = uploaded_file.size / (1024 * 1024)
                total_size += uploaded_file.size
                
                # Check file size
                if uploaded_file.size > MAX_FILE_SIZE:
                    logger.warning(f"File {uploaded_file.name} too large: {file_size_mb:.2f}MB")
                    return Response(
                        {
                            "error": f"File '{uploaded_file.name}' exceeds 25MB limit.",
                            "message": f"File is {file_size_mb:.2f}MB. Max size is 25MB.",
                            "file_name": uploaded_file.name,
                            "file_size": f"{file_size_mb:.2f}MB"
                        },
                        status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
                    )
                
                # Check file type
                file_extension = uploaded_file.name.lower().split('.')[-1]
                if f'.{file_extension}' not in allowed_extensions:
                    logger.warning(f"Invalid file type: {file_extension}")
                    return Response(
                        {
                            "error": "Invalid file type.",
                            "message": f"File '{uploaded_file.name}' type '.{file_extension}' not supported.",
                            "allowed_types": ", ".join(allowed_extensions)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                logger.info(f"Processing file {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                
                # 5. Upload to ImageKit
                try:
                    from .utils import ImageKitClient
                    imgkit = ImageKitClient(uploaded_file)
                    result = imgkit.upload_media
                    
                    if not result:
                        logger.error(f"ImageKit upload failed for {uploaded_file.name}")
                        return Response(
                            {
                                "error": f"Failed to upload '{uploaded_file.name}'.",
                                "message": "Cloud storage upload failed."
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    
                    file_url = result.get('url')
                    file_id = result.get('fileId') or result.get('file_id')
                    
                    if not file_url:
                        logger.error(f"No URL returned for {uploaded_file.name}")
                        return Response(
                            {
                                "error": f"Upload incomplete for '{uploaded_file.name}'.",
                                "message": "No file URL returned."
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                    
                    # Store in dictionaries
                    file_urls_dict[uploaded_file.name] = file_url
                    file_ids_dict[uploaded_file.name] = file_id
                    
                    logger.info(f"✅ Uploaded {uploaded_file.name} to ImageKit: {file_id}")
                    
                except Exception as e:
                    logger.error(f"ImageKit error for {uploaded_file.name}: {str(e)}")
                    return Response(
                        {
                            "error": f"Upload failed for '{uploaded_file.name}'.",
                            "message": str(e) if settings.DEBUG else "Cloud storage error.",
                            "details": str(e) if settings.DEBUG else None
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # 6. Prepare database data
            upload_data = {
                'Owner': user.id,
                'Unique_url': unique_url,
                'FileUpload': json.dumps(file_urls_dict),
                'FileUploadID': json.dumps(file_ids_dict),
            }
            
            # ✅ NEW: Handle page counts with detailed logging
            file_pages_dict = {}
            total_pages = 0
            
            # 🔍 DEBUG: Check if FilePagesCount is in request
            if 'FilePagesCount' in request.data:
                logger.info(f"📄 FilePagesCount found in request: {request.data.get('FilePagesCount')}")
            else:
                logger.warning(f"⚠️ FilePagesCount NOT found in request.data")
                logger.info(f"📋 Available keys: {list(request.data.keys())}")
            
            # Add other form fields
            for key, value in request.data.items():
                logger.info(f"🔑 Processing field: {key} = {value} (type: {type(value).__name__})")
                
                if key == 'FileUpload':
                    continue
                elif key == 'PaymentStatus':
                    # Convert PaymentStatus string to boolean
                    upload_data[key] = value in ['1', 'true', 'True', True, 1]
                    logger.info(f"✅ PaymentStatus converted to: {upload_data[key]}")
                    
                elif key == 'FilePagesCount':
                    # Parse and store page counts
                    logger.info(f"📄 Processing FilePagesCount: {value}")
                    try:
                        if isinstance(value, str):
                            file_pages_dict = json.loads(value)
                            logger.info(f"✅ Parsed FilePagesCount from string: {file_pages_dict}")
                        elif isinstance(value, dict):
                            file_pages_dict = value
                            logger.info(f"✅ FilePagesCount is already dict: {file_pages_dict}")
                        else:
                            logger.warning(f"⚠️ Unexpected FilePagesCount type: {type(value)}")
                            file_pages_dict = {}
                        
                        # Store as JSON string
                        upload_data['FilePagesCount'] = json.dumps(file_pages_dict)
                        logger.info(f"✅ Stored FilePagesCount: {upload_data['FilePagesCount']}")
                        
                        # Calculate total pages
                        if file_pages_dict:
                            total_pages = sum(int(p) for p in file_pages_dict.values())
                            logger.info(f"✅ Calculated total_pages: {total_pages}")
                        
                    except (json.JSONDecodeError, TypeError, AttributeError, ValueError) as e:
                        logger.error(f"❌ Failed to parse FilePagesCount: {e}")
                        logger.error(f"❌ Value was: {value} (type: {type(value)})")
                        upload_data['FilePagesCount'] = '{}'
                        
                elif key == 'NoOfPages':
                    # Use provided total or calculated total
                    try:
                        provided_pages = int(value) if value else 0
                        # Use the maximum of provided or calculated
                        total_pages = max(provided_pages, total_pages)
                        upload_data[key] = total_pages
                        logger.info(f"✅ NoOfPages set to: {total_pages}")
                    except (ValueError, TypeError) as e:
                        logger.error(f"❌ Failed to parse NoOfPages: {e}")
                        upload_data[key] = total_pages
                else:
                    upload_data[key] = value
            
            # ✅ Ensure FilePagesCount exists even if not sent
            if 'FilePagesCount' not in upload_data:
                logger.warning(f"⚠️ FilePagesCount not in upload_data, setting to empty dict")
                upload_data['FilePagesCount'] = '{}'
            
            # ✅ Ensure NoOfPages is set
            if 'NoOfPages' not in upload_data or not upload_data['NoOfPages']:
                upload_data['NoOfPages'] = total_pages
                logger.info(f"✅ Set default NoOfPages to: {total_pages}")
            
            # 🔍 DEBUG: Log final upload_data
            logger.info(f"📦 Final upload_data:")
            logger.info(f"   - FileUpload: {upload_data.get('FileUpload')}")
            logger.info(f"   - FileUploadID: {upload_data.get('FileUploadID')}")
            logger.info(f"   - FilePagesCount: {upload_data.get('FilePagesCount')}")
            logger.info(f"   - NoOfPages: {upload_data.get('NoOfPages')}")
            
            logger.info(f"Validating serializer for {unique_url} with {len(uploaded_files)} files")
        
            # 7. Validate and Save to Database
            serializer = UploadFilesSerializer(data=upload_data)

            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        instance = serializer.save()
                        logger.info(f"✅ Order {instance.id} saved with {len(uploaded_files)} files")
                        logger.info(f"✅ Saved FilePagesCount: {instance.FilePagesCount}")
                        logger.info(f"✅ Saved NoOfPages: {instance.NoOfPages}")
                        
                    return Response(
                        {
                            "success": True,
                            "message": f"Order submitted successfully with {len(uploaded_files)} file(s)!",
                            "data": serializer.data,
                            "order_id": upload_data.get('OrderId'),
                            "files_uploaded": len(uploaded_files),
                            "file_names": list(file_urls_dict.keys()),
                            "total_size": f"{total_size / (1024 * 1024):.2f}MB",
                            "total_pages": total_pages,
                            "file_pages": file_pages_dict
                        },
                        status=status.HTTP_201_CREATED
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Database save error: {str(e)}\n{traceback.format_exc()}")
                    return Response(
                        {
                            "error": "Failed to save order.",
                            "message": "Files uploaded but database save failed.",
                            "details": str(e) if settings.DEBUG else None
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                logger.error(f"❌ Validation failed: {serializer.errors}")
                
                error_messages = []
                for field, errors in serializer.errors.items():
                    for error in errors:
                        error_messages.append(f"{field}: {error}")
                
                return Response(
                    {
                        "error": "Invalid order data.",
                        "message": "Please check your input.",
                        "validation_errors": error_messages,
                        "details": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return Response(
                {
                    "error": "An unexpected error occurred.",
                    "message": "Please try again later.",
                    "details": str(e) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(
        {
            "error": "Method not allowed.",
            "message": "Only GET and POST requests are supported."
        },
        status=status.HTTP_405_METHOD_NOT_ALLOWED
    )