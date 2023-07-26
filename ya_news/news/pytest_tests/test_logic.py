import pytest
from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        comment,
        client,
        one_news,
        form_data):
    '''Тест анонимный пользователь не может оставлять комментарии'''
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(one_news.id,))
    client.post(url, data=form_data)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_user_can_create_comment(comment, author_client, one_news, form_data):
    '''Тест пользователь может оставлять комментарии'''
    comments_count_before = Comment.objects.count()
    url = reverse('news:detail', args=(one_news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, one_news):
    '''Тест использоввания запрещенных слов'''
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(one_news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING)
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, one_news):
    '''Тест удаления автором своего комментария'''
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(one_news.id,))
    url_to_comments = news_url + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count_after = Comment.objects.count()
    all_comments = Comment.objects.all()
    assert comment not in all_comments
    assert comments_count_after == comments_count_before - 1


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(reader_client, comment):
    '''Тест удаления автором чужого комментария'''
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    response = reader_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, form_data, one_news):
    '''Тест редактирования автором своего комментария'''
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(one_news.id,))
    url_to_comments = news_url + '#comments'
    comment_id_before = comment.id
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.id == comment_id_before


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
        reader_client,
        comment,
        form_data):
    '''Тест редактирования автором чужого комментария'''
    edit_url = reverse('news:edit', args=(comment.id,))
    response = reader_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != form_data['text']
