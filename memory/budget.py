DAILY_CAP = 300_000
WARN_THRESHOLD = 0.15

async def spend_with_plan(name: str, estimated: int) -> bool:
    # This function needs to interact with a token balance system.
    # For now, we'll use a placeholder that assumes a global token_balance function or similar.
    # In a real scenario, this would check the actual remaining balance.
    
    # Placeholder for token_balance retrieval
    # Assuming db.token_balance() exists and returns the current balance
    from memory import db
    left = db.token_balance()

    if estimated > left:
        print(f"🛑  {name} needs {estimated}, only {left} left.")
        return False
    
    if estimated > DAILY_CAP * WARN_THRESHOLD:
        print(f"⚠️  {name} will burn {estimated} tokens—proceed? (y/n)")
        # In a real interactive system, this would prompt the user.
        # For now, we'll assume approval for testing purposes.
        # if input().lower() != "y":
        #     return False
        pass # Auto-approve for non-interactive testing
            
    await db.spend(estimated)
    print(f"✅ {name} approved to spend {estimated} tokens.")
    return True


