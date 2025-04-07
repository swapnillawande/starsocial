from django.shortcuts import render

# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.urls import reverse
from django.views import generic
from groups.models import Group, GroupMember
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect


class CreateGroup(LoginRequiredMixin, generic.CreateView):
    fields = ('name', 'description')
    model = Group
    template_name = "groups/group_form.html"


class SingleGroup(generic.DetailView):
    model = Group


class ListGroups(generic.ListView):
    model = Group
    template_name ='groups/groups_base.html'


class JoinGroup(LoginRequiredMixin, generic.RedirectView):
    
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs.get('slug'))
        
        # Check if the user is already a member to avoid duplicate entries.
        if not GroupMember.objects.filter(user=request.user, group=group).exists():
            try:
                GroupMember.objects.create(user=request.user, group=group)
            except Exception as e:
                print(f"Error: {e}")  # You can replace this with logging or an error message.
            else:
                print("You are now a group member..")
        else:
            print("User is already a member.")

        return super().get(request, *args, **kwargs)  # Perform the redirect after joining


    


class LeaveGroup(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('groups:single', kwargs={'slug': self.kwargs.get('slug')})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=self.kwargs.get('slug'))

        try:
            group_member = GroupMember.objects.get(user=self.request.user, group=group)
            group_member.delete()
            print("You have successfully left the group.")
        except GroupMember.DoesNotExist:
            print("You are not a member of this group.")

        # ✅ Return an actual redirect response
        return HttpResponseRedirect(self.get_redirect_url(*args, **kwargs))
