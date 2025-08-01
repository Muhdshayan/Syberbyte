from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def hello_world(request):
    """Hello world endpoint."""
    return Response({'message': f'Hello World: {datetime.now().isoformat()}'})