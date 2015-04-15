from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required
from apps.book.views import BookListView
from apps.book.views import BookDetailView
# from apps.book.views import BorrowBookView
from apps.book.views import get_book
from apps.book.views import borrow_book
from apps.libraryuser.views import BookIndexListView, LoginView, LogoutView, register_user
from apps.libraryuser.views import HomeView
from apps.libraryuser.models import Fellow

urlpatterns = patterns ('',
    # url(r'^home/', HomeView.as_view(), name='home'),
    url(r'^home/', BookIndexListView.as_view(), name='book-index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/', LoginView.as_view(), name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^accounts/register/$', register_user),
    url(r'^add-book/$', login_required(get_book), name='add-book'),
    url(r'^book-status/$', BookListView.as_view(), name='book-list'),
    url(r'^book-lend/(?P<pk>\d+)/$', BookDetailView.as_view(), name='book-detail'),
    url(r'^borrow/$', borrow_book, name='borrow-book'),
)
