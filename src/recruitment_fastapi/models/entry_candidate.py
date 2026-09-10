from recruitment_fastapi.models.candidate import Candidate


class EntryCandidate(Candidate):
    __mapper_args__ = {"polymorphic_identity": "entry_candidate"}
