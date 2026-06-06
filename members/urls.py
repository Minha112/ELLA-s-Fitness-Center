from django.urls import path
from . import views

urlpatterns = [
    path('join/', views.join_gym, name='join_gym'),
    path('select-plan/<str:plan>/', views.select_plan, name='select_plan'),
    path('my-membership/', views.my_membership, name='my_membership'),
    # Admin
    path('admin/members/', views.member_list, name='member_list'),
    path('admin/members/add/', views.member_add, name='member_add'),
    path('admin/members/<int:user_id>/', views.member_detail, name='member_detail'),
    path('admin/members/<int:user_id>/edit/', views.member_edit, name='member_edit'),
    path('admin/members/<int:user_id>/delete/', views.member_delete, name='member_delete'),
]
