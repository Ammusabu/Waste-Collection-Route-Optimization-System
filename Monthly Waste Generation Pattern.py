import matplotlib.pyplot as plt

# Sample data
status_counts = {
    'Empty (0-20%)': 125,
    'Half-Full (20-70%)': 342,
    'Critical (70-90%)': 89,
    'Overflowing (>90%)': 47
}

# Visualization
plt.figure(figsize=(8, 6))
colors = ['#2ecc71', '#f39c12', '#e74c3c', '#c0392b']
explode = (0, 0, 0.1, 0.2)

plt.pie(status_counts.values(),
        labels=status_counts.keys(),
        colors=colors,
        explode=explode,
        autopct='%1.1f%%',
        startangle=90,
        shadow=True)
plt.title('Current Bin Status Distribution in Ludhiana')
plt.axis('equal')
plt.show()
# Generate sample data
dates = pd.date_range('2024-01-01', periods=12, freq='M')
residential = [1200, 1150, 1300, 1250, 1400, 1550,
               1650, 1600, 1450, 1350, 1250, 1400]
commercial = [800, 820, 950, 900, 1000, 1100,
              1050, 1150, 1200, 1100, 950, 1000]

fig, ax1 = plt.subplots(figsize=(10,6))

color = 'tab:blue'
ax1.set_xlabel('Month (2024)')
ax1.set_ylabel('Residential Waste (kg)', color=color)
ax1.plot(dates, residential, color=color, marker='o')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Commercial Waste (kg)', color=color)
ax2.plot(dates, commercial, color=color, marker='s')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Monthly Waste Generation Patterns')
fig.tight_layout()
plt.show()

