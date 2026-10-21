class ZoneConflit:

    def __init__(self, x_min, x_max, y_min, y_max):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def contient(self, vehicule):

        return (
            self.x_min <= vehicule.x <= self.x_max
            and
            self.y_min <= vehicule.y <= self.y_max
        )

    def est_libre(self, vehicules):

        for vehicule in vehicules:

            if self.contient(vehicule):
                return False

        return True