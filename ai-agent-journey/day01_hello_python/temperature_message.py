t = int(input("Temperature (°C): "))

if t >= 35:
    print("Extreme heat warning.")
elif t >= 25:
    print("Warm day.")
elif t >= 15:
    print("Mild.")
else:
    print("Cold, bring a jacket.")
if t >= 40:
    print("Dangerous heat! Stay indoors.")
elif t >= 35:
    print("Extreme heat warning.")
elif t >= 25:
    print("Warm day.")
elif t >= 15:
    print("Mild.")
elif t >= 5:
    print("Cool.")
else:
    print("Very cold, bring a heavy jacket.")
