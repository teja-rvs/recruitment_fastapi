class BaseMachine:
    def transition(self, column, machine_class, event):
        current_value = getattr(self, column)

        machine = machine_class(start_value=current_value)

        machine.send(event)

        setattr(self, column, machine.current_state.id)
