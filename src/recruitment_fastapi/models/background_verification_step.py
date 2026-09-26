from typing import ClassVar

from recruitment_fastapi.models.hld_interview_step import HldInterviewStep
from recruitment_fastapi.models.recruitment_step import RecruitmentStep


class BackgroundVerificationStep(RecruitmentStep):
    STEP_TYPE: ClassVar = "background_verification_step"

    __mapper_args__: ClassVar = {"polymorphic_identity": STEP_TYPE}

    @classmethod
    def allowed_roles(cls):
        return ["hiring_manager"]

    @classmethod
    def prerequisite(cls):
        return [HldInterviewStep]

    def submit_feedback(self, feedback):
        self.feedback = feedback
        self.status_machine.request_review()
