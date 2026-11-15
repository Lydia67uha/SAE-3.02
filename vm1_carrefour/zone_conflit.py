class ZoneConflit:
    """La zone au milieu du carrefour, où les véhicules se croisent."""

    def __init__(self, x_min, x_max, y_min, y_max):
        """Définit la zone par ses limites en x et en y."""
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def contient(self, vehicule):
        """Retourne True si le véhicule est dans la zone."""
        return self.x_min <= vehicule.x <= self.x_max and self.y_min <= vehicule.y <= self.y_max

    def est_libre(self, vehicules):
        """Retourne True si aucun véhicule n'est dans la zone."""
        for vehicule in vehicules:
            if self.contient(vehicule):
                return False

        return True
