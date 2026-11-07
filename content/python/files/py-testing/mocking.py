# 3.2 Testing: unittest, pytest and mocks
# Example "mocking" from the lesson.
# From the Brainy Bytes Python subject. Run it with: python3 <this file>

from unittest.mock import Mock, patch


class WeatherClient:
    def temperature(self, city):
        raise RuntimeError("this would call the internet")


def advice(client, city):
    t = client.temperature(city)
    return "take a jacket" if t < 15 else "t-shirt weather"


fake = Mock()
fake.temperature.return_value = 9              # pretend the service said 9 degrees
print(advice(fake, "Pune"))
fake.temperature.assert_called_once_with("Pune")
print(fake.temperature.call_count, fake.temperature.call_args)

fake.temperature.side_effect = [20, 3]         # a different answer on each call
print(advice(fake, "Goa"), "|", advice(fake, "Leh"))

with patch.object(WeatherClient, "temperature", return_value=30):
    print(advice(WeatherClient(), "Delhi"))    # the real class with one method replaced

flaky = Mock(side_effect=TimeoutError("no answer"))
try:
    flaky()
except TimeoutError as err:
    print("TimeoutError:", err)
