import matplotlib.pyplot as plt

BLUE = '#2a78d6'    # main data colour
ORANGE = '#eb6834'  # highlight
INK = '#0b0b0b'     # titles and labels
MUTED = '#52514e'   # axes and secondary text
GRID = '#e6e5e1'


def apply_style():
    """Recessive axes and grid, so the data stands out."""
    plt.rcParams.update({
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'axes.titlecolor': INK,
        'xtick.color': MUTED, 'ytick.color': MUTED,
        'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.6, 'axes.axisbelow': True,
        'font.size': 10, 'figure.dpi': 110,
    })