import random
import time

class Commander:
    def __init__(self):
        self.credits = 100
        self.fuel = 100
        self.cargo_hold = {}
        self.max_cargo = 5
        self.location = "Lave"

def generate_galaxy():
    # Simple procedural generation of star systems and commodity prices
    systems = {
        "Lave": {"tech": "Agricultural", "prices": {"Food": 10, "Machinery": 50, "Minerals": 20}},
        "Zaonce": {"tech": "Industrial", "prices": {"Food": 25, "Machinery": 30, "Minerals": 15}},
        "Diso": {"tech": "Rich Agricultural", "prices": {"Food": 8, "Machinery": 60, "Minerals": 25}},
        "Leesti": {"tech": "Hi-Tech", "prices": {"Food": 30, "Machinery": 20, "Minerals": 40}}
    }
    return systems

def play_space_game():
    player = Commander()
    universe = generate_galaxy()
    
    print("=== TERMINAL ELITE PROTOTYPE ===")
    print("Welcome, Commander. Your goal is to trade, survive, and explore the galaxy.")
    
    while True:
        print(f"\n--- Location: {player.location} ({universe[player.location]['tech']}) ---")
        print(f"Credits: {player.credits} CR | Fuel: {player.fuel}% | Cargo: {player.cargo_hold}")
        print("\nWhat would you like to do?")
        print("1) Trade commodities")
        print("2) Jump to another system")
        print("3) Scan space for anomalies")
        print("4) Exit game")
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            current_prices = universe[player.location]["prices"]
            print("\nMarket Prices:")
            for item, price in current_prices.items():
                print(f"- {item}: {price} CR")
            
            action = input("Do you want to (B)uy or (S)ell? ").strip().lower()
            if action == 'b':
                item_choice = input("Enter item name to buy: ").capitalize()
                if item_choice in current_prices:
                    cost = current_prices[item_choice]
                    total_cargo = sum(player.cargo_hold.values())
                    if player.credits >= cost and total_cargo < player.max_cargo:
                        player.credits -= cost
                        player.cargo_hold[item_choice] = player.cargo_hold.get(item_choice, 0) + 1
                        print(f"Purchased 1 {item_choice}!")
                    else:
                        print("Not enough credits or cargo space full!")
                else:
                    print("Invalid item.")
            elif action == 's':
                item_choice = input("Enter item name to sell: ").capitalize()
                if item_choice in player.cargo_hold and player.cargo_hold[item_choice] > 0:
                    revenue = current_prices.get(item_choice, 10)
                    player.credits += revenue
                    player.cargo_hold[item_choice] -= 1
                    if player.cargo_hold[item_choice] == 0:
                        del player.cargo_hold[item_choice]
                    print(f"Sold 1 {item_choice} for {revenue} CR!")
                else:
                    print("You don't have that item to sell.")
                    
        elif choice == "2":
            print("\nAvailable Destinations:")
            destinations = [s for s in universe.keys() if s != player.location]
            for idx, dest in enumerate(destinations, 1):
                print(f"{idx}) {dest}")
            
            dest_choice = input("Choose destination number: ").strip()
            if dest_choice.isdigit():
                idx = int(dest_choice) - 1
                if 0 <= idx < len(destinations):
                    if player.fuel >= 25:
                        player.fuel -= 25
                        player.location = destinations[idx]
                        print(f"Hyperspace jump complete. Welcome to {player.location}!")
                        
                        # Random encounter chance during travel
                        if random.random() < 0.4:
                            print("\nWARNING: Pirate vessel intercepted your flight path!")
                            if "Machinery" in player.cargo_hold:
                                print("They demand a bribe of 1 Machinery unit or credits!")
                                choice_pirate = input("Fight or Bribe? (f/b): ").lower()
                                if choice_pirate == 'b':
                                    del player.cargo_hold["Machinery"]
                                    print("You dropped the cargo. They let you go.")
                                else:
                                    print("You narrowly escaped, but lost 10 credits in the scuffle!")
                                    player.credits = max(0, player.credits - 10)
                            else:
                                print("Your cargo hold was empty. They got bored and warped away.")
                    else:
                        print("Not enough fuel to jump! (Refuel mechanic coming soon)")
                else:
                    print("Invalid destination selection.")
                    
        elif choice == "3":
            print("\nScanning deep space...")
            time.sleep(1)
            event = random.choice([
                "You found a drifting asteroid rich in minerals! +15 Credits.",
                "Quiet sector. Nothing of interest found.",
                "You picked up a strange radio signal from an abandoned satellite."
            ])
            print(event)
            if "mineral" in event.lower():
                player.credits += 15
                
        elif choice == "4":
            print("Saving flight logs... Goodbye, Commander.")
            break
        else:
            print("Invalid choice, try again.")

if __name__ == "__main__":
    play_space_game()
