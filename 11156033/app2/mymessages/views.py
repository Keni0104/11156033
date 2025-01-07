from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, MessageForm, UserProfileForm
from .models import Message, CustomUser 

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '註冊成功！')
            return redirect('message_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'mymessages/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('message_list')

def message_list(request):
    
    popular_messages = Message.objects.order_by('-likes', '-views')[:5]
    search_query = request.GET.get('search', None)
    messages_list = Message.objects.all()
    category = request.GET.get('category', None)
    if category:
        messages_list = messages_list.filter(category=category)
    if search_query:
        messages_list = messages_list.filter(content__icontains=search_query)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, '請先登入')
            return redirect('login')
        
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            message.save()
            messages.success(request, '留言成功！')
            return redirect('message_list')
    else:
        form = MessageForm()

    if request.user.is_authenticated:
        following_users = request.user.following.all()
        following_messages = Message.objects.filter(user__in=following_users)
    else:
        following_messages = Message.objects.none()
        
    return render(request, 'mymessages/message_list.html', {
        'messages_list': messages_list,
        'popular_messages': popular_messages,
        'following_messages': following_messages,
        'form': form,
    })

@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, user=request.user)
    
    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, '留言已更新')
            return redirect('message_list')
    else:
        form = MessageForm(instance=message)
    
    return render(request, 'mymessages/edit_message.html', {
        'form': form, 
        'message': message
    })

@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, user=request.user)
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, '留言已刪除')
        return redirect('message_list')
    
    return render(request, 'mymessages/delete_message.html', {'message': message})

from .forms import UserProfileForm

@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('edit_profile')  # 假設有一個顯示個人資料的頁面
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'mymessages/edit_profile.html', {'form': form})

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(CustomUser  , id=user_id)
    request.user.following.add(user_to_follow)
    messages.success(request, f'已追蹤 {user_to_follow.username}')
    return redirect('message_list')  # 重定向到留言列表

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(CustomUser  , id=user_id)
    request.user.following.remove(user_to_unfollow)
    messages.success(request, f'已取消追蹤 {user_to_unfollow.username}')
    return redirect('message_list')  # 重定向到留言列表