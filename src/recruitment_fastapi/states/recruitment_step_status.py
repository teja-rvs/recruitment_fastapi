from statemachine import State, StateMachine


class RecruitmentStepStatusMachine(StateMachine):
    initialized = State(initial=True)
    in_progress = State()
    interview_scheduled = State()
    in_review = State()

    rejected = State(final=True)
    approved = State(final=True)
    cancelled = State(final=True)

    start = initialized.to(in_progress)
    schedule_interview = in_progress.to(interview_scheduled)
    interview_complete = interview_scheduled.to(in_review)
    review = interview_scheduled.to(in_review)
    request_review = in_progress.to(in_review)
    approve = approved.from_(in_review, cond="review_provided")
    reject = rejected.from_(
        in_progress, interview_scheduled, in_review, cond="review_provided"
    )
    cancel = cancelled.from_(initialized, in_progress, interview_scheduled, in_review)

    def review_provided(self):
        return self.model.feedback is not None
