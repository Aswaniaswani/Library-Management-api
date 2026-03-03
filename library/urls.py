from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    # Books
    path('api/books/', views.list_books,name='list_book'),
    path('api/books/add/', views.add_book,name='add_book'),
    path('api/books/update/<int:id>/', views.update_book,name='update_book'),
    path('api/books/delete/<int:id>/', views.delete_book,name='delete_book'),

    # Issue & Return
    path('api/issue/', views.issue_book,name='issue_book'),
    path('api/return/<int:id>/', views.return_book,name='return_book'),

    # User history
    path('api/my-books/', views.my_books,name='my_books'),

    path('books/search/', views.search_books, name='search_books'),
]