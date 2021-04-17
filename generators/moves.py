#--------------------------------------------------------------------
# linoone: moves.py
#
# Page generator for the Pokémon moves page. Lists all the
# moves.
#--------------------------------------------------------------------
from generators.base_generator import BaseGenerator


class MovesGenerator(BaseGenerator):
    def prepare_template_data(self):
        """
        Prepares any additional data the page generator needs to
        render itself. Returns a dict of variables and/or functions
        that will be exposed to the template.
        """
        levelup_move_mons = create_levelup_move_map(
            self.core_data["mon_learnsets"],
            self.core_data["national_to_species"]
        )
        tmhm_move_mons = create_tmhm_move_map(
            self.core_data["mon_tmhm_learnsets"],
            self.core_data["item_to_move"],
            self.core_data["national_to_species"]
        )
        sorted_moves = get_sorted_moves(self.core_data["move_names"])
        return {
            "levelup_move_mons": levelup_move_mons,
            "tmhm_move_mons": tmhm_move_mons,
            "sorted_moves": sorted_moves,
        }


    def generate(self, env):
        """
        Generates all of the move pages into the distribution directory.
        """
        for move in self.core_data["move_names"]:
            self.render_template(
                env,
                "move.html",
                "moves/%s.html" % move,
                extra_data={
                    'move': move,
                }
            )

        self.render_template(env, "moves.html", "moves.html")


def create_levelup_move_map(mon_learnsets, national_to_species):
    """
    Create a convenient move mapping with all the Pokémon that
    have learn each move by level up.
    """
    result = {}
    for national_num in national_to_species:
        species = national_to_species[national_num]
        for move_info in mon_learnsets[species]:
            move = move_info["move"]
            level = move_info["level"]
            if move not in result:
                result[move] = []

            result[move].append({"national_num": national_num, "level": level})

    for move in result:
        result[move] = sorted(result[move], key=lambda item: int(item["national_num"]))

    return result


def create_tmhm_move_map(mon_tmhm_learnsets, item_to_move, national_to_species):
    """
    Create a convenient move mapping with all the Pokémon that
    have learn each move by tm/hm.
    """
    result = {}
    for national_num in national_to_species:
        species = national_to_species[national_num]
        for item_id in mon_tmhm_learnsets[species]:
            move = item_to_move[item_id]
            if move not in result:
                result[move] = []

            result[move].append(national_num)

    for move in result:
        result[move] = sorted(result[move], key=int)

    return result


def get_sorted_moves(move_names):
    """
    Gets the sorted list of abilities by their names.
    """
    keys = list(move_names.keys())
    keys.sort(key = lambda ability: move_names[ability].lower())
    return keys
