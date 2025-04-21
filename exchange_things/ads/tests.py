from django.test import TestCase
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal
from django.urls import reverse

ad_fields = {'title': 'тест1', 'description': 'описание тест1',
            'image': '', 'category': 'тест', 'condition': 'новый'}

ad_fields_2 = {'title': 'тест2', 'description': 'описание тест2',
            'image': '', 'category': 'тест', 'condition': 'новый'}

ad_fields_3 = {'title': 'тест3', 'description': 'описание тест3',
            'image': '', 'category': 'тест', 'condition': 'новый'}

class TestBaseFunction(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="password1")
        self.user2 = User.objects.create_user(username="user2", password="password2")

    # Проверка создания объявления
    def test_create_ad(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse('create_ad'), ad_fields)
        
        # Проверка что объявление создалось
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ad.objects.count(), 1)

        ad = Ad.objects.first()
        self.assertEqual(ad.title, ad_fields['title'])
        self.assertEqual(ad.description, ad_fields['description'])
        self.assertEqual(ad.category, ad_fields['category'])
        self.assertEqual(ad.condition, ad_fields['condition'])
    
    # Проверка изменения объявления
    def test_edit_ad(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse('create_ad'), ad_fields)
        edit_fileds = ad_fields.copy()
        edit_fileds['description'] = 'новое описание тест1'
        response = self.client.post(reverse('edit_ad', args=[1]), edit_fileds)

        # Что запрос успешный и объявление все еще одно
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ad.objects.count(), 1)

        # Проверка, что значение изменилось
        ad = Ad.objects.first()
        self.assertEqual(ad.description, edit_fileds['description'])

        # Проверка, что другой пользователь не может редактировать чужое объявление
        self.client.login(username="user2", password="password2")
        new_edit_fileds = edit_fileds.copy()
        new_edit_fileds['description'] = 'тест2'
        response = self.client.post(reverse('edit_ad', args=[1]), new_edit_fileds)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Ad.objects.count(), 1)
        # Проверка, что описание не изменилось
        ad = Ad.objects.first()
        self.assertEqual(ad.description, edit_fileds['description'])

    # Проверка удаления объявления
    def test_delete_ad(self):
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse('create_ad'), ad_fields)

        # Проверка, что другой пользователь не может удалить объявление
        self.client.login(username="user2", password="password2")
        response = self.client.post(reverse('delete_ad', args=[1]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Ad.objects.count(), 1)

        # Проверка, что владелец может удалить объявление
        self.client.login(username="user1", password="password1")
        response = self.client.post(reverse('delete_ad', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ad.objects.count(), 0)

    # Проверка поиска объявления
    def test_search(self):
        self.client.login(username="user1", password="password1")
        # Создаем 3 объявления
        response = self.client.post(reverse('create_ad'), ad_fields)
        response = self.client.post(reverse('create_ad'), ad_fields_2)
        response = self.client.post(reverse('create_ad'), ad_fields_3)

        # Ищем объявление у которого в названии или в описании есть цифра 1
        response = self.client.post(reverse('get_ads'), {'search': '1'})

        # Проверяем, что запрос успешный
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Проверяем, что нашлось только одно объявление
        self.assertEqual(content.count('ID:'), 1)