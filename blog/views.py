from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail



def post_list(request):
	post_list = Post.published.all()                              # Постраничная разбивка с 3 постами на страницу
	paginator = Paginator(post_list, 3)
	page_number = request.GET.get('page', 1)
	try:
		posts = paginator.page(page_number)
	except PageNotAnInteger:                                      # Если page_number не целое число, то выдать первую страницу
		posts = paginator.page(1)
	except EmptyPage:                                             # Если page_number находится вне диапазона, то выдать последнюю страницу
		posts = paginator.page(paginator.num_pages)
	return render(request,
		'blog/post/list.html',
		{'posts': posts})



class PostListView(ListView):                              	      # Альтернативное представление списка постов на основе класса
	queryset = Post.published.all()
	context_object_name = 'posts'
	paginate_by = 3
	template_name = 'blog/post/list.html'



from django.http import Http404

def post_detail(request, year, month, day, post):
	post = get_object_or_404(Post,
		#id=id,
		status=Post.Status.PUBLISHED,
		slug=post,
		publish__year=year,
		publish__month=month,
		publish__day=day)

#	try:
#		post = Post.published.get(id=id)
#	except Post.DoesNotExist:
#		raise Http404("No Post found.")

	return render(request,
		'blog/post/detail.html',
		{'post': post})



def post_share(request, post_id):
	# Извлечь пост по идентификатору id
	post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
	sent = False

	if request.method == 'POST':
	# Форма была передана на обработку
		form = EmailPostForm(request.POST)
		if form.is_valid():
		# Поля формы успешно прошли валидацию
			cd = form.cleaned_data
			post_url = request.build_absolute_uri(post.get_absolute_url())
			subject = f"{cd['name']} recommends you read " f"{post.title}"
			message = f"Read {post.title} at {post_url}\n\n" f"{cd['name']}\'s comments: {cd['comments']}"
			send_mail(subject, message, 'your_account@gmail.com',[cd['to']])
			sent = True
	# ... отправить электронное письмо
	else:
		form = EmailPostForm()
	return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
