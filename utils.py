def trim_history(history, max_turns=10):
    return history[-max_turns:]

def format_user(user):
    return f"{user.display_name} ({user.id})"
