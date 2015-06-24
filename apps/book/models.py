from django.db import models
from datetime import datetime, date, timedelta
import time
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.contrib.auth.models import User
from apps.libraryuser.models import StaffUser, Fellow

Categories = (
         ("Science fiction", "Science fiction"),
         ("Satire", "Satire"),
         ("Drama", "Drama"),
         ("Action and Adventure","Action and Adventure"),
         ("Romance", "Romance"),
         ("Mystery", "Mystery"),
         ("Horror", "Horror"),
         ("Self help", "Self help"),
         ("Guide", "Guide"),
         ("Travel", "Travel"),
         ("Children's", "Children's"),
         ("Religious", "Religious"),
         ("Science", "Science"),
         ("History", "History"),
         ("Math", "Math"),
         ("Anthologies", "Anthologies"),
         ("Poetry", "Poetry"),
         ("Encyclopedias", "Encyclopedias"),
         ("Dictionaries", "Dictionaries"),
         ("Comics", "Comics"),
         ("Art", "Art"),
         ("Cookbooks", "Cookbooks"),
         ("Diaries", "Diaries"),
         ("Journals", "Journals"),
         ("Prayer books", "Prayer books"),
         ("Series", "Series"),
         ("Programming", "Programming"),
         ("Biographies", "Biographies"),
         ("Autobiographies", "Autobiographies"),
         ("Fantasy", "Fantasy"),
    )

class Book(models.Model):
    title = models.CharField(max_length=50, blank=False)
    author = models.CharField(max_length=100, blank=False)
    isbn_number = models.CharField(max_length=100, unique=True)
    date_recieved = models.DateField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    source = models.CharField(max_length=50)
    category = models.CharField(max_length=150, choices=Categories)

    def get_num_available_book(self):
        available = self.quantity
        if available > 0:
            total_leased = self.book_leases.all().count()
            available = available - total_leased
        return available
    
    def get_book_request(self):
        requests = self.bookborrowrequest_set.all()
        return [i.borrower.username for i in requests]

    def get_book_deadline(self):
        leases = self.book_leases.all()
        return {lease.borrower.email:lease.days_due() for lease in leases}

    num_book_available = property(get_num_available_book)
        
    def __unicode__(self): 
        return '{}'.format(self.title)


def get_deadline():
    return datetime.now() + timedelta(days=14)

class BookBorrowRequest(models.Model):
    borrower = models.ForeignKey(User)
    book_name = models.ForeignKey(Book)
    is_allowed = models.BooleanField(default=False)

    # def __unicode__(self):
    #     return self.borrower

class BookLease(models.Model):
    book = models.ForeignKey(Book, related_name='book_leases')
    borrower = models.ForeignKey(Fellow)
    borrowed_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(default=get_deadline)
    returned = models.NullBooleanField()

    def book_is_due(self):
        check_time = time.mktime(self.due_date.timetuple()) - time.time()
        check_month = timezone.now().month == self.due_date.month
        now = date(timezone.now().year, timezone.now().month, timezone.now().day)
        then =  date(self.due_date.year, self.due_date.month, self.due_date.day)
        check_day = abs((now - then).days)
       
        if check_time <= 0:
            return "due"
        elif check_month and check_day <= 2:
            return "about"

    def days_due(self):
        now = date(timezone.now().year, timezone.now().month, timezone.now().day)
        then =  date(self.due_date.year, self.due_date.month, self.due_date.day)
        return abs((now - then).days)

    def __unicode__(self): 
        return '{}'.format(self.book)
