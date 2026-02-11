types = ((id, title) for id, title in enumerate(["refill", "withdraw"], 1))

systems = ((id, title) for id, title in enumerate(["Visa", "Mastercard"], 1))

statuses = (
    (id, title) for id, title in enumerate(["In progress", "Success", "Canceled"], 1)
)
