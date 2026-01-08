from core.models import Todos

class TodosService:
    def __init__(self):
        pass

    def get_all(self):
        return Todos.objects.all()
