from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteSameSlugs(TestCase):
    NOTE_TEXT = 'Текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': 'Заголовок'
        }
        cls.url = reverse('notes:add')

    def test_author_cant_use_same_slugs(self):
        '''Тест проверки одинаковых слагов'''
        note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug1',
            author=self.author)
        self.form_data['slug'] = note.slug
        notes_count_before = Note.objects.count()
        response = self.author_client.post(self.url, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=note.slug + WARNING
        )

    def test_auto_create_slugs(self):
        '''Тест проверки автоматического создания слагов'''
        response = self.author_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestCreateNote(TestCase):
    NOTE_TEXT = 'Текст'
    NOTE_TITLE = 'Заголовок'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note_add_url = reverse('notes:add')
        cls.login_url = reverse('users:login')
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        '''Тест создания заметки анонимным пользователем'''
        notes_count_before = Note.objects.count()
        response = self.client.post(
            self.note_add_url,
            data=self.form_data)
        expected_url = f'{self.login_url}?next={self.note_add_url}'
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)
        self.assertRedirects(response, expected_url)

    def test_user_can_create_note(self):
        '''Тест создания заметки пользователем'''
        notes_count_before = Note.objects.count()
        response = self.author_client.post(
            self.note_add_url,
            data=self.form_data,
            follow=True)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before + 1)
        success_url = reverse('notes:success')
        self.assertRedirects(response, success_url)
        note = Note.objects.get(slug=self.NOTE_SLUG)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.author)


class TestNoteEditAndDelete(TestCase):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Обновлённый текст'
    NOTE_TITLE = 'Заголовок'
    NOTE_SLUG = 'test_slug'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author)
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.note_delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }

    def test_author_can_delete_note(self):
        '''Тест удаления заметки автором'''
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(self.note_delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before - 1, notes_count_after)

    def test_user_cant_delete_note_of_another_user(self):
        '''Тест удаления заметки не автором'''
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(self.note_delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before, notes_count_after)

    def test_author_can_edit_note(self):
        '''Тест редактирования заметки автором'''
        response = self.author_client.post(
            self.note_edit_url,
            data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_user_cant_edit_note_of_another_user(self):
        '''Тест редактирования заметки не автором'''
        response = self.reader_client.post(
            self.note_edit_url,
            data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
