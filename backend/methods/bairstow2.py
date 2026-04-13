from backend.methods.bairstow import Bairstow

class Bairstow2(Bairstow):
    nombre = "Bairstow 2"
    def _calcular(self, ec, params):
        if 'r' not in params:
            params['r'] = '1'
        if 's' not in params:
            params['s'] = '-1'
        return super()._calcular(ec, params)