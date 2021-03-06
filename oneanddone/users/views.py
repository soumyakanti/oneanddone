# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from django.contrib import messages
from django.shortcuts import redirect
from django.views import generic

import django_browserid.views
from funfactory.urlresolvers import reverse_lazy
from tower import ugettext as _

from oneanddone.tasks.models import TaskAttempt
from oneanddone.users.forms import UserProfileForm
from oneanddone.users.mixins import UserProfileRequiredMixin
from oneanddone.users.models import UserProfile


class LoginView(generic.TemplateView):
    template_name = 'users/login.html'


class Verify(django_browserid.views.Verify):
    def login_failure(self, *args, **kwargs):
        messages.error(self.request, _('There was a problem signing you in. Please try again.'))
        return super(Verify, self).login_failure(*args, **kwargs)


class CreateProfileView(generic.CreateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'

    def dispatch(self, request, *args, **kwargs):
        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('users.profile.detail')
        else:
            return super(CreateProfileView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.user = self.request.user
        profile.save()
        return redirect('users.profile.detail')


class UpdateProfileView(UserProfileRequiredMixin, generic.UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile/edit.html'
    success_url = reverse_lazy('users.profile.detail')

    def get_object(self):
        return self.request.user.profile


class ProfileDetailView(UserProfileRequiredMixin, generic.DetailView):
    model = UserProfile
    template_name = 'users/profile/detail.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProfileDetailView, self).get_context_data(*args, **kwargs)

        attempts_in_progress = self.request.user.taskattempt_set.filter(state=TaskAttempt.STARTED)
        ctx['attempts_in_progress'] = attempts_in_progress

        return ctx
