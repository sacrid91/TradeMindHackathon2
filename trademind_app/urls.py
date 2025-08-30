# trademind_app/urls.py
from django.urls import path
from . import views

app_name = 'trademind_app'

urlpatterns = [
    # Landing & Public
    path('', views.landing, name='landing'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Trade Flow
    path('trade/log/', views.trade_log, name='trade_log'),
    path('trade/<int:trade_id>/insight/', views.ai_insight, name='ai_insight'),
    
    # Rule Management
    path('rule/add/', views.add_strategy_rule, name='add_rule'),
    path('rule/<int:rule_id>/edit/', views.edit_strategy_rule, name='edit_rule'),
    path('rule/<int:rule_id>/delete/', views.delete_strategy_rule, name='delete_rule'),
    
]