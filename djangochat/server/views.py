from django.db.models import Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from .models import Server
from .schema import server_list_docs
from .serializer import ServerSerializer


# Create your views here.
class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()
    
    @server_list_docs
    def list(self,request):
        """
        Returns a filtered list of servers based on query parameters.

        This method supports filtering by category, limiting quantity, 
        filtering by authenticated user membership, filtering by server ID, 
        and optionally annotating each server with the number of members.

        Args:
            request (Request): The DRF request object containing query parameters:
                - category (str, optional): Filter servers by category name.
                - qty (int, optional): Limit the number of results returned.
                - by_user (str, optional): If "true", filter servers by the logged-in user.
                - by_serverid (str, optional): Filter by a specific server ID.
                - with_num_members (str, optional): If "true", annotate each server 
                with the count of its members.

        Raises:
            AuthenticationFailed: If `by_user` or `by_serverid` is requested but the user is not authenticated.
            ValidationError: If an invalid server ID is provided or the server is not found.

        Returns:
            Response: A DRF Response containing serialized server data.
        """
        category = request.query_params.get("category")  
        qty = request.query_params.get("qty")   
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # if by_user or by_serverid and not request.user.is_authenticated:
        #     raise AuthenticationFailed()

        if category:
            self.queryset = self.queryset.filter(category__name=category) 
        
        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member = user_id)
            else:
                raise AuthenticationFailed() 
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members = Count("member"))

        if qty:
            self.queryset = self.queryset[: int(qty)]

        if by_serverid:
            try:
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                raise ValidationError(detail=f"Server with id {by_serverid} not found")

            
        serializer = ServerSerializer(self.queryset,many=True, context={"num_members": with_num_members}) 
        return Response(serializer.data)