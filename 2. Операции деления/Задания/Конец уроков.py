n = int(input())
hour = 9
minute = 0
lesson_duration = 45
totalminutes = hour * 60 + minute
totalminutes += n * lesson_duration
if n > 1:
    oddbreaks = (n - 1) // 2 + (1 if n > 1 and (n - 1) % 2 == 1 else 0)
    evenbreaks = (n - 1) // 2
    totalminutes += oddbreaks * 5 + evenbreaks * 15
endhour = (totalminutes // 60) % 24
endminute = totalminutes % 60
print(endhour, endminute)