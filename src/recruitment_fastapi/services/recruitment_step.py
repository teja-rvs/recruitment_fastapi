from fastapi import BackgroundTasks

from recruitment_fastapi.errors.invalid_state_error import InvalidStateError
from recruitment_fastapi.errors.resource_not_found_error import ResourceNotFoundError
from recruitment_fastapi.jobs.run_recruitment_process import run_recruitment_process
from recruitment_fastapi.models.recruitment_step import RecruitmentStep
from recruitment_fastapi.repositories.recruitment_step import RecruitmentStepRepository
from recruitment_fastapi.schemas.recruitment_steps import (
    AssignInterviewerSchema,
    ReviewSchema,
)


class RecruitmentStepService:
    def __init__(
        self, repository: RecruitmentStepRepository, background_tasks: BackgroundTasks
    ):
        self.repository = repository
        self.background_tasks = background_tasks

    async def find(self, id: int):
        return await self.repository.find(id)

    async def assign_interviewer(
        self,
        recruitment_step: RecruitmentStep,
        data: AssignInterviewerSchema,
    ):
        if data.interviewer_id:
            recruitment_step.interviewer_id = await self._update_interviewer(
                recruitment_step, data.interviewer_id
            )

        if data.interview_date:
            recruitment_step.interview_date = data.interview_date

        if recruitment_step.interviewer_id and recruitment_step.interview_date:
            recruitment_step.schedule_interview()

        recruitment_step = await self.repository.save(recruitment_step)

        return recruitment_step

    async def all(self):
        return await self.repository.all()

    async def _update_interviewer(
        self, recruitment_step: RecruitmentStep, interviewer_id: int
    ):
        interviewer = await self.repository.allowed_interviewer(
            interviewer_id, recruitment_step.allowed_roles()
        )

        if interviewer is None:
            raise ResourceNotFoundError("Interviewer not found")

        return interviewer_id

    async def review(self, recruitment_step: RecruitmentStep, data: ReviewSchema):
        if recruitment_step.status != "in_review":
            raise InvalidStateError("Recruitment step must be in review stage")

        recruitment_step.feedback = data.review
        return await self.repository.save(recruitment_step)

    async def approve(self, recruitment_step: RecruitmentStep):
        if recruitment_step.feedback is None:
            raise InvalidStateError("Provide feedback before approval")
        recruitment_step.approve()

        recruitment_step = await self.repository.save(recruitment_step)

        self.background_tasks.add_task(
            run_recruitment_process, recruitment_step.candidate_id
        )

        return recruitment_step

    async def reject(self, recruitment_step: RecruitmentStep):
        if recruitment_step.feedback is None:
            raise InvalidStateError("Provide feedback before rejection")

        recruitment_step.reject()
        recruitment_step = await self.repository.save(recruitment_step)
        await self._reject_candidate(recruitment_step.candidate)
        return recruitment_step

    async def _reject_candidate(self, candidate):
        candidate.reject()
        recruitment_steps = await self.repository.find_by_candidate(candidate.id)

        for step in recruitment_steps:
            if step.status not in ["approved", "rejected", "cancelled"]:
                step.cancel()

        await self.repository.save_all(candidate)

    async def interview_complete(self, step):
        step.interview_complete()

        return await self.repository.save(step)
