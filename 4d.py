#!/usr/bin/env python3
import math
import pygame
from pygame import Color

def krychle(pozice, hrana):
    """
    Vytvori n-dimenzionalni krychli (rozmer je urcen podle delky `pozice`)
    """

    rozmer = len(pozice)

    # zaklad krychle (bez delky hrany a startovni pozice)
    def to_bin_tuple(cislo, rozmer):
        """
        Prevede cislo na jeho obracenou binarni reprezentaci rozlozenou
        do tuplu (3 = (1,1,0)).
        `rozmer` urcuje delku tuplu.
        """
        return tuple([ int((cislo & (2**i)) / (2**i)) for i in range(rozmer) ])
    
    ## vrcholy
    vrcholy = [ to_bin_tuple(i, rozmer) for i in range(2**rozmer) ]

    ## hrany
    def vytvor_hrany(vrcholu, start_index):
        if vrcholu == 2:
            return [(start_index, start_index+1)]
        else:
            poloviny = vytvor_hrany(vrcholu//2, start_index) + vytvor_hrany(vrcholu//2, start_index + vrcholu//2)
            spojovaci = [
                (i, i + vrcholu//2)
                for i in range(start_index, start_index + vrcholu//2)
            ]

            return poloviny + spojovaci

    #hrany = vytvor_hrany(rozmer * 2**(rozmer-1), 0)
    hrany = vytvor_hrany(2**rozmer, 0)

    # zapocitame startovni pozici a delku hrany
    return {
        'vrcholy': [
            tuple([
                vrchol[i] * hrana + pozice[i]
                for i in range(len(vrchol))
            ])
            for vrchol in vrcholy
        ],
        'hrany': hrany
    }

def transponuj(bod, transpozice):
    return tuple([
        bod[i] + transpozice[i]
        for i in range(len(bod))
    ])

def rotuj(bod, uhel, zmen):
    """
    Primitivni funkce pro rotaci kolem bodu 0.
    `uhel` je v rad.
    `zmen` je tuple dvou souradnic (indexu v `uhlu`), ktere se maji zmenit
    """
    x = bod[zmen[0]]
    y = bod[zmen[1]]
    vysledek = list(bod)

    vysledek[zmen[0]] = x * math.cos(uhel) - y * math.sin(uhel)
    vysledek[zmen[1]] = x * math.sin(uhel) + y * math.cos(uhel)

    return tuple(vysledek)
    
def rotuj_uf(bod, rotace, stred):
    """
    User-friendly rotace
    `rotace` je v setinach rad
    """
    bod = transponuj(bod, [-x for x in stred])

    i = 0
    for a in range(len(bod)):
        for b in range(i, len(bod)):
            bod = rotuj(bod, rotace[i] / 100, (a, b))
            i += 1

    bod = transponuj(bod, stred)
    return bod

def promitni(bod, f):
    """
    Promitne bod do nizsiho rozmeru (eliminuje posledni prvek tuplu)

                f
    x' = x * -------
              z + f
    """
    if bod[-1] <= 0:
        # vratime nejakou random hodnotu pro z <= 0, abychom nedelili nulou
        return bod[0:-1]

    return tuple([
        x*f / (f + bod[-1])
        for x in bod[0:-1]
    ])

def nd_promitni(bod, f):
    """
    Promitne bod z n-te dimenze do druhe
    """
    while len(bod) > 2:
        bod = promitni(bod, f)

    return bod
    


teleso = krychle((-50, -50, 50, -50), 500)

print(str(teleso))

pygame.init()
screen = pygame.display.set_mode((400,300))
clock = pygame.time.Clock()

f = 600
transpozice = [0, 0, 0, 0]
rotace = [0, 0, 0, 0, 0, 0]

def handle_transpozice(zmacknute, controls, posun):
    for i in range(len(controls)):
        if zmacknute[ord(controls[i][0])]: transpozice[i] += posun
        if zmacknute[ord(controls[i][1])]: transpozice[i] -= posun

def handle_rotace(zmacknute, controls, posun):
    for i in range(len(controls)):
        if zmacknute[ord(controls[i][0])]: rotace[i] += posun
        if zmacknute[ord(controls[i][1])]: rotace[i] -= posun


done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: done = True

    screen.fill((0, 0, 0))

    nove_body = [
        transponuj( # transpozice na souradnice v souradnem systemu pygame
            nd_promitni( # promitani
                transponuj( # transpozice polohy
                    rotuj_uf(bod, rotace, (0,0,0,0)), # rotace
                    transpozice
                ),
                f
            ),
            (screen.get_width() // 2, screen.get_height() // 2)
        )
        for bod in teleso['vrcholy']
    ]
    for hrana in teleso['hrany']:
        pygame.draw.line(screen, (255,255,255), nove_body[hrana[0]], nove_body[hrana[1]])

    # handlovani klavesoveho vstupu
    klavesy = pygame.key.get_pressed()
    if klavesy[pygame.K_LSHIFT]:
        handle_rotace(klavesy, ['ty', 'ws', 'ad', 'er', 'ui', 'op'], 5)
    else:
        handle_transpozice(klavesy, ['ad', 'ws', 're', 'yt'], 5)

    if klavesy[pygame.K_f]: f += 1
    if klavesy[pygame.K_g]: f -= 1

    pygame.display.flip()
    clock.tick(25)
