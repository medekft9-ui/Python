n = int(input())
hour = 9
minute = 0
lesson_duration = 45
total_minutes = hour * 60 + minute
total_minutes += n * lesson_duration
if n > 1:
    odd_breaks = (n - 1) // 2 + (1 if n > 1 and (n - 1) % 2 == 1 else 0)
    even_breaks = (n - 1) // 2
    total_minutes += odd_breaks * 5 + even_breaks * 15
end_hour = (total_minutes // 60) % 24
end_minute = total_minutes % 60
print(end_hour, end_minute)