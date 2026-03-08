import matplotlib.pyplot as plt
import numpy as np

def plot_accidents_by_year(df):
    filters = [
        (None, "Kaikki onnettomuudet"),
        ("JK", "Jalankulkijat (JK)"),
        ("PP", "Polkupyörät (PP)"),
        ("MP", "Mopo/Moottoripyörät (MP)"),
        ("MA", "Moottoriajoneuvot (MA)"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    axes = axes.ravel()

    for i, (laji, title) in enumerate(filters):
        data = df if laji is None else df[df['LAJI'] == laji]
        counts = data.groupby('VV').size().reset_index(name='count')

        x = counts['VV']
        y = counts['count']

        axes[i].plot(x, y, marker='o', label=title)
        m, b = np.polyfit(x, y, 1)
        axes[i].plot(x, m * x + b, linestyle='--')
        axes[i].set_title(title)
        axes[i].set_xlabel("Vuosi")
        axes[i].set_ylabel("Onnettomuuksien määrä")
        axes[i].grid(True, alpha=0.3)

    axes[5].set_visible(False)
    plt.tight_layout()
    plt.show()



def plot_seriousness_by_year(df):
    colors = {1: 'steelblue', 2: 'orange', 3: 'tomato'}
    labels = {1: 'Omaisuusvahinko', 2: 'Loukkaantuminen', 3: '!!KUOLEMA!!'}

    counts = df.groupby(['VV', 'VAKAV_A']).size().unstack(fill_value=0)

    fig, axes = plt.subplots(1, 3, figsize=(12, 6))

    fig.suptitle("Onnettomuuksien vakavuus vuosittain", fontsize=14, fontweight='bold', y=1.02)
    for i, sev in enumerate([1, 2, 3]):
        x = counts.index
        y = counts[sev]

        axes[i].plot(x, y, marker='o', color=colors[sev], label=labels[sev])

        m, b = np.polyfit(x, y, 1)
        axes[i].plot(x, m * x + b, linestyle='--', color=colors[sev], alpha=0.5, label="Trendi")

        axes[i].set_title(labels[sev])
        axes[i].set_xlabel("Vuosi")
        axes[i].set_ylabel("Onnettomuuksien määrä")
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()