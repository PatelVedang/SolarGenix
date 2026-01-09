from core.models import Todo

class TodoService:
    def __init__(self):
        pass

    def get_all(self):
        return Todo.objects.all()
