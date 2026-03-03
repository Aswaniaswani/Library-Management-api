from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Book, BookIssue
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.models import User
from rest_framework import status
from .serializers import BookSerializer, BookIssueSerializer

@api_view(['POST'])
def register_user(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    
    return Response(
        {"message": "User registered successfully"},
        status=status.HTTP_201_CREATED
    )

@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    login(request, user)
    return Response({
        "message": "Login successful",
        "username": user.username,
        "is_admin": user.is_staff
    })


@api_view(['POST'])
def logout_user(request):
    if not request.user.is_authenticated:
        return Response(
            {"error": "User not logged in"},
            status=status.HTTP_400_BAD_REQUEST
        )

    logout(request)
    return Response(
        {"message": "Logout successful"},
        status=status.HTTP_200_OK
    )

# ---------------- BOOK APIs ----------------

# List books (User & Admin)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_books(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


# Add book (Admin only)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_book(request):
    if not request.user.is_staff:
        return Response({"error": "Admin access required"}, status=403)

    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)


# Update book (Admin only)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_book(request, id):
    if not request.user.is_staff:
        return Response({"error": "Admin access required"}, status=403)

    book = get_object_or_404(Book, id=id)
    serializer = BookSerializer(book, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Book updated successfully"})
    return Response(serializer.errors)


# Delete book (Admin only)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_book(request, id):
    if not request.user.is_staff:
        return Response({"error": "Admin access required"}, status=403)

    book = get_object_or_404(Book, id=id)
    book.delete()
    return Response({"message": "Book deleted successfully"})


# ---------------- ISSUE / RETURN APIs ----------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def issue_book(request):
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )

    user_id = request.data.get('user')
    book_id = request.data.get('book')
    due_date = request.data.get('due_date')

    if not user_id or not book_id or not due_date:
        return Response(
            {"error": "user, book and due_date are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = get_object_or_404(User, id=user_id)
    book = get_object_or_404(Book, id=book_id)

    if book.available_copies <= 0:
        return Response(
            {"error": "No copies available"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Prevent duplicate issue
    if BookIssue.objects.filter(
        user=user,
        book=book,
        status="Issued"
    ).exists():
        return Response(
            {"error": "This user already has this book issued"},
            status=status.HTTP_400_BAD_REQUEST
        )

    issue = BookIssue.objects.create(
        user=user,
        book=book,
        due_date=due_date,
        status="Issued"
    )

    book.available_copies -= 1
    book.save()

    serializer = BookIssueSerializer(issue)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def return_book(request, id):
    if not request.user.is_staff:
        return Response(
            {"error": "Admin access required"},
            status=status.HTTP_403_FORBIDDEN
        )

    issue = get_object_or_404(BookIssue, id=id)

    if issue.status == "Returned":
        return Response(
            {"message": "Book already returned"},
            status=status.HTTP_400_BAD_REQUEST
        )

    issue.status = "Returned"
    issue.save()

    issue.book.available_copies += 1
    issue.book.save()

    return Response(
        {"message": "Book returned successfully"},
        status=status.HTTP_200_OK
    )
# ---------------- USER HISTORY ----------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_books(request):
    issues = BookIssue.objects.filter(user=request.user)
    serializer = BookIssueSerializer(issues, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_books(request):
    title = request.GET.get('title')
    books = Book.objects.all()

    if title:
        books = books.filter(title__icontains=title)

    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)