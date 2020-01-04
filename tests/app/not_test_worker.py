from app.worker import submit_ep, submit_bangumi
from app.db.mysql import db
from app.db_models import IqiyiBangumi, IqiyiEpisode, BilibiliBangumi, BilibiliEpisode


def test_submit_bilibili_bangumi():
    submit_bangumi(
        subject_id=262939,
        url='https://www.bilibili.com/bangumi/play/ep276477/',
    )
    BilibiliBangumi.get(
        subject_id=262939,
        media_id=28221399,
        season_id=28002,
    )


def test_submit_bilibili_ep():
    submit_ep(
        ep_id=893707,
        url='https://www.bilibili.com/bangumi/play/ep276614',
    )
    with db.allow_sync():
        BilibiliBangumi.get(
            subject_id=271724,
            media_id=28221412,
            season_id=28013,
        )

        BilibiliEpisode.get(
            source_ep_id=276614,
            ep_id=893707,
            subject_id=271724,
        )


def test_submit_iqiyi_bangumi():
    submit_bangumi(
        subject_id=219200,
        url='http://www.iqiyi.com/a_19rrh1ss1p.html',
    )
    with db.allow_sync():
        IqiyiBangumi.get(
            subject_id=219200,
            bangumi_id='19rrh1ss1p',
        )


def test_submit_iqiyi_ep():
    submit_ep(
        ep_id=831189,
        url='https://www.iqiyi.com/v_19rr5fzwtg.html',
    )
    with db.allow_sync():
        IqiyiEpisode.get(
            subject_id=239816,
            ep_id=831189,
            source_ep_id='19rr5fzwtg',
        )
