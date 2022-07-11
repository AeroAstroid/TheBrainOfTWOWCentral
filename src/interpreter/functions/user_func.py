import src.interpreter.globals as globals

from datetime import datetime



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
            return datetime.timestamp(globals.codebase.user.created_at)
        case "display_name" | "nickname" | "nick":
            return globals.codebase.user.display_name
        case "display_avatar":
            return globals.codebase.user.display_avatar
        case "accent_color":
            if globals.codebase.user.accent_color is not None:
                return str(globals.codebase.user.accent_color)
            else:
                raise ValueError("This user doesn't have an accent color.")
        case "banner":
            if globals.codebase.user.banner is not None:
                return str(globals.codebase.user.banner)
            else:
                raise ValueError("This user doesn't have a banner.")
        case _:
            raise NotImplementedError("Currently, user supports `name`, `id`, `discriminator`, `avatar`, `created_at`, `display_name`, `display_avatar`, `accent_color`, and `banner`.")
