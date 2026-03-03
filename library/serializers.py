from rest_framework import serializers
from .models import Book, BookIssue

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookIssueSerializer(serializers.ModelSerializer):
    book_title = serializers.ReadOnlyField(source='book.title')

    class Meta:
        model = BookIssue
        fields = [
            'id',
            'user',
            'book',
            'book_title',
            'issue_date',
            'due_date',
            'status'
        ]