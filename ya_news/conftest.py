import pytest
from datetime import datetime, timedelta

from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def one_news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
        comment=comment
    )
    return news


@pytest.fixture
def news():
    all_news = []
    today = datetime.today()
    for index in range(NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        all_news.append(news)
    return all_news


@pytest.fixture
def comment(author, one_news):
    comment = Comment.objects.create(
        news=one_news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def comments(author, one_news):
    now = timezone.now()
    for index in range(2):
        comments = Comment.objects.create(
            news=one_news,
            author=author,
            text=f'Tекст {index}'
        )
        comments.created = now + timedelta(days=index)
        comments.save()
    return comments


@pytest.fixture
def news_id_for_args(one_news):
    return one_news.pk,


@pytest.fixture
def comment_id_for_args(comment):
    return comment.pk,


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def detail_url(one_news):
    return reverse('news:detail', args=(one_news.id,))
