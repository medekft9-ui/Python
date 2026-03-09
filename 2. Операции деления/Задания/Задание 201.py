seconds = int(input())
hours = seconds // 3600
minutes = (seconds % 3600) // 60
secs = seconds % 60
print(f'{hours}:{minutes}:{secs}')