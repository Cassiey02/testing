import pytest

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_count(news, author_client, home_url):
    '''Тест количества новостей на странице'''
    response = author_client.get(home_url)
    object_list = response.context['object_list']
    assert len(object_list) == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url):
    '''Тест сортировки новостей'''
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
def test_comments_order(client, comments, detail_url):
    '''Тест сортировки комментариев'''
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
@pytest.mark.django_db
def test_client_has_form(detail_url, parametrized_client, form_in_context):
    '''Тест наличия формы у пользователей'''
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_in_context
