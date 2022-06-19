import src.interpreter.globals as globals


def user_func(userItemToGet):
    match userItemToGet:
        case "name":
            return globals.codebase.user.name
        case "id":
            return globals.codebase.user.id
        case "discriminator":
            return globals.codebase.user.discriminator
        case "avatar":
            return str(globals.codebase.user.avatar_url)
        case "created_at":
            return globals.codebase.user.created_at
        case "display_name":
            return globals.codebase.user.display_name
        case _:
            raise NotImplementedError("Currently, user only supports `name`, `id`, `discriminator`, `avatar`, `created_at`, and `display_name`.")