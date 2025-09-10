from django.urls import path
from . import feature_views, document_views

app_name = 'features'

urlpatterns = [
    # ============ MOTIVATIONAL QUOTES ============
    path('quotes/daily/', 
         feature_views.get_daily_quote, 
         name='daily-quote'),
    
    path('quotes/mark-viewed/', 
         feature_views.mark_quote_viewed, 
         name='mark-quote-viewed'),
    
    path('quotes/like/', 
         feature_views.like_daily_quote, 
         name='like-daily-quote'),
    
    # ============ SAVED CHAT HISTORY ============
    path('chats/saved/', 
         feature_views.SavedChatHistoryListView.as_view(), 
         name='saved-chats-list'),
    
    path('chats/save/', 
         feature_views.save_chat_session, 
         name='save-chat-session'),
    
    path('chats/saved/<int:chat_id>/', 
         feature_views.delete_saved_chat, 
         name='delete-saved-chat'),
    
    path('chats/saved/<int:chat_id>/update/', 
         feature_views.update_saved_chat, 
         name='update-saved-chat'),
    
    # ============ GOALS AND REWARDS ============
    path('goals/', 
         feature_views.GoalListCreateView.as_view(), 
         name='goals-list-create'),
    
    path('goals/<int:pk>/', 
         feature_views.GoalDetailView.as_view(), 
         name='goal-detail'),
    
    path('goals/update-progress/', 
         feature_views.update_goal_progress, 
         name='update-goal-progress'),
    
    path('goals/dashboard/', 
         feature_views.get_goal_dashboard, 
         name='goal-dashboard'),
    
    path('rewards/', 
         feature_views.MilestoneRewardListView.as_view(), 
         name='rewards-list'),
    
    path('rewards/claim/', 
         feature_views.claim_reward, 
         name='claim-reward'),
    
    # ============ DOCUMENT SUMMARIZER ============
    path('documents/upload/', 
         document_views.upload_document, 
         name='upload-document'),
    
    path('documents/', 
         document_views.DocumentSummaryListView.as_view(), 
         name='document-summaries-list'),
    
    path('documents/<int:pk>/', 
         document_views.DocumentSummaryDetailView.as_view(), 
         name='document-summary-detail'),
    
    path('documents/<int:document_id>/toggle-favorite/', 
         document_views.toggle_favorite, 
         name='toggle-document-favorite'),
    
    path('documents/<int:document_id>/regenerate-summary/', 
         document_views.regenerate_summary, 
         name='regenerate-summary'),
    
    path('documents/dashboard/', 
         document_views.document_dashboard, 
         name='document-dashboard'),
    
    path('documents/bulk-delete/', 
         document_views.bulk_delete, 
         name='bulk-delete-documents'),
    
    path('documents/bulk-favorites/', 
         document_views.bulk_update_favorites, 
         name='bulk-update-document-favorites'),
    
    # ============ DEBUG ENDPOINT ============
    path('debug/auth-test/', 
         feature_views.debug_auth_test, 
         name='debug-auth-test'),
    
    # ============ STUDENT NOTIFICATIONS ============
    path('student/notifications/stats/',
         feature_views.get_notification_stats,
         name='student-notification-stats'),
]
