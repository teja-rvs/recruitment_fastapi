from recruitment_fastapi.models.candidate import Candidate


class SeniorCandidate(Candidate):
    __mapper_args__ = {"polymorphic_identity": "senior_candidate"}
