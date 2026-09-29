from statemachine import State, StateMachine


class CandidateStatusMachine(StateMachine):
    in_progress = State(initial=True)
    recruited = State(final=True)
    rejected = State(final=True)

    recruit = in_progress.to(recruited)
    reject = in_progress.to(rejected)
