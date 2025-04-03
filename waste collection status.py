import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Cities in Punjab
cities = ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda',
          'Mohali', 'Firozpur', 'Hoshiarpur', 'Moga', 'Pathankot']

# Create sample data
np.random.seed(42)
data = []
for city in cities:
    for i in range(1, 6):  # 5 bins per city for simplicity
        data.append({
            'City': city,
            'Bin': f'{city}_Bin_{i}',
            'Type': np.random.choice(['General', 'Recycle', 'Hazard']),
            'Fill %': np.random.randint(0, 101),
            'Last Collected': (datetime.now() - timedelta(days=np.random.randint(0, 8))).strftime('%Y-%m-%d'),
            'Status': '⚠️ Urgent' if np.random.random() > 0.7 else '✅ Normal'
        })

# Create DataFrame
df = pd.DataFrame(data)

# Display the table
print("Punjab Waste Collection Status")
print("="*40)
display(df.style.highlight_max(subset=['Fill %'], color='orange')
             .highlight_min(subset=['Fill %'], color='lightgreen')
             .set_properties(**{'text-align': 'left'}))
