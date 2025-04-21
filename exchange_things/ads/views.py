from django.shortcuts import render
from .models import Ad, ExchangeProposal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .forms import CreateAd, CreatedExchange, CategoryForm, SearchForm
from django.shortcuts import get_object_or_404
from .search import search_function
from django.contrib.auth.models import User


def filter_ads(request, id=None):
    category = None
    search = None
    ads = Ad.objects.all()
    if id:
        ads= ads.filter(user__id=id)
    if request.GET.get('condition'):
        ads = ads.filter(condition=request.GET.get('condition'))
    
    if request.POST.get('category'):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            ads = ads.filter(category=category)
    elif request.GET.get('category'):
        category = request.GET.get('category')
        ads = ads.filter(category=category)
    
    if request.POST.get('search'):
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data['search']
            ads = search_function(ads, search)
    elif request.GET.get('search'):
        search = request.GET.get('search')
        ads = search_function(ads, search)
    paginator = Paginator(ads, 5)
    page = request.GET.get('page', 1)
    try:
        ads = paginator.page(page)
    except EmptyPage:
        ads = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        ads = paginator.page(1)
    return {'ads': ads,
                'section': 'Объявления',
                'num_pages': paginator.num_pages,
                'category': category,
                'search': search}


def get_ads(request):
    context = filter_ads(request)
    return render(request, 
                'ads/list.html',
                context)


@login_required
def get_my_ads(request):
    ads = request.user.ads.all()
    return render(request, 
                'ads/my_list.html',
                {'ads': ads,
                'section': 'Мои объявления'})


def get_user_ads(request, id):
    context = filter_ads(request, id)
    return render(request,
                'ads/list.html',
                context)


@login_required
def get_exchange(request):
    status_code = 200
    color = 'green'
    message = None

    if request.method == 'POST':
        try:
            exchange = ExchangeProposal.objects.get(id=request.POST.get('id_exchange'))
            if request.user == exchange.receiver and exchange.status == 'Ожидает':
                new_status = request.POST.get('new_status')
                if new_status == 'Принять':
                    exchange.status = 'Принята'
                    exchange.save(update_fields=["status"])
                elif new_status == 'Отклонить':
                    exchange.status = 'Отклонена'
                    exchange.save(update_fields=["status"])
                else:
                    message = 'Некорректный статус'
                    color = 'red'
            else:
                message = 'Вы не можете менять статус у этого предложения'
                color = 'red'
        except Exception as ex:
            message = 'Предложение не найдено'
            color = 'red'
    status = request.GET.get('status')
    sender = request.GET.get('user')
    exchenges_in = request.user.received.all()
    exchenges_out = request.user.sended.all()
    users = exchenges_in.values_list('sender', flat=True).distinct().order_by('sender')
    if status:
        exchenges_in = exchenges_in.filter(status=status)
        exchenges_out = exchenges_out.filter(status=status)
    if sender:
        try:
            exchenges_in = exchenges_in.filter(sender=int(sender))
        except Exception as ex:
            message = 'Некорректный запрос'
            status_code = 404
            color = 'red'

    return render(request, 
                'exchange/list.html',
                {'exchenges_in': exchenges_in,
                'exchenges_out': exchenges_out,
                'section': 'Обмены',
                'sender': sender, 'color': color, 'mes': message,
                'users': users}, status=status_code)


@login_required
def create_ad(request):
    message = None
    color = 'green'
    form = CreateAd()
    if request.method == 'POST':
        form = CreateAd(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            message = f'Объявление "{ad.title}" добавлено'
    return render(request, 
                'ads/create.html',
                {'form': form,
                'mes': message,
                'color': color})


@login_required
def edit_ad(request, id):
    message = None
    color = 'green'
    status = 200
    form_visible = True
    ad = Ad.objects.filter(id=id, user=request.user)
    if len(ad):
        ad = ad[0]
        if request.method == 'POST':
            form = CreateAd(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                ad.title = cd['title']
                ad.description = cd['description']
                ad.image = cd['image']
                ad.category = cd['category']
                ad.condition = cd['condition']
                ad.save(update_fields=['title', 'description',
                                        'image', 'category', 'condition'])
                message = 'Изменения сохранены'
                return render(request,
                        'ads/edit.html',
                        {'form': form,
                        'mes': message,
                        'color': color})

        form = CreateAd(instance=ad)
    else:
        message = 'Объявление не найдено или вы не являетесь автором.'
        color = 'red'
        form = None
        form_visible = False
        status=404
    return render(request,
                'ads/edit.html',
                {'form': form,
                'mes': message,
                'color': color,
                'form_visible': form_visible}, status=status)


@login_required
def delete_ad(request, id):
    message = None
    color = 'green'
    status = 200
    ad = Ad.objects.filter(id=id, user=request.user)
    if len(ad):
        ad = ad[0]
        if request.method == 'POST':
            message = f'Объявление "{ad.title}" удалено'
            ad.delete()
    else:
        message = f'У вас нет объявления с id равным {id}'
        color = 'red'
        status = 404
    return render(request,
                'ads/delete.html',
                {'ad': ad,
                'mes': message,
                'color': color}, status=status)


@login_required
def create_exchange(request, id):
    message = None
    color = 'green'
    form_visible = True
    form = CreatedExchange()
    status = 200
    ad_receiver = Ad.objects.filter(id=id)
    if len(ad_receiver):
        ad_receiver = ad_receiver[0]
        if request.user != ad_receiver.user:
            if request.method == 'POST':
                form = CreatedExchange(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    ad_sender = Ad.objects.filter(id=cd['ad_sender'].id, user=request.user)
                    if len(ad_sender):
                        ad_sender = ad_sender[0]
                        new_exchange = form.save(commit=False)
                        new_exchange.sender = request.user
                        new_exchange.receiver = ad_receiver.user
                        new_exchange.ad_receiver = ad_receiver
                        try:
                            new_exchange.save()
                            message = 'Обмен предложен, посмотреть статус вы можете во вкладке "Обмены"'
                            form_visible = False
                        except Exception as ex:
                            message = f'Ошибка: {ex}'
                            color = 'red'
                            status = 404
                    else:
                        message = 'У вас нет такого объявления'
                        status = 404
                        color = 'red'
                        ads_sender = Ad.objects.filter(user=request.user)
                        ads_list = [(ad.id, ad) for ad in ads_sender]
                        form.fields['ad_sender'].choices = ads_list
                else:
                    ads_sender = Ad.objects.filter(user=request.user)
                    ads_list = [(ad.id, ad) for ad in ads_sender]
                    form.fields['ad_sender'].choices = ads_list
                    message = 'Ошибка заполнения формы'
                    status = 404
                    color = 'red'
            else:        
                ads_sender = Ad.objects.filter(user=request.user)
                if len(ads_sender):
                    ads_list = [(ad.id, ad) for ad in ads_sender]
                    form.fields['ad_sender'].choices = ads_list
                else:
                    message = 'У вас нет объявлений для обмена. Добавьте что-нибудь'
                    color = 'red'
                    form_visible = False
        else:
            message = 'Нельзя меняться с самим собой'
            color = 'red'
            form_visible = False
            status = 404
    else:
        message = f'Объявления с id "{id}" не существует'
        color = 'red'
        form_visible = False
        status=404
    return render(request,
                'exchange/create.html',
                {'form': form,
                'mes': message,
                'color': color,
                'form_visible': form_visible}, status=status)
