from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic import View
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.edit import DeleteView, FormMixin, FormView
from django.views.generic.list import ListView
from django.contrib import messages
import datetime
from django.contrib.auth.models import User
from django.db.models import Q

from apps.book.models import BookLease, Book, BookBorrowRequest
from apps.libraryuser.models import Fellow
from apps.book.forms import AddForm, LendBookForm, BookEditForm
from apps.book.helpers import send_decline_mail, send_borrow_request_mail

        
class BookListView(ListView):
    model = Book
    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['form'] = LendBookForm()
        return context

class BookDetailView(DetailView):

    model = Book

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        return context

#function to handle to actions of the admin
#when the user requests to borrow a book
def admin_response(request):
    if request.GET.get('type') == 'lend':
        user = User.objects.get(username=request.GET.get('name'))
        book = Book.objects.get(id=request.GET.get('book'))
        new_lender = Fellow.objects.get(email=user.email)
        get_request = BookBorrowRequest.objects.get(borrower_id=user.id, book_name_id=request.GET.get('book'))
        get_request.is_allowed = True 
        get_request.save()
        BookLease.objects.create(book=book, borrower=new_lender, returned=False)
        return HttpResponseRedirect('/detail/%s' %(request.GET.get('book')))
    else:
        requested_leases = BookBorrowRequest.objects.all()

        lender = [i for i in requested_leases if i.borrower.username==str(request.GET.get('name'))
            and i.book_name.id==int(request.GET.get('book'))][0]
        send_decline_mail(lender.borrower.email, lender.book_name.title)
        lender.delete();
        return HttpResponseRedirect('/detail/%s' %(request.GET.get('book')))
        
class BookLeaseListView(View):

    afteroneday = datetime.date.today() + datetime.timedelta(days=1)
    aftertwodays = datetime.date.today() + datetime.timedelta(days=2)
    due_date = datetime.date.today()

    def get(self, request):
        leased_book = BookLease.objects.all()
        return render(request, 'book/booklease_list.html', {'book_lease_list': leased_book})

    def post(self, request):
        if request.POST.get('filter', None) == "1":
            leased_book = BookLease.objects.all()
            return render(request, 'book/booklease_list.html', {'book_lease_list': leased_book})
        elif request.POST.get('filter', None) == "2":
            leased_book = BookLease.objects.filter(Q(due_date=self.aftertwodays) | Q(due_date=self.afteroneday))
            return render(request, 'book/booklease_list.html', {'book_lease_list': leased_book})
        elif request.POST.get('filter', None) == "3":
            leased_book = BookLease.objects.filter(Q(due_date__lte=self.due_date))
            return render(request, 'book/booklease_list.html', {'book_lease_list': leased_book, 'due': 'due'})

class BookLeaseDetailView(DetailView):

    model = BookLease

    def get_context_data(self, **kwargs):
        context = super(BookLeaseDetailView, self).get_context_data(**kwargs)
        return context

@login_required
def get_book(request, id=None, template_name = 'book_new.html'):
    user = request.user
    if id:
        book = get_object_or_404 (Book, pk=id)
    if request.POST:
        form = AddForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "thank_you.html", locals())
    else:
        form = AddForm()
    return render(request, 'book_new.html', {'form': form,},context_instance = RequestContext(request))


@login_required
def borrow_book(request, id=None):
    user = request.user
    book = Book.objects.get(id=id)
    form = LendBookForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            book_id = request.POST.get('book')
            book = Book.objects.get(pk=book_id)
            request.session['book_id'] = book_id
            form.save()
            # request.session['borrower'] = borrower
            messages.success(request, 'Lent out Successfully')
            return HttpResponseRedirect('/home/')
    else:
        form.fields['book'].initial = book

    return render(request, 'borrow_book.html', locals(), context_instance=RequestContext(request))

@login_required
def lend_book(request, id=None):
    user = request.user
    book = Book.objects.get(id=id)
    BookBorrowRequest.objects.create(borrower=user, book_name=book)
    send_borrow_request_mail(user, book.title)
    messages.success(request, 'Your request has been sent to the Librarian')
    return HttpResponseRedirect('/home/')

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)   
    if book:
        book.delete()
        messages.warning(request, 'has been deleted')
    return HttpResponseRedirect('/home/')

@login_required
def edit_book(request, id=None):
    book = Book.objects.get(id=id)

    if request.method == 'POST':
        form = BookEditForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return render(request, "updated.html", locals())
    else:
        form = BookEditForm(instance=book)
    return render(request, 'book_edit.html', locals(), context_instance = RequestContext(request))
