# pylint: disable=C0103
from .app import app
from .bgm_tv import bgm_calendar


@app.route('/')
def index():
    return 'api index'


app.add_url_rule(
    '/calendar/bgm.tv/<user_id>', bgm_calendar.__qualname__, bgm_calendar
)

__all__ = ['app']
