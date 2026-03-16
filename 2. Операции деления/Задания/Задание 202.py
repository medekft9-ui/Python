n = int(input())
start_minutes = 9 * 60
lesson_duration = 45
breaks = 20 * ((n - 1) // 2) + 5 * ((n - 1) % 2)
end_minutes = start_minutes + lesson_duration * n + breaks
hours = end_minutes // 60
minutes = end_minutes % 60
print(hours, minutes)