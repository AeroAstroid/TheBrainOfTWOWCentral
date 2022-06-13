import src.interpreter.globals as globals


def user_func(userItemToGet):
    # TODO: Replace back to match case when we fix the heroku crash on 3.10
    if userItemToGet == "name":
        return globals.codebase.user.name
    elif userItemToGet == "id":
        return globals.codebase.user.id
    elif userItemToGet == "discriminator":
        return globals.codebase.user.discriminator
    elif userItemToGet == "avatar":
        return str(globals.codebase.user.avatar_url)
    elif userItemToGet == "created_at":
        return globals.codebase.user.created_at
    elif userItemToGet == "display_name":
        return globals.codebase.user.display_name
    elif userItemToGet == "_":
        raise NotImplementedError(
            "Currently, user only supports `name`, `id`, `discriminator`, `avatar`, `created_at`, and `display_name`.")
