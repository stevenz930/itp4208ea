from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'courses': reverse('course-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format)
    })

@api_view(['GET'])
def health_check(request, format=None):
    """Simple health check endpoint"""
    return Response({'status': 'healthy'}, status=status.HTTP_200_OK)
