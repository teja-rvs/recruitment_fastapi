class RecruitmentProcessService:
    def __init__(
        self,
        candidate_id: int,
        candidate_repository,
    ):
        self.candidate_id = candidate_id
        self.candidate_repository = candidate_repository

    async def run(self) -> None:
        candidate = await self._get_candidate()

        if candidate is None:
            return

        candidate_steps = candidate.recruitment_steps

        all_steps_approved = all(step.status == "approved" for step in candidate_steps)

        if all_steps_approved:
            candidate.recruit()
        else:
            for stage in candidate.STAGES:
                if self._stage_complete(stage, candidate_steps):
                    continue

                self._start_stage(stage, candidate_steps)
                break

        await self.candidate_repository.save(candidate)

    async def _get_candidate(self):
        return await self.candidate_repository.find_with_current_recruitment_steps(
            self.candidate_id
        )

    def _stage_complete(self, stage, candidate_steps) -> bool:
        if stage is None:
            return True

        return all(
            (
                step := self._find_step(
                    step_definition.STEP_TYPE,
                    candidate_steps,
                )
            )
            and step.status == "approved"
            for step_definition in stage.steps
        )

    def _start_stage(self, stage, candidate_steps) -> None:
        for step_definition in stage.steps:
            step = self._find_step(
                step_definition.STEP_TYPE,
                candidate_steps,
            )

            if step is not None:
                step.start()

    @staticmethod
    def _find_step(step_type, candidate_steps):
        return next(
            (step for step in candidate_steps if step.type == step_type),
            None,
        )
