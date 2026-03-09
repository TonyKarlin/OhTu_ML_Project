import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd

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
    

def clean_data(project_df):
	project_df = project_df.copy()
	areas = gpd.read_file("datasets/piirialuejako-1995-2019.gpkg", layer="osa_alue_2019")
	accidents = gpd.GeoDataFrame(
		project_df,
		geometry=gpd.points_from_xy(project_df["ita_etrs"], project_df["pohj_etrs"]),
		crs="EPSG:3879"
	)
	areas = areas.to_crs(accidents.crs)

	accidents = gpd.sjoin(
		accidents,
		areas[["Nimi", "geometry"]],
		how="left",
		predicate="within"
	)

	accidents = accidents.rename(columns={"Nimi": "Osa-alue"})
	accidents = accidents.drop(columns=["geometry", "index_right"])

	col_rename = {"LAJI": "O_Tyyppi", "pohj_etrs": "Pohj_coords", "ita_etrs": "Itä_coords","VAKAV_A": "Vakavuus", "VV": "Vuosi"}
	accidents = accidents.rename(columns=col_rename)
	accidents = accidents.iloc[:, [1, 2, 5, 0, 4, 3]]

	cols_to_categorical = ["Osa-alue", "O_Tyyppi"]
	accidents[cols_to_categorical] = accidents[cols_to_categorical].astype("category")

	cols_to_float = ["Pohj_coords", "Itä_coords"]
	accidents[cols_to_float] = accidents[cols_to_float].astype(float)

	accidents = accidents[accidents["Vuosi"] <= 2019]
	return accidents, areas


def plot_map(df):
	accidents, areas = clean_data(df)
	accidents_geo = gpd.GeoDataFrame(
		accidents,
		geometry=gpd.points_from_xy(accidents["Itä_coords"], accidents["Pohj_coords"]),
		crs="EPSG:3879"
	)

	xmin, ymin, xmax, ymax = accidents_geo.total_bounds
	margin_x = (xmax - xmin) * 0.05
	margin_y = (ymax - ymin) * 0.05

	fig, ax = plt.subplots(figsize=(12,12))

	areas.plot(ax=ax, color="lightgrey", edgecolor="black")

	accidents_geo[accidents_geo["Vakavuus"]==1].plot(
		ax=ax, markersize=0.5, color="blue", label="Omaisuusvahinko"
	)
	accidents_geo[accidents_geo["Vakavuus"]==2].plot(
		ax=ax, markersize=1, color="orange", label="Loukkaantuminen"
	)
	accidents_geo[accidents_geo["Vakavuus"]==3].plot(
		ax=ax, markersize=5, color="red", label="Kuolema"
	)

	ax.set_xlim(xmin - margin_x, xmax + margin_x)
	ax.set_ylim(ymin - margin_y, ymax + margin_y)
	ax.set_aspect("equal")

	plt.legend()
	plt.title("Liikenneonnettomuudet Helsingissä (vakavuuden mukaan)")
	plt.show()
 
def accidents_by_place(df):
	accidents, areas = clean_data(df)
	accidents_geo = gpd.GeoDataFrame(
		accidents,
		geometry=gpd.points_from_xy(accidents["Itä_coords"], accidents["Pohj_coords"]),
		crs="EPSG:3879"
	)	
	vakavuus_area = accidents_geo.groupby(["Osa-alue","Vakavuus"], observed=True).size().unstack(fill_value=0)

	for col in [1, 2, 3]:
		if col not in vakavuus_area.columns:
			vakavuus_area[col] = 0

	vakavimmat = vakavuus_area[2] + vakavuus_area[3]
	vakavimmat.name = "Vakavat"

	vakava = vakavuus_area[vakavimmat > 0].copy()
	vakava["Vakavat"] = vakavimmat[vakavimmat > 0]
	vakava = vakava.sort_values("Vakavat", ascending=False).head(10)
	vakava = vakava.rename(columns={1: "Omaisuusvahinko", 2: "Loukkaantuminen", 3: "Kuolema"})
	return vakava

def plot_accidents_by_place(df):
	vakava = accidents_by_place(df)
	vakava.plot(kind='bar', stacked=True, figsize=(10,6),
				color=['blue','orange','red'])
	plt.title("Top 10 vaarallisinta Helsingin osa-aluetta vakavuuden mukaan")
	plt.ylabel("Onnettomuuksien lukumäärä")
	plt.xlabel("Osa-alue")
	plt.xticks(rotation=45)
	plt.legend(["Omaisuusvahinko", "Loukkaantuminen", "Kuolema"])
	plt.tight_layout()
	plt.show()	