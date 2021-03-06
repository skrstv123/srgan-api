from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import Job
from .serializers import JobSerializer
import uuid
from rest_framework.permissions import IsAuthenticated, BasePermission

class OnlyReadWritePermission(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['POST', 'GET']

class CreateJobViewSet(ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated, OnlyReadWritePermission]

    
    # list job submmitted by current user
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            queryset.filter(
                job_submitted_by = self.request.user),
                many=True
            )
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        input_file = request.data.pop('input_file')
        fname = str(uuid.uuid4()) + '.' + input_file[0].name.split('.')[-1]
        with open(f"input_files/{fname}", "wb") as received_file:
            for chunk in input_file[0].chunks():
                received_file.write(chunk)
        job = serializer.instance
        job.input_file = fname
        job.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)



