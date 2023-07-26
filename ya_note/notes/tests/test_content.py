from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.not_author = User.objects.create(username='Лев Простой')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)

        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            slug='note-slug',
            author=cls.author)
        cls.list_url = reverse('notes:list')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_in_list(self):
        '''Тест передачи заметки в конекст'''
        client_notes = (
            (self.author_client, True),
            (self.not_author_client, False)
        )
        for parametrized_client, note_in_context in client_notes:
            with self.subTest():
                response = parametrized_client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_context)

    def test_authorized_client_has_form_add(self):
        '''Тест передачи заметки в форму создания и редактирования'''
        urls = (
            (self.add_url, True),
            (self.edit_url, True)
        )
        for url, form_in_context in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertIs(('form' in response.context), form_in_context)
