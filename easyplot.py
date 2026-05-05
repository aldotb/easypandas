import pandas as pd
import matplotlib.pyplot as plt
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt
import seaborn as sns
console = Console()
from easyplot import *
def familystat(df_interno, column):
    # 1. Cálculos de la "Tabla de Posiciones"
    counts = df_interno[column].value_counts().reset_index()
    counts.columns = [column, 'Qty']
    counts['Percentage'] = (counts['Qty'] / len(df_interno) * 100).round(1)
    
    # 2. Cuadro resumen elegante con RICH
    table = Table(title=f"📊 [bold magenta]{column.upper()} STAT[/bold magenta]")
    table.add_column(column, justify="left", style="cyan", no_wrap=True)
    table.add_column("Qty", justify="right", style="green")
    table.add_column("Percentage", justify="right", style="yellow")

    for _, row in counts.iterrows():
        table.add_row(str(row[column]), str(row['Qty']), f"{row['Percentage']}%")
    
    console.print(table)

    # 3. Configuración de colores dinámicos
    if column.lower() == 'color':
        color_map = {'Yellow': '#FFC300', 'Red': '#FF5733', 
                     'Green': '#28B463', 'Blue': '#3498DB'}
        colors = [color_map.get(c, '#CCCCCC') for c in counts[column]]
    else:
        # Paleta variada por defecto
        colors = plt.cm.Paired(range(len(counts)))

    # 4. Creación de Gráficos (1 fila, 2 columnas)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.5))
    
    # --- GRÁFICO DE BARRAS (Izquierda) ---
    bars = ax1.bar(counts[column], counts['Qty'], color=colors, 
                   edgecolor='black', linewidth=1.2)
    
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_ylabel('Quantity')
    ax1.set_title(f'Bar Chart: {column}', fontsize=12, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # --- GRÁFICO PIE (Derecha) ---
    ax2.pie(counts['Qty'], labels=counts[column], autopct='%1.1f%%', 
            startangle=140, colors=colors, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
    ax2.set_title(f'Distribution: {column}', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.show()

def generalplot(df):
    g = sns.PairGrid(df)
    return (g.map(sns.scatterplot))


def plotversus(df,real_x,real_y , color=None, kind='scatter'):
        """
        Grafica x vs y asegurando que los nombres de las columnas 
        sean corregidos por gfield.
        """
        # 1. Aplicamos la "magia" de gfield a todos los inputs
        real_color = color

        # 2. Configuración del estilo
        sns.set_theme(style="whitegrid")
        plt.figure(figsize=(10, 6))

        # 3. Renderizado del gráfico
        if kind == 'scatter':
            ax = sns.scatterplot(
                data=df, 
                x=real_x, 
                y=real_y, 
                hue=real_color,
                palette='viridis'
            )
        
        # 4. Etiquetas automáticas (usando los nombres reales corregidos)
        plt.title(f'Analysis: {real_x} vs {real_y}', fontsize=14)
        plt.xlabel(real_x)
        plt.ylabel(real_y)
        
        return plt.show()    