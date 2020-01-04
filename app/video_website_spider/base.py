import abc
import functools

from app.db.mysql import db


class UrlNotValidError(Exception):
    def __init__(self, pattern: str):
        self.pattern = pattern


class BaseWebsite(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def valid_ep_url(cls, url: str):  # pragma: no cover
        """
        valid if url if a correct episode player url

        raise UrlNotValidError(pattern) if url is not valid
        pattern is correct pattern for user to understand

        Returns
        -------
            None

        Raises
        ------
            UrlNotValidError
        """
        raise NotImplementedError(cls.__name__, 'valid_ep_url')

    @classmethod
    @abc.abstractmethod
    def valid_subject_url(cls, url: str):  # pragma: no cover
        """
        valid if url if a correct bangumi player url

        raise UrlNotValidError(pattern) if url is not valid
        pattern is correct pattern for user to understand

        Returns
        -------
            None

        Raises
        ------
            UrlNotValidError
        """
        raise NotImplementedError(cls.__name__, 'valid_subject_url')

    @classmethod
    @abc.abstractmethod
    def subject(cls, subject_id: int, url: str):  # pragma: no cover
        raise NotImplementedError(cls.__name__, 'subject')

    @classmethod
    @abc.abstractmethod
    def ep(cls, ep_id: int, url: str):  # pragma: no cover
        raise NotImplementedError(cls.__name__, 'subject')


def sync_db(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        with db.allow_sync():
            return func(*args, **kwargs)

    return wrapped
