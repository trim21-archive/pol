from app.db_models import IqiyiBangumi, IqiyiEpisode

from .iqiyi import Iqiyi


def test_init():
    Iqiyi()


def test_submit_ep():

    Iqiyi.ep(
        ep_id=831189,
        url='https://www.iqiyi.com/v_19rr5fzwtg.html',
    )
    IqiyiEpisode.get(
        subject_id=239816,
        ep_id=831189,
        source_ep_id='v_19rr5fzwtg',
    )


def test_submit_bangumi():

    Iqiyi.subject(
        subject_id=219200,
        url='http://www.iqiyi.com/a_19rrh1ss1p.html',
    )
    IqiyiBangumi.get(
        subject_id=219200,
        bangumi_id='a_19rrh1ss1p',
    )
