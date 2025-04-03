import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# List of all 10 cities
cities = ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda',
          'Mohali', 'Firozpur', 'Hoshiarpur', 'Moga', 'Pathankot']

# Generate sample urgency data (0-100) for 5 zones in each city
np.random.seed(42)
data = []
for city in cities:
    for zone in ['North', 'South', 'East', 'West', 'Central']:
        # Base urgency + city-specific modifier
        urgency = np.random.randint(20,80) + {
            'Ludhiana': 15, 'Amritsar': 10, 'Jalandhar': 5,
            'Patiala': 0, 'Bathinda': -5, 'Mohali': 10,
            'Firozpur': -10, 'Hoshiarpur': 0, 'Moga': -5,
            'Pathankot': 5
        }[city]
        urgency = max(0, min(100, urgency))  # Clamp to 0-100
        data.append({'City': city, 'Zone': zone, 'Urgency': urgency})

df = pd.DataFrame(data)

# Pivot for heatmap
# Pivot for heatmap
heatmap_data = df.pivot(index="City", columns="Zone", values="Urgency") # Updated pivot() call to match current format

# Visualization
plt.figure(figsize=(12, 8))
ax = sns.heatmap(heatmap_data,
                 annot=True,
                 fmt=".0f",
                 cmap="YlOrRd",
                 cbar_kws={'label': 'Collection Urgency (0-100)'},
                 linewidths=0.5,
                 annot_kws={"size": 10})

# Enhancements
plt.title('Waste Collection Urgency Across Punjab Cities (By Zone)',
          pad=20, fontsize=14)
plt.xlabel('Zone', labelpad=10)
plt.ylabel('City', labelpad=10)
plt.xticks(rotation=45)
plt.yticks(rotation=0)

# Add priority indicators
for city_idx, city in enumerate(cities):
    max_zone = df[df['City']==city].nlargest(1, 'Urgency')['Zone'].values[0]
    ax.add_patch(plt.Rectangle((list(heatmap_data.columns).index(max_zone), city_idx),
                              1, 1, fill=False, edgecolor='blue', lw=2))

# Legend
plt.text(5.5, -1.5,
         'Urgency Guide:\n'
         '■ 0-30: Low (Weekly)\n'
         '■ 31-70: Medium (Every 3 days)\n'
         '■ 71-100: High (Daily)\n'
         'Blue boxes = Highest urgency zone per city',
         ha='center', va='center')

plt.tight_layout()
plt.show()
