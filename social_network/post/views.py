from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView

from social_network.post.forms import NewPostForm
from social_network.post.models import Post

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = NewPostForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user.profile
        messages.success(self.request, 'Posted successfully')
        return super().form_valid(form)
