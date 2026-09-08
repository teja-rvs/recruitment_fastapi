from recruitment_fastapi.models.candidate import Candidate

class MidCandidate(Candidate):
    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "mid_candidate"
    }
