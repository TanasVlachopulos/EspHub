import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(0, 10)
plt.plot(x, np.sin(x), '--', linewidth=2)
plt.plot(x, np.cos(x), '--', linewidth=2)

fig = plt.gcf()

# plotly_fig = tls.mpl_to_plotly(fig)
# plotly_fig['layout']['showlegend'] = True
#
# fig = plt.gcf()
# plot_url = py.plot_mpl(fig, filename='mpl-basic-line')

fig.savefig("testfig.png")
fig.show()

print("done")