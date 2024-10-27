DEVICE_ADDRESS = '127.0.0.1:16384'

NUMS_ADDRESS = {
    '0': (205, 1137),
}
NUMS_ADDRESS.update({
    str(_n): (103 + 177*(_n-1), 1266)
    for _n in range(1, 6)
})
NUMS_ADDRESS.update({
    str(_n): (203 + 177*(_n-6), 1394)
    for _n in range(6, 10)
})

RED_CONFIG = {
    "top_left": (181, 222+0), "bottom_right": (477, 518+0)
}
PERPLE_CONFIG = {
    "top_left": (170, 593+0), "bottom_right": (466, 886+0)
}
