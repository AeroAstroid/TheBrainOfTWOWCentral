import Config.b_star_interpreter.globals as globals

from datetime import datetime


def user_func(userItemToGet):
    useritem = userItemToGet.lower()
    match useritem:
        case "name":
            return globals.codebase.user.name
        case "id":
            return globals.codebase.user.id
        case "discriminator":
            return globals.codebase.user.discriminator
        case "avatar":
            return str(globals.codebase.user.avatar.url)
        case "created_at":
            return datetime.timestamp(globals.codebase.user.created_at)
        case "display_name":
            return globals.codebase.user.display_name
        case "color":
            return globals.codebase.user.color
        case "accent_color":
            return globals.codebase.user.accent_color
        case "":
            return [globals.codebase.user.name, globals.codebase.user.id, globals.codebase.user.discriminator,
                    str(globals.codebase.user.avatar.url), datetime.timestamp(globals.codebase.user.created_at),
                    globals.codebase.user.display_name, globals.codebase.user.color, globals.codebase.user.accent_color]
        case _:
            raise NotImplementedError("Currently, user only supports `name`, `id`, `discriminator`, `avatar`, `created_at`, `display_name`, `color`, and `accent_color`.")
