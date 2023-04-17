from Config.b_star_interpreter.exceptions import BStarTypeCoercionFailureException, safe_cut

def j(amount):

    return "j" * max(min(amount, 250), 1)
