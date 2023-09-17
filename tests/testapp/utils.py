EVENTS = {
    "Germany": [
        {
            "name": "Wacken Open Air",
            "city": "Wacken",
            "tickets": "www.example.com/wacken"
        },
        {
            "name": "Full Force",
            "city": "Grafenhainichen",
            "tickets": "www.example.com/full_force"
        }
    ],
    "Spain": [
        {
            "name": "Resurrection",
            "city": "Viveiro",
            "tickets": "www.example.com/resurrection"
        }
    ]
}


def get_event_list(country):
    return EVENTS[country.name]
