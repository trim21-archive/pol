from app.worker import submit_bangumi
from app.db.mysql import Session
from app.db_models import sa
from app.video_website_spider.bilibili import Bilibili


def test_init():
    Bilibili()


# def test_valid_ep_url():
#     pass

# def test_valid_subject_url():
#     pass


def test_submit_ep(db_session: Session):
    Bilibili.ep(
        ep_id=893707,
        url='https://www.bilibili.com/bangumi/play/ep276614',
    )
    db_session.query(sa.BangumiBilibili).filter_by(
        subject_id=271724,
        media_id=28221412,
        season_id=28013,
    ).one()

    db_session.query(sa.EpBilibili).filter_by(
        source_ep_id=276614,
        ep_id=893707,
        subject_id=271724,
    ).one()


def test_submit_bangumi_play_ss(db_session: Session):
    submit_bangumi(
        subject_id=278683, url='https://www.bilibili.com/bangumi/play/ss29310'
    )

    db_session.query(sa.BangumiBilibili).filter_by(
        subject_id=285776,
        media_id=28224080,
        season_id=29310,
    ).one()


def test_submit_bangumi_md(db_session: Session):
    db_session.query(sa.BangumiBilibili).filter_by(
        subject_id=262939,
        media_id=28221399,
        season_id=28002,
    ).delete()
    db_session.query(sa.EpBilibili).filter_by(subject_id=262939).delete()
    db_session.commit()
    db_session.flush()

    Bilibili.subject(
        subject_id=262939,
        url='https://www.bilibili.com/bangumi/media/md28221399/',
    )

    db_session.query(sa.BangumiBilibili).filter_by(
        subject_id=262939,
        media_id=28221399,
        season_id=28002,
    ).one()
    db_session.query(sa.EpBilibili).filter_by(
        source_ep_id=276476,
        ep_id=891210,
        subject_id=262939,
    ).one()
