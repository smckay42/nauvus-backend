class DefaultDatabaseRouter:
    """
    A router to not control database operations on models in the
    searchdb application.
    """

    def db_for_read(self, model, **hints):
        return "default"
        # if model._meta.app_label == "loads":
        #     return "search"
        # else:
        #     return "default"

    def db_for_write(self, model, **hints):
        return "default"
        # if model._meta.app_label == "loads":
        #     return "search"
        # else:
        #     return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True
        # if obj1._meta.app_label == "loads" or obj2._meta.app_label == "loads":
        #     return None
        # else:
        #     return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
        # if app_label == "loads":
        #     return db == "search"
        # else:
        #     return db == "default"
        # return None
