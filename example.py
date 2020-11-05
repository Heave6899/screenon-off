import sys, select

print("You have ten seconds to answer!")

i, o, e = select.select( [sys.stdin], [], [], 10 )

if (i):
  print(type(i))
  x = sys.stdin.readline().strip()
  print("You said", x)
else:
  print("You said nothing!")