from itertools import count

from polyfactory.fields import Use

from recruitment_fastapi.models import (
    Candidate,
    EntryCandidate,
    MidCandidate,
    SeniorCandidate,
)

from .base import BaseTestFactory

_names = count(1)
_emails = count(1)
_phones = count(1)


def _candidate_name() -> str:
    return f"Candidate {next(_names)}"


def _candidate_email() -> str:
    return f"candidate{next(_emails)}@example.com"


def _candidate_phone() -> str:
    return f"+91900000{next(_phones):04d}"


def _experience() -> int:
    return CandidateFactory.__random__.randint(0, 100)


class CandidateFactory(BaseTestFactory[Candidate]):
    __model__ = Candidate

    name = Use(_candidate_name)
    email = Use(_candidate_email)
    phone = Use(_candidate_phone)
    experience = Use(_experience)


class EntryCandidateFactory(CandidateFactory):
    __model__ = EntryCandidate


class MidCandidateFactory(CandidateFactory):
    __model__ = MidCandidate


class SeniorCandidateFactory(CandidateFactory):
    __model__ = SeniorCandidate
