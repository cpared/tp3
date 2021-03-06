from mesa import *
from mazo import *

CANT_FUNDACIONES = 4
CANT_PILAS_TABLERO = 4

class SolitarioClasico:
    """Interfaz para implementar un solitario."""

    def __init__(self, mesa):
        """Inicializa con una mesa creada y vacía."""
        self.mesa = mesa

    def armar(self):
        """Arma el tablero con la configuración inicial."""
        self.mesa.mazo = crear_mazo()
        self.mesa.descarte = PilaCartas(
            pila_visible = True,
        )
        self.mesa.descarte.apilar(self.mesa.mazo.desapilar(), forzar = True)
        self.mesa.descarte.tope().voltear()

        for i in range(CANT_FUNDACIONES):
            # Creamos 4 fundaciones, una para cada palo, no más restricciones
            self.mesa.fundaciones.append(
                PilaCartas(
                    valor_inicial = 1,
                    criterio_apilar=criterio(palo = MISMO_PALO, orden= DESCENDENTE),
                ))

        for i in range(CANT_PILAS_TABLERO):
            # Creamos 4 pilas en el tablero, sin restricciones.
            self.mesa.pilas_tablero.append(
                PilaCartas(
                    pila_visible=True,
                    criterio_mover = criterio(palo = DISTINTO_COLOR, orden = ASCENDENTE),
                    criterio_apilar = criterio(palo = DISTINTO_COLOR, orden = ASCENDENTE)
                ))

            for _ in range(4 + (1 if i < 4 else 0)):
                # Barajamos cartas en nuestra pila
                self.mesa.pilas_tablero[i].apilar(self.mesa.mazo.desapilar(), forzar = True)
            self.mesa.pilas_tablero[i].tope().voltear() # Ponemos boca arriba todas las cartas.

    def termino(self):
        """Avisa si el juego se terminó."""
        for pila in self.mesa.pilas_tablero:
            if not pila.es_vacia():
                return False
        return True

    def jugar(self, jugada):
        """Efectúa una movida.
            La jugada es una lista de pares (PILA, numero). (Ver mesa.)
            Si no puede realizarse la jugada se levanta una excepción SolitarioError *descriptiva*."""
        j0, p0 = jugada[0]
        j1, p1 = jugada[1] if len(jugada) == 2 else (SALIR, 0)

        if len(jugada) == 1 and (j0 == PILA_TABLERO or j0 == DESCARTE):
            # Sólo especificaron una pila de origen, intentamos mover a alguna fundación.
            origen = self.mesa.pilas_tablero[p0] if j0 == PILA_TABLERO else self.mesa.descarte
            for fundacion in self.mesa.fundaciones:
                try:    
                    self._carta_a_pila(origen, fundacion)
                    return
                except SolitarioError:
                    pass
            raise SolitarioError("No se puede apilar en la fundación")       

        elif len(jugada) == 1 and j0 == MAZO:
            # Muevo una carta del maso al descarte
            if self.mesa.mazo.es_vacia():
                while not self.mesa.descarte.es_vacia():
                    carta = self.mesa.descarte.desapilar()
                    carta.voltear()
                    self.mesa.mazo.apilar(carta, forzar = True)
            else:
                self.mesa.descarte.apilar(self.mesa.mazo.desapilar(), forzar = True)
                self.mesa.descarte.tope().voltear()      
        elif len(jugada) == 2 and j0 == PILA_TABLERO and j1 in (FUNDACION, PILA_TABLERO):
            # Especificaron origen y destino, intentamos mover del tablero adonde corresponda.
            destino = self.mesa.fundaciones[p1] if j1 == FUNDACION else self.mesa.pilas_tablero[p1]
            self._pila_a_pila(self.mesa.pilas_tablero[p0], destino)
        elif len(jugada) == 2 and j0 == DESCARTE and j1 in (FUNDACION, PILA_TABLERO):
            # Especificaron origen y destino, intentamos mover del descarte adonde corresponda.
            destino = self.mesa.fundaciones[p1] if j1 == FUNDACION else self.mesa.pilas_tablero[p1]
            self._carta_a_pila(self.mesa.descarte, destino)
        else:
            # No hay más jugadas válidas según nuestras reglas.
            raise SolitarioError("Movimiento inválido")

    def _carta_a_pila(self, origen, pila):
        """Mueve la carta del tope entre dos pilas, si se puede, levanta SolitarioError si no."""
        if origen.es_vacia():
            raise SolitarioError("La pila está vacía")

        # Dejamos que PilaCarta haga las validaciones :)
        pila.apilar(origen.tope())
        origen.desapilar()

        if not origen.es_vacia() and origen.tope().boca_abajo:
            origen.tope().voltear()
    
    def _pila_a_pila(self, origen, pila):
        """Mueve la carta del tope entre dos pilas, si se puede, levanta SolitarioError si no."""
        if origen.es_vacia():
            raise SolitarioError("La pila está vacía")

        # Dejamos que PilaCarta haga las validaciones :)
        pila.mover(origen)

        if not origen.es_vacia() and origen.tope().boca_abajo:
            origen.tope().voltear()